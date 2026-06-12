import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DB_PATH = "D:/Claude_code/liangke_historical/historical_final.db"

st.set_page_config(page_title="融资数据看板", layout="wide")
st.title("💰 量子科技融资数据看板")

# 加载数据
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    # 总文章数
    total = pd.read_sql("SELECT COUNT(*) as cnt FROM articles WHERE tags LIKE '%融资%'", conn)
    # 文章类型分布
    type_dist = pd.read_sql(
        "SELECT article_type, COUNT(*) as cnt FROM articles WHERE tags LIKE '%融资%' GROUP BY article_type", conn
    )
    # 月度趋势
    monthly = pd.read_sql(
        "SELECT substr(liangke_date, 1, 7) as month, COUNT(*) as cnt "
        "FROM articles WHERE tags LIKE '%融资%' AND liangke_date IS NOT NULL "
        "GROUP BY month ORDER BY month", conn
    )
    conn.close()
    return total, type_dist, monthly

total_df, type_df, monthly_df = load_data()

# ---- 指标卡片 ----
total_count = total_df["cnt"].iloc[0]
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""
        <div style="background:#1a1a2e;padding:20px;border-radius:12px;text-align:center;
                    border:1px solid #e94560;">
            <p style="color:#aaa;font-size:14px;margin:0;">📄 融资相关文章总数</p>
            <p style="color:#e94560;font-size:42px;font-weight:700;margin:5px 0;">{total_count}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""
        <div style="background:#1a1a2e;padding:20px;border-radius:12px;text-align:center;
                    border:1px solid #0f3460;">
            <p style="color:#aaa;font-size:14px;margin:0;">📊 文章类型</p>
            <p style="color:#53d8fb;font-size:42px;font-weight:700;margin:5px 0;">{len(type_df)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""
        <div style="background:#1a1a2e;padding:20px;border-radius:12px;text-align:center;
                    border:1px solid #0f3460;">
            <p style="color:#aaa;font-size:14px;margin:0;">📆 覆盖月份数</p>
            <p style="color:#53d8fb;font-size:42px;font-weight:700;margin:5px 0;">{len(monthly_df)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---- 图表 ----
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 文章类型分布")
    fig_pie = px.pie(
        type_df,
        names="article_type",
        values="cnt",
        color_discrete_sequence=px.colors.sequential.RdBu_r,
        hole=0.4,
    )
    fig_pie.update_traces(
        textposition="outside",
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}",
    )
    fig_pie.update_layout(
        height=380,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc"),
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("📈 月度发布趋势")
    monthly_df["month"] = pd.to_datetime(monthly_df["month"])
    fig_line = px.line(
        monthly_df,
        x="month",
        y="cnt",
        markers=True,
        color_discrete_sequence=["#e94560"],
    )
    fig_line.update_traces(
        line=dict(width=2.5),
        marker=dict(size=5),
        hovertemplate="<b>%{x|%Y-%m}</b><br>文章数: %{y}",
    )
    fig_line.update_layout(
        height=380,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc"),
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#333",
            tickformat="%Y-%m",
        ),
        yaxis=dict(title="文章数", showgrid=True, gridcolor="#333"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ---- 数据表 ----
st.subheader("📋 融资相关文章列表")
conn = sqlite3.connect(DB_PATH)
articles_df = pd.read_sql(
    "SELECT liangke_date, title, article_type FROM articles "
    "WHERE tags LIKE '%融资%' ORDER BY liangke_date DESC LIMIT 50", conn
)
conn.close()
articles_df.columns = ["日期", "标题", "类型"]
st.dataframe(articles_df, use_container_width=True, hide_index=True)
