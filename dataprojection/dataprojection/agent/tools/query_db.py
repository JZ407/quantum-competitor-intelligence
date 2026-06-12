"""query_database tool executor."""
import json
from dataprojection.datasources.bridge import get_liangke_historical


# In MVP, we only have one data source. In Phase 2, this becomes a registry lookup.
_SOURCES = {
    "liangke_historical": get_liangke_historical,
}


def execute_query_database(tool_input: dict) -> dict:
    """Execute a read-only SQL query on a registered data source.

    Args:
        tool_input: {"db_name": str, "sql_query": str}

    Returns:
        {"columns": [...], "rows": [[...], ...], "row_count": int,
         "truncated": bool, "max_rows": int}
        or {"error": str}
    """
    db_name = tool_input.get("db_name", "")
    sql_query = tool_input.get("sql_query", "").strip()

    if not db_name:
        return {"error": "db_name is required"}
    if not sql_query:
        return {"error": "sql_query is required"}

    if db_name not in _SOURCES:
        return {
            "error": f"Unknown data source: '{db_name}'. "
                     f"Available sources: {list(_SOURCES.keys())}"
        }

    try:
        ds = _SOURCES[db_name]()
    except Exception as e:
        return {"error": f"Failed to connect to '{db_name}': {e}"}

    try:
        result = ds.execute_query(sql_query)
    except ValueError as e:
        return {"error": f"SQL rejected: {e}"}

    # If result has many rows, summarize
    if result.get("row_count", 0) > 0:
        # Add a note for the AI about the result format
        result["_note"] = (
            f"查询返回 {result['row_count']} 行数据。"
            + (" 结果已截断。" if result.get("truncated") else "")
            + " 请用通俗语言向用户解释这些数据，并根据数据特征建议合适的可视化方式。"
        )

    return result
