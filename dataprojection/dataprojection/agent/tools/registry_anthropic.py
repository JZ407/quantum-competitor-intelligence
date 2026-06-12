"""Tool definitions in Anthropic Claude format."""

import json
from dataprojection.agent.tools.query_db import execute_query_database
from dataprojection.agent.tools.schema import execute_get_schema
from dataprojection.agent.tools.chart import execute_generate_chart


TOOLS_ANTHROPIC = [
    {
        "name": "get_database_schema",
        "description": "获取指定数据源的完整表结构（表名、字段名、类型、示例值）。写 SQL 前先用此工具了解字段。",
        "input_schema": {
            "type": "object",
            "properties": {
                "db_name": {
                    "type": "string",
                    "description": "数据源名称，如 'liangke_historical'"
                },
            },
            "required": ["db_name"],
        },
    },
    {
        "name": "query_database",
        "description": "执行只读 SELECT 查询。仅允许 SELECT，最多返回 200 行。请包含 LIMIT。",
        "input_schema": {
            "type": "object",
            "properties": {
                "db_name": {
                    "type": "string",
                    "description": "数据源名称"
                },
                "sql_query": {
                    "type": "string",
                    "description": "SQL SELECT 语句，请始终包含 LIMIT"
                },
            },
            "required": ["db_name", "sql_query"],
        },
    },
    {
        "name": "generate_chart",
        "description": "根据查询结果生成 Altair 交互图表。x_field/y_field 必须与数据列名精确匹配。支持 bar/line/scatter/area/pie。",
        "input_schema": {
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
                    "description": "X 轴列名（必须与 query_database 返回的 columns 中某个名称完全一致）"
                },
                "y_field": {
                    "type": "string",
                    "description": "Y 轴列名（必须与 query_database 返回的 columns 中某个名称完全一致）"
                },
                "x_type": {
                    "type": "string",
                    "enum": ["quantitative", "temporal", "nominal", "ordinal"],
                    "description": "X 轴数据类型"
                },
                "y_type": {
                    "type": "string",
                    "enum": ["quantitative", "temporal", "nominal", "ordinal"],
                    "description": "Y 轴数据类型"
                },
                "color_field": {
                    "type": "string",
                    "description": "颜色分组列名（可选）"
                },
                "data_json": {
                    "type": "string",
                    "description": "JSON: {\"columns\": [...], \"rows\": [[...], ...]}，直接从 query_database 结果复制"
                },
                "width": {"type": "integer", "description": "宽度，默认 600"},
                "height": {"type": "integer", "description": "高度，默认 400"},
            },
            "required": ["chart_type", "title", "x_field", "y_field", "data_json"],
        },
    },
    {
        "name": "save_dashboard",
        "description": "将当前对话中的图表保存为仪表盘。用户说「保存」「存下来」时调用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "仪表盘标题"},
                "description": {"type": "string", "description": "简介（可选）"},
                "charts": {
                    "type": "array",
                    "description": "图表列表。如不传则自动使用本轮生成的所有图表。",
                    "items": {"type": "object"},
                },
            },
            "required": ["title"],
        },
    },
]

_EXECUTORS = {
    "query_database": execute_query_database,
    "get_database_schema": execute_get_schema,
    "generate_chart": execute_generate_chart,
    "save_dashboard": lambda inp: json.dumps(
        {"status": "saved", "message": "仪表盘已保存。",
         "charts_count": len(inp.get("charts", [])),
         "title": inp.get("title", "")},
        ensure_ascii=False),
}


def get_tools() -> list[dict]:
    return TOOLS_ANTHROPIC


def execute_tool(name: str, inp: dict) -> str:
    if name not in _EXECUTORS:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = _EXECUTORS[name](inp)
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
