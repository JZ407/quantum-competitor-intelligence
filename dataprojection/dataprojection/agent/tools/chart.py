"""generate_chart tool — re-executes SQL instead of trusting AI data parsing."""
import json
import altair as alt
import pandas as pd
from dataprojection.datasources.bridge import get_liangke_historical


_SOURCES = {"liangke_historical": get_liangke_historical}


def execute_generate_chart(tool_input: dict) -> dict:
    """Generate a chart by re-executing a SQL query and building an Altair spec.

    Args:
        chart_type, title, x_field, y_field, x_type, y_type,
        sql_query: the SQL to re-execute (from previous query_database call),
        db_name: data source name,
        color_field (optional), width, height
    """
    chart_type = tool_input.get("chart_type", "bar")
    title = tool_input.get("title", "Chart")
    x_field = tool_input.get("x_field", "")
    y_field = tool_input.get("y_field", "")
    x_type = tool_input.get("x_type", "nominal")
    y_type = tool_input.get("y_type", "quantitative")
    color_field = tool_input.get("color_field", "")
    sql_query = tool_input.get("sql_query", "")
    db_name = tool_input.get("db_name", "liangke_historical")
    data_json_str = tool_input.get("data_json", "")  # fallback
    width = tool_input.get("width", 600)
    height = tool_input.get("height", 400)

    if not x_field or not y_field:
        return {"error": "x_field and y_field are required"}

    # ── Get data: prefer re-executing SQL, fallback to data_json ──
    if sql_query and db_name in _SOURCES:
        try:
            ds = _SOURCES[db_name]()
            query_result = ds.execute_query(sql_query)
            if query_result.get("error"):
                return {"error": f"SQL query failed: {query_result['error']}"}
        except Exception as e:
            return {"error": f"Query execution failed: {e}"}
    elif data_json_str:
        try:
            query_result = json.loads(data_json_str)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid data_json: {e}"}
    else:
        return {"error": "Either sql_query or data_json is required"}

    columns = query_result.get("columns", [])
    rows = query_result.get("rows", [])

    if not columns or not rows:
        return {"error": f"Query returned no data. columns={columns}, rows_count={len(rows)}"}

    # ── Validate fields ──
    if x_field not in columns:
        return {
            "error": f"x_field '{x_field}' not found in columns: {columns}. "
                     f"Please use the exact column name from the query."
        }
    if y_field not in columns:
        return {
            "error": f"y_field '{y_field}' not found in columns: {columns}. "
                     f"Please use the exact column name from the query."
        }
    if color_field and color_field not in columns:
        return {"error": f"color_field '{color_field}' not found in columns: {columns}"}

    # ── Build records ──
    records = []
    for row in rows:
        record = {}
        for i, col_name in enumerate(columns):
            val = row[i] if i < len(row) else None
            if y_type == "quantitative" and col_name == y_field:
                try:
                    val = float(val) if val is not None else 0.0
                except (ValueError, TypeError):
                    val = 0.0
            elif x_type == "quantitative" and col_name == x_field:
                try:
                    val = float(val) if val is not None else 0.0
                except (ValueError, TypeError):
                    pass
            record[col_name] = val
        records.append(record)

    if not records:
        return {"error": "No valid data after processing"}

    # ── DataFrame ──
    df = pd.DataFrame(records)
    if y_type == "quantitative" and y_field in df.columns:
        df[y_field] = pd.to_numeric(df[y_field], errors="coerce").fillna(0)

    # ── Build chart ──
    try:
        # X encoding
        if x_type == "temporal":
            x_enc = alt.X(x_field, type="temporal",
                          axis=alt.Axis(format="%Y-%m-%d", labelAngle=-45,
                                        labelLimit=200))
        elif x_type == "quantitative":
            x_enc = alt.X(x_field, type="quantitative")
        elif x_type == "ordinal":
            x_enc = alt.X(x_field, type="ordinal",
                          axis=alt.Axis(labelAngle=-45, labelLimit=200))
        else:
            x_enc = alt.X(x_field, type="nominal",
                          axis=alt.Axis(labelAngle=-45, labelLimit=200))

        # Y encoding
        if y_type == "quantitative":
            y_enc = alt.Y(y_field, type="quantitative")
        else:
            y_enc = alt.Y(y_field, type="nominal")

        enc = {"x": x_enc, "y": y_enc}
        tooltip_cols = [x_field, y_field]
        if color_field and color_field in df.columns:
            enc["color"] = alt.Color(color_field, legend=alt.Legend(title=color_field))
            tooltip_cols.append(color_field)
        enc["tooltip"] = tooltip_cols

        # Chart mark
        if chart_type == "bar":
            chart = alt.Chart(df).mark_bar().encode(**enc)
        elif chart_type == "line":
            chart = alt.Chart(df).mark_line(point=True).encode(**enc)
        elif chart_type == "scatter":
            chart = alt.Chart(df).mark_circle(size=60).encode(**enc)
        elif chart_type == "area":
            chart = alt.Chart(df).mark_area(opacity=0.3).encode(**enc)
        elif chart_type == "pie":
            chart = (
                alt.Chart(df).mark_arc(innerRadius=50)
                .encode(
                    theta=alt.Theta(y_field, type="quantitative"),
                    color=alt.Color(x_field, type="nominal",
                                    legend=alt.Legend(title=x_field)),
                    tooltip=tooltip_cols,
                )
            )
        else:
            chart = alt.Chart(df).mark_bar().encode(**enc)

        chart = chart.properties(
            title=alt.TitleParams(title, fontSize=16),
            width=width, height=height,
        ).interactive()

        chart_spec = chart.to_dict()

        return {
            "chart_spec": chart_spec,
            "chart_type": "altair",
            "message": (
                f"Success: {chart_type} chart '{title}' "
                f"({len(records)} points, x={x_field}({x_type}), y={y_field}({y_type}))"
            ),
        }

    except Exception as e:
        return {"error": f"Chart generation failed: {e}"}
