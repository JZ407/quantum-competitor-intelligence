"""Canvas state — thread-safe bridge between AI tools and Streamlit UI."""

# Module-level canvas config that AI tools modify and Streamlit renders.
# Structure:
# {
#     "title": "My Dashboard",
#     "columns": 2,
#     "components": [
#         {"id": "c1", "type": "chart", "title": "...", "row": 0, "col": 0,
#          "config": {"chart_type": "line", "sql_query": "...", ...}},
#         ...
#     ]
# }

_canvas = {
    "title": "",
    "columns": 2,
    "components": [],
}


def get_canvas() -> dict:
    """Get current canvas config."""
    return dict(_canvas)


def set_canvas(config: dict):
    """Replace entire canvas config."""
    global _canvas
    _canvas = dict(config)


def apply_operations(operations: list[dict]) -> dict:
    """Apply a list of operations to the canvas.

    Returns {"status": "ok", "canvas": current_state, "changes_made": [...]}
    """
    changes = []
    for op in operations:
        action = op.get("action", "")
        try:
            if action == "add":
                comp = op.get("component", {})
                if comp:
                    _canvas["components"].append(comp)
                    changes.append(f"Added {comp.get('type','?')} '{comp.get('title','?')}'")
            elif action == "update":
                cid = op.get("id", "")
                changes_data = op.get("changes", {})
                for comp in _canvas["components"]:
                    if comp.get("id") == cid:
                        if "config" in changes_data:
                            comp["config"].update(changes_data["config"])
                        for k, v in changes_data.items():
                            if k != "config":
                                comp[k] = v
                        changes.append(f"Updated component '{cid}'")
                        break
            elif action == "remove":
                cid = op.get("id", "")
                _canvas["components"] = [
                    c for c in _canvas["components"] if c.get("id") != cid
                ]
                changes.append(f"Removed '{cid}'")
            elif action == "set_title":
                _canvas["title"] = op.get("title", "")
                changes.append(f"Set title to '{_canvas['title']}'")
            elif action == "set_columns":
                _canvas["columns"] = op.get("columns", 2)
                changes.append(f"Set columns to {_canvas['columns']}")
        except Exception as e:
            changes.append(f"Error with action '{action}': {e}")

    return {
        "status": "ok",
        "component_count": len(_canvas["components"]),
        "title": _canvas["title"],
        "columns": _canvas["columns"],
        "components": [
            {"id": c["id"], "type": c["type"], "title": c.get("title", ""),
             "row": c.get("row", 0), "col": c.get("col", 0)}
            for c in _canvas["components"]
        ],
        "changes_made": changes,
    }


def reset_canvas():
    """Reset canvas to empty state."""
    global _canvas
    _canvas = {"title": "", "columns": 2, "components": []}
