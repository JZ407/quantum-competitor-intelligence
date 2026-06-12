"""Canvas Renderer — renders UI components from a declarative canvas config."""

import json
import streamlit as st
import altair as alt
import pandas as pd

from dataprojection.datasources.bridge import get_liangke_historical

_SOURCES = {"liangke_historical": get_liangke_historical}


def render_canvas(config: dict):
    """Render all components from a canvas configuration.

    config = {
        "title": "My Dashboard",
        "columns": 2,
        "components": [
            {
                "id": "c1", "type": "chart", "title": "...",
                "row": 0, "col": 0, "width": 1, "height": 1,
                "config": { chart_type, sql_query, db_name, x_field, y_field, ... }
            },
            {
                "id": "c2", "type": "metric", "title": "...",
                "row": 0, "col": 1,
                "config": { sql_query, db_name, format }
            },
            {
                "id": "c3", "type": "table", "title": "...",
                "row": 1, "col": 0, "width": 2,
                "config": { sql_query, db_name, page_size }
            },
            {
                "id": "c4", "type": "text", "title": "...",
                "row": 2, "col": 0, "width": 2,
                "config": { content }
            },
        ]
    }

    Renders a responsive grid of components.
    """
    if not config or not config.get("components"):
        st.info("画布是空的。在下方对话中说「帮我设计一个融资数据看板」开始吧。")
        return

    components = config.get("components", [])
    cols = config.get("columns", 2)
    title = config.get("title", "")

    if title:
        st.header(title)

    # Organize by row
    row_map = {}
    for comp in components:
        row = comp.get("row", 0)
        if row not in row_map:
            row_map[row] = []
        row_map[row].append(comp)

    for row_idx in sorted(row_map.keys()):
        row_comps = sorted(row_map[row_idx], key=lambda c: c.get("col", 0))

        # Simple layout: one row = one set of columns
        num_cols = min(cols, len(row_comps))
        if num_cols == 0:
            continue
        st_cols = st.columns(num_cols)

        for i, comp in enumerate(row_comps):
            col_idx = i % num_cols
            with st_cols[col_idx]:
                _render_component(comp)


def _render_component(comp: dict):
    """Render a single component based on its type."""
    ctype = comp.get("type", "chart")
    cid = comp.get("id", "?")
    ctitle = comp.get("title", "")
    cfg = comp.get("config", {})

    if ctitle:
        st.subheader(ctitle)

    try:
        if ctype == "chart":
            _render_chart_component(cfg)
        elif ctype == "metric":
            _render_metric_component(cfg)
        elif ctype == "table":
            _render_table_component(cfg)
        elif ctype == "text":
            _render_text_component(cfg)
        else:
            st.caption(f"未知组件类型: {ctype}")
    except Exception as e:
        st.error(f"组件渲染失败 ({cid}): {e}")


def _get_data(cfg: dict) -> dict:
    """Execute SQL and return query result."""
    sql = cfg.get("sql_query", "")
    db_name = cfg.get("db_name", "liangke_historical")

    if not sql:
        return {"columns": [], "rows": [], "error": "No sql_query"}

    if db_name not in _SOURCES:
        return {"columns": [], "rows": [], "error": f"Unknown source: {db_name}"}

    try:
        ds = _SOURCES[db_name]()
        return ds.execute_query(sql)
    except Exception as e:
        return {"columns": [], "rows": [], "error": str(e)}


def _build_dataframe(result: dict) -> pd.DataFrame:
    """Convert query result to DataFrame."""
    columns = result.get("columns", [])
    rows = result.get("rows", [])
    if not columns or not rows:
        return pd.DataFrame()
    records = []
    for row in rows:
        record = {}
        for i, col_name in enumerate(columns):
            val = row[i] if i < len(row) else None
            record[col_name] = val
        records.append(record)
    return pd.DataFrame(records)


def _render_chart_component(cfg: dict):
    """Render a chart with live SQL execution."""
    chart_type = cfg.get("chart_type", "bar")
    x_field = cfg.get("x_field", "")
    y_field = cfg.get("y_field", "")
    x_type = cfg.get("x_type", "nominal")
    y_type = cfg.get("y_type", "quantitative")
    color_field = cfg.get("color_field", "")
    width = cfg.get("width", 400)
    height = cfg.get("height", 300)

    result = _get_data(cfg)
    if result.get("error"):
        st.caption(f"查询失败: {result['error']}")
        return

    df = _build_dataframe(result)
    if df.empty:
        st.caption("无数据")
        return

    # Type coercion
    if y_type == "quantitative" and y_field in df.columns:
        df[y_field] = pd.to_numeric(df[y_field], errors="coerce").fillna(0)
    if x_type == "quantitative" and x_field in df.columns:
        df[x_field] = pd.to_numeric(df[x_field], errors="coerce").fillna(0)

    # X encoding
    if x_type == "temporal":
        x_enc = alt.X(x_field, type="temporal",
                      axis=alt.Axis(format="%Y-%m-%d", labelAngle=-45))
    elif x_type == "quantitative":
        x_enc = alt.X(x_field, type="quantitative")
    else:
        x_enc = alt.X(x_field, type="nominal",
                      axis=alt.Axis(labelAngle=-45, labelLimit=200))

    # Y encoding
    if y_type == "quantitative":
        y_enc = alt.Y(y_field, type="quantitative")
    else:
        y_enc = alt.Y(y_field, type="nominal")

    enc = {"x": x_enc, "y": y_enc}

    tooltip_fields = [x_field, y_field]
    if color_field and color_field in df.columns:
        enc["color"] = alt.Color(color_field, legend=alt.Legend(title=color_field))
        tooltip_fields.append(color_field)
    enc["tooltip"] = tooltip_fields

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
                color=alt.Color(x_field, type="nominal"),
                tooltip=tooltip_fields,
            )
        )
    else:
        chart = alt.Chart(df).mark_bar().encode(**enc)

    chart = chart.properties(width=width, height=height).interactive()
    st.altair_chart(chart, use_container_width=True)

    # Show row count
    st.caption(f"{len(df)} 行" + (" (已截断)" if result.get("truncated") else ""))


def _render_metric_component(cfg: dict):
    """Render a big number metric card."""
    result = _get_data(cfg)
    if result.get("error"):
        st.caption(f"查询失败: {result['error']}")
        return

    rows = result.get("rows", [])
    if not rows:
        st.caption("无数据")
        return

    value = rows[0][0] if rows[0] else "—"
    fmt = cfg.get("format", "number")

    # Format
    try:
        if fmt == "number":
            value = f"{int(float(value)):,}" if value else "0"
        elif fmt == "currency":
            value = f"¥{float(value):,.0f}" if value else "¥0"
        elif fmt == "percent":
            value = f"{float(value) * 100:.1f}%" if value else "0%"
    except (ValueError, TypeError):
        value = str(value)

    st.markdown(f"## {value}")
    subtitle = cfg.get("subtitle", "")
    if subtitle:
        st.caption(subtitle)


def _render_table_component(cfg: dict):
    """Render a data table."""
    result = _get_data(cfg)
    if result.get("error"):
        st.caption(f"查询失败: {result['error']}")
        return

    df = _build_dataframe(result)
    if df.empty:
        st.caption("无数据")
        return

    page_size = cfg.get("page_size", 10)
    st.dataframe(df, use_container_width=True, height=min(page_size * 35 + 38, 400))
    st.caption(f"共 {len(df)} 行" + (" (已截断)" if result.get("truncated") else ""))


def _render_text_component(cfg: dict):
    """Render a markdown text block."""
    content = cfg.get("content", "")
    st.markdown(content)
