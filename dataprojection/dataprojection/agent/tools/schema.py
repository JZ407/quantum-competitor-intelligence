"""get_database_schema tool executor."""
from dataprojection.datasources.bridge import get_liangke_historical


_SOURCES = {
    "liangke_historical": get_liangke_historical,
}


def execute_get_schema(tool_input: dict) -> dict:
    """Get the full schema of a registered data source.

    Args:
        tool_input: {"db_name": str}

    Returns:
        {"db_name": str, "tables": [{"table_name": str, "row_count": int,
         "columns": [{"name": str, "type": str, "samples": [...]}]}]}
        or {"error": str}
    """
    db_name = tool_input.get("db_name", "")

    if not db_name:
        return {"error": "db_name is required"}

    if db_name not in _SOURCES:
        return {
            "error": f"Unknown data source: '{db_name}'. "
                     f"Available: {list(_SOURCES.keys())}"
        }

    try:
        ds = _SOURCES[db_name]()
        tables = ds.get_schema()
    except Exception as e:
        return {"error": f"Failed to read schema for '{db_name}': {e}"}

    return {
        "db_name": db_name,
        "description": ds.description,
        "tables": tables,
    }
