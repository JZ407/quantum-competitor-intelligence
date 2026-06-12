"""Tool definitions in OpenAI function-calling format for DeepSeek API."""

import json
from dataprojection.agent.tools.query_db import execute_query_database
from dataprojection.agent.tools.schema import execute_get_schema
from dataprojection.agent.tools.chart import execute_generate_chart
from dataprojection.canvas.state import get_canvas, apply_operations
from dataprojection.workspace.context import get_context
from dataprojection.workspace.manager import (
    read_file, write_file, list_files, start_app, stop_app, get_app_status,
    register_app,
)


# ── Tool definitions (OpenAI function-calling format) ──

TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "get_database_schema",
            "description": "获取指定数据源的完整表结构，包括表名、字段名、数据类型、行数和示例值。在写 SQL 查询之前应先使用此工具了解数据结构。",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_name": {
                        "type": "string",
                        "description": "数据源名称，例如 'liangke_historical'"
                    },
                },
                "required": ["db_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "对已注册的数据源执行只读 SQL SELECT 查询。使用前请先通过 get_database_schema 了解表结构。仅支持 SELECT 语句，最多返回 200 行。请在 SQL 中包含 LIMIT。",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_name": {
                        "type": "string",
                        "description": "数据源名称，如 'liangke_historical'"
                    },
                    "sql_query": {
                        "type": "string",
                        "description": "SQL SELECT 查询语句，仅允许 SELECT。请始终包含 LIMIT 子句。"
                    },
                },
                "required": ["db_name", "sql_query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_chart",
            "description": "生成图表。传入 sql_query（从 query_database 复制）和字段名即可。x_field/y_field 必须与 SQL 查询结果的列名完全一致。优先传 sql_query 而非 data_json。",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": ["bar", "line", "scatter", "area", "pie"],
                        "description": "图表类型"
                    },
                    "title": {
                        "type": "string",
                        "description": "图表标题"
                    },
                    "x_field": {
                        "type": "string",
                        "description": "X 轴的数据列名"
                    },
                    "y_field": {
                        "type": "string",
                        "description": "Y 轴的数据列名"
                    },
                    "x_type": {
                        "type": "string",
                        "enum": ["quantitative", "temporal", "nominal", "ordinal"],
                        "description": "X 轴数据类型: quantitative(数值)、temporal(时间)、nominal(分类)、ordinal(有序分类)"
                    },
                    "y_type": {
                        "type": "string",
                        "enum": ["quantitative", "temporal", "nominal", "ordinal"],
                        "description": "Y 轴数据类型"
                    },
                    "color_field": {
                        "type": "string",
                        "description": "用于颜色分组的列名（可选）"
                    },
                    "sql_query": {
                        "type": "string",
                        "description": "重新执行此 SQL 来获取图表数据（推荐，比传 data_json 更可靠）"
                    },
                    "db_name": {
                        "type": "string",
                        "description": "数据源名称，默认 'liangke_historical'"
                    },
                    "data_json": {
                        "type": "string",
                        "description": "JSON 格式数据（备选）。优先使用 sql_query 传 SQL"
                    },
                    "width": {"type": "integer", "description": "图表宽度（像素），默认 600"},
                    "height": {"type": "integer", "description": "图表高度（像素），默认 400"},
                },
                "required": ["chart_type", "title", "x_field", "y_field"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_dashboard",
            "description": "保存当前对话中生成的图表为仪表盘。用户说「保存」「存下来」等时调用。将已有的图表组合成一个仪表盘配置。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "仪表盘标题"
                    },
                    "description": {
                        "type": "string",
                        "description": "仪表盘简介（可选）"
                    },
                    "charts": {
                        "type": "array",
                        "description": "要保存的图表列表。每个图表包含 chart_spec、chart_type、title。如无图表则传空数组。",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "chart_type": {"type": "string"},
                                "chart_spec": {"type": "object"},
                            },
                        },
                    },
                },
                "required": ["title", "charts"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_interface",
            "description": "修改画布上的 UI 组件。可以添加/修改/删除组件、设置标题和列数。一次调用可执行多个操作。",
            "parameters": {
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "description": "操作列表。每个操作: add添加组件, update修改组件, remove删除组件, set_title设置标题, set_columns设置列数",
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["add", "update", "remove", "set_title", "set_columns"]},
                                "id": {"type": "string", "description": "组件ID (update/remove 需要)"},
                                "component": {"type": "object", "description": "组件定义 (add 需要)"},
                                "changes": {"type": "object", "description": "要修改的字段 (update 需要)"},
                                "title": {"type": "string", "description": "画布标题 (set_title 需要)"},
                                "columns": {"type": "integer", "description": "列数 (set_columns 需要)"},
                            },
                        },
                    },
                },
                "required": ["operations"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_canvas_state",
            "description": "获取画布当前状态（所有组件列表）。在修改画布之前先看看上面有什么。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "在用户的 app 工作目录中创建或覆盖一个文件。自动创建父目录。用于写 Python 代码、HTML、CSS、requirements.txt 等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径，相对于 app 根目录，如 'app.py' 或 'pages/data.py'"},
                    "content": {"type": "string", "description": "文件的完整内容"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取用户 app 工作目录中的文件。用于查看已有代码后做修改。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径，相对于 app 根目录"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出用户 app 工作目录中的文件和子目录。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "子目录（可选），默认列出根目录"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_app",
            "description": "启动用户的 Streamlit 应用。先确保 app.py 已写好、依赖已安装再调用。用户可以在浏览器中查看结果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "description": "端口号（可选），默认使用注册的端口"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "stop_app",
            "description": "停止用户的 Streamlit 应用。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_app_status",
            "description": "检查用户应用是否正在运行，返回运行状态和 URL。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


# ── Executor mapping ──

def _ctx():
    """Get current workspace context."""
    c = get_context()
    return c["username"], c["app_slug"]


_EXECUTORS = {
    "query_database": execute_query_database,
    "get_database_schema": execute_get_schema,
    "generate_chart": execute_generate_chart,

    # Workspace file tools
    "create_file": lambda inp: json.dumps(
        write_file(*_ctx(), inp.get("path", ""), inp.get("content", "")),
        ensure_ascii=False),
    "read_file": lambda inp: json.dumps(
        read_file(*_ctx(), inp.get("path", "")),
        ensure_ascii=False),
    "list_files": lambda inp: json.dumps(
        list_files(*_ctx(), inp.get("path", "")),
        ensure_ascii=False),

    # App lifecycle
    "start_app": lambda inp: json.dumps(
        start_app(*_ctx(), inp.get("port")),
        ensure_ascii=False),
    "stop_app": lambda inp: json.dumps(
        stop_app(*_ctx()),
        ensure_ascii=False),
    "get_app_status": lambda inp: json.dumps(
        get_app_status(*_ctx()),
        ensure_ascii=False),

    # Canvas tools (legacy)
    "edit_interface": lambda inp: json.dumps(
        apply_operations(inp.get("operations", [])),
        ensure_ascii=False),
    "get_canvas_state": lambda inp: json.dumps(get_canvas(), ensure_ascii=False),
    "save_dashboard": lambda inp: json.dumps(
        {"status": "saved", "message": "仪表盘配置已接收。",
         "charts": len(inp.get("charts", [])),
         "title": inp.get("title", "")},
        ensure_ascii=False),
}


def get_tool_definitions() -> list[dict]:
    """Get all tool definitions in OpenAI function-calling format."""
    return TOOLS_OPENAI


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a JSON string."""
    if tool_name not in _EXECUTORS:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    try:
        result = _EXECUTORS[tool_name](tool_input)
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
