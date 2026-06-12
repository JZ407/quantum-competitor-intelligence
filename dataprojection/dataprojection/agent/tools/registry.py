"""Tool definitions for Claude API — tool schemas and executors."""

import json
from typing import Any

# ── Tool JSON Schemas (for Claude API `tools` parameter) ──

TOOL_QUERY_DATABASE = {
    "name": "query_database",
    "description": "对已注册的数据源执行只读 SQL SELECT 查询。"
                   "使用前请先用 get_database_schema 了解表结构和字段名。"
                   "查询限制：只允许 SELECT 语句，返回最多 200 行。",
    "input_schema": {
        "type": "object",
        "properties": {
            "db_name": {
                "type": "string",
                "description": "数据源名称，例如 'liangke_historical'"
            },
            "sql_query": {
                "type": "string",
                "description": "SQL SELECT 查询语句。仅支持 SELECT。"
                               "请始终包含 LIMIT 子句。"
            },
        },
        "required": ["db_name", "sql_query"],
    },
}

TOOL_GET_SCHEMA = {
    "name": "get_database_schema",
    "description": "获取指定数据源的完整表结构，包括表名、字段名、"
                   "数据类型、示例值。在写 SQL 之前使用此工具了解数据结构。",
    "input_schema": {
        "type": "object",
        "properties": {
            "db_name": {
                "type": "string",
                "description": "数据源名称，例如 'liangke_historical'"
            },
        },
        "required": ["db_name"],
    },
}

TOOL_GENERATE_CHART = {
    "name": "generate_chart",
    "description": "根据数据生成 Altair (Vega-Lite) 交互式图表。"
                   "支持 bar、line、scatter、area、pie、heatmap 等类型。"
                   "用于将查询结果可视化展示。",
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
                "description": "X 轴对应的数据列名"
            },
            "y_field": {
                "type": "string",
                "description": "Y 轴对应的数据列名"
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
                "description": "用于颜色分组的列名（可选）"
            },
            "data_json": {
                "type": "string",
                "description": "JSON 格式的数据: "
                               "{\"columns\": [...], \"rows\": [[...], ...]}"
            },
            "width": {
                "type": "integer",
                "description": "图表宽度（像素），默认 600"
            },
            "height": {
                "type": "integer",
                "description": "图表高度（像素），默认 400"
            },
        },
        "required": ["chart_type", "title", "x_field", "y_field", "data_json"],
    },
}


# ── Tool Registry ──

class ToolRegistry:
    """Maps tool names to their schemas and executor functions."""

    def __init__(self):
        self._tools: dict[str, dict] = {}

    def register(self, schema: dict, executor: callable):
        self._tools[schema["name"]] = {
            "schema": schema,
            "executor": executor,
        }

    def get_schemas(self) -> list[dict]:
        """Get all tool schemas for Claude API `tools` parameter."""
        return [t["schema"] for t in self._tools.values()]

    def execute(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool and return the result as a JSON string."""
        if tool_name not in self._tools:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        try:
            result = self._tools[tool_name]["executor"](tool_input)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def has(self, tool_name: str) -> bool:
        return tool_name in self._tools
