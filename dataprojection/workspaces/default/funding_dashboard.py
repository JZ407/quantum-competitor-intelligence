"""
量子科技投融资数据看板 — Streamlit 应用
从 liangke_historical 数据库提取融资文章，统计月度趋势和地区分布
"""
import streamlit as st
import pandas as pd
import sqlite3
import re
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ═══ Page config ═══
st.set_page_config(
    page_title="量子科技投融资看板",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══ 数据库路径 ═══
import os
DB_PATH = r"D:\Claude_code\liangke_historical\historical_final.db"

if not os.path.exists(DB_PATH):
    st.error(f"❌ 历史库不存在: {DB_PATH}")
    st.stop()


# ═══ 金额提取 ═══
def extract_amount(text: str) -> float | None:
    """从文本中提取投融资金额，返回「万元人民币」为单位的数值。

    支持格式：
    - X.X亿美元 / X.X亿人民币 / X.X亿元
    - X.X万元 / X.X万人民币
    - X.X百万美元 / X.X千万美元
    - $X.X million / $X.X billion
    - ¥X.X亿 / ¥X.X万

    使用美元汇率 1 USD ≈ 7.2 CNY
    """
    if not text or not isinstance(text, str):
        return None

    text = text.replace(",", "").replace("，", "")

    patterns = [
        # 亿美元 → 万人民币 (1亿USD = 72000万CNY)
        (r'(\d+\.?\d*)\s*亿美元', lambda x: float(x) * 72000),
        # 亿美金
        (r'(\d+\.?\d*)\s*亿美[金元]', lambda x: float(x) * 72000),
        # 亿人民币 / 亿元
        (r'(\d+\.?\d*)\s*亿[元人]?民?币?', lambda x: float(x) * 10000),
        (r'(\d+\.?\d*)\s*亿元', lambda x: float(x) * 10000),
        # 千万美元 → 万人民币 (1千万USD = 7200万CNY)
        (r'(\d+\.?\d*)\s*千万美元', lambda x: float(x) * 7200),
        (r'(\d+\.?\d*)\s*千万美[金元]', lambda x: float(x) * 7200),
        # 百万美元 → 万人民币 (1百万USD = 720万CNY)
        (r'(\d+\.?\d*)\s*百万美元', lambda x: float(x) * 720),
        (r'(\d+\.?\d*)\s*百万美[金元]', lambda x: float(x) * 720),
        # 万元 / 万人民币
        (r'(\d+\.?\d*)\s*万[元人]?民?币?', lambda x: float(x)),
        # $X billion → 万人民币
        (r'\$\s*(\d+\.?\d*)\s*[Bb]illion', lambda x: float(x) * 72000),
        # $X million → 万人民币
        (r'\$\s*(\d+\.?\d*)\s*[Mm]illion', lambda x: float(x) * 720),
        # ¥X亿
        (r'¥\s*(\d+\.?\d*)\s*亿', lambda x: float(x) * 10000),
        # ¥X万
        (r'¥\s*(\d+\.?\d*)\s*万', lambda x: float(x)),
        # 数亿 / 近亿 → 估算为 1亿 = 10000万
        (r'[数近]亿[美]?[元金]?', lambda x: 10000),
        # 数千万 → 估算为 3000万
        (r'[数近]千万[美]?[元金]?', lambda x: 3000),
        # 数百万 → 估算为 500万
        (r'[数近]百万[美]?[元金]?', lambda x: 500),
    ]

    amounts = []
    for pattern, converter in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            try:
                val = converter(m) if callable(converter) else float(m) if isinstance(m, str) else converter
                amounts.append(val)
            except (ValueError, TypeError):
                pass

    if not amounts:
        return None

    # 去重：相近金额合并（容差 ±5%），取最大值
    amounts = sorted(set(amounts), reverse=True)
    deduped = []
    for a in amounts:
        if not deduped or all(abs(a - d) / max(a, d) > 0.05 for d in deduped):
            deduped.append(a)
        else:
            # 保留更大的那个
            for i, d in enumerate(deduped):
                if abs(a - d) / max(a, d) <= 0.05 and a > d:
                    deduped[i] = a

    return max(deduped)  # 返回最大金额


def extract_amount_from_row(row) -> float | None:
    """从一行数据中提取金额，优先 title 后 content"""
    title = row.get("title", "") or ""
    content = row.get("content", "") or ""

    # 先从标题提取（更精确）
    title_amount = extract_amount(str(title))
    if title_amount is not None:
        return title_amount

    # 从正文提取
    content_amount = extract_amount(str(content))
    return content_amount


# ═══ 数据加载 ═══
# 每日库 MySQL 连接
MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "scraper",
    "password": "scraper123",
    "database": "liangke_scraper",
    "charset": "utf8mb4",
}

# 国内量子企业（用于 area 推断）
CHINESE_COMPANIES = {
    '本源量子', '量旋科技', '相干科技', '逻辑比特', '矩量光启', '武汉超磁科技',
    '玻色量子', '图灵量子', '正则量子', '奇算光启', '华翊量子', '幺正量子',
    '中科酷原', '无量量子', '太一量生', '两仪万象', '无问清芯', '不筹量子', '原子矩阵',
    '国仪量子', '国测量子', '未磁科技', '频准激光', '国光量子',
    '国盾量子', '国科量子', '微观纪元', '量坤科技', '瀚海量子', '隧穿智元',
    '知冷低温', '量羲技术', '森一量子', '硅臻量子', '天芯量子', '矩阵时光',
    '太微量子', '伏曦量子',
}


def _derive_area(row) -> str:
    """从 tags/title/content 推断地区"""
    tags = row.get("tags")
    title = str(row.get("title", ""))

    # 1. 从 funding.company 判断
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            tags = {}
    if isinstance(tags, dict):
        company = (tags.get("funding", {}) or {}).get("company", "")
        if company in CHINESE_COMPANIES:
            return "中国"
        if company and any('一' <= c <= '鿿' for c in company):
            return "中国"

    # 2. 标题关键词
    cn_kw = ['合肥', '北京', '上海', '深圳', '武汉', '成都', '杭州', '南京', '济南', '广州',
             '厦门', '湖州', '本源', '国盾', '国仪', '图灵', '玻色', '华翊', '幺正', '量旋',
             '正则', '奇算', '相干', '逻辑', '矩量', '中科酷原', '太一', '无问清芯', '不筹',
             '国测量子', '国光', '未磁', '频准激光', '知冷低温', '量羲', '微观纪元', '瀚海',
             '硅臻', '森一', '量坤', '隧穿', '太微', '伏曦', '天芯', '矩阵时光',
             '湖北', '四川', '安徽']
    if any(kw in title for kw in cn_kw):
        return "中国"

    # 3. 海外关键词
    overseas_kw = ['美国', '英国', '法国', '德国', '加拿大', '芬兰', '以色列', '日本',
                   '韩国', '荷兰', '瑞士', '瑞典', '澳大利亚', '欧盟', '欧洲']
    for kw in overseas_kw:
        if kw in title:
            return kw if kw != '欧盟' else '欧洲'

    return "海外"


@st.cache_data(ttl=300)
def load_funding_data():
    """加载所有融资相关文章 — 每日库(MySQL) + 历史库(SQLite)"""
    dfs = []

    # ── 1. 每日库: MySQL (量科网抓取 + websearch) ──
    try:
        from sqlalchemy import create_engine
        mysql_engine = create_engine(
            'mysql+pymysql://scraper:scraper123@127.0.0.1:3306/liangke_scraper?charset=utf8mb4'
        )
        df_mysql = pd.read_sql(
            """
            SELECT id, title, content, liangke_date as published_at,
                   page_type as article_type, tags, source_domain, liangke_url
            FROM articles
            WHERE liangke_date IS NOT NULL
              AND (
                tags LIKE '%%融资%%'
                OR tags LIKE '%%资本运作%%'
                OR tags LIKE '%%国内投融资%%'
              )
            ORDER BY liangke_date DESC
            """,
            mysql_engine,
        )
        mysql_engine.dispose()

        if not df_mysql.empty:
            # 解析 JSON tags
            def parse_tags(t):
                if isinstance(t, str):
                    try: return json.loads(t)
                    except: return {}
                return t if isinstance(t, dict) else {}
            df_mysql["tags_parsed"] = df_mysql["tags"].apply(parse_tags)

            # 添加缺失列
            df_mysql["area"] = df_mysql.apply(_derive_area, axis=1)
            df_mysql["category"] = ""
            df_mysql["id"] = df_mysql["id"].astype(str)  # 避免与 SQLite id 冲突

            dfs.append(df_mysql)
    except Exception as e:
        st.warning(f"⚠️ MySQL（每日库）连接失败: {e}")

    # ── 2. 历史库: SQLite (v2+v3 合并) ──
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info('articles')")
    columns = [row[1] for row in cursor.fetchall()]

    if "published_at" in columns:
        date_col = "published_at"
    elif "liangke_date" in columns:
        date_col = "liangke_date"
    else:
        date_col = None

    if date_col is not None:
        df_sqlite = pd.read_sql(
            f"""
            SELECT CAST(id AS TEXT) as id, title, content,
                   COALESCE(area, '') as area,
                   {date_col} as published_at,
                   article_type, tags,
                   COALESCE(category, '') as category,
                   COALESCE(source_domain, '') as source_domain,
                   liangke_url
            FROM articles
            WHERE tags LIKE '%融资%' AND {date_col} IS NOT NULL
            ORDER BY {date_col} DESC
            """,
            conn,
        )
        dfs.append(df_sqlite)
    conn.close()

    # ── 合并 ──
    if not dfs:
        return pd.DataFrame(), "empty", []

    df = pd.concat(dfs, ignore_index=True)

    # 去重（按 title + published_at）
    df = df.drop_duplicates(subset=["title", "published_at"], keep="first")

    if df.empty:
        return df, "empty", columns if 'columns' in dir() else []

    # 解析日期
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    df = df.dropna(subset=["published_at"])

    # 标准化 area
    df["area_clean"] = df["area"].apply(_normalize_area)

    # 提取金额
    df["amount"] = df.apply(extract_amount_from_row, axis=1)

    # 月度
    df["month"] = df["published_at"].dt.to_period("M")

    return df, "ok", columns if 'columns' in dir() else []


def _normalize_area(area):
    """标准化地区名称"""
    if not area or not isinstance(area, str):
        return "未知"
    area = area.strip()
    # 合并同义地区
    mapping = {
        "中国大陆": "中国",
        "中国内地": "中国",
        "中国台湾": "台湾",
        "北美": "美国",
        "北美地区": "美国",
        "欧洲地区": "欧洲",
        "欧盟": "欧洲",
    }
    return mapping.get(area, area)


# ═══ 加载 ═══
with st.spinner("📡 正在加载投融资数据..."):
    df, status, columns = load_funding_data()

if status == "no_date_column":
    st.error(f"❌ 数据库中未找到日期列（published_at / liangke_date）。可用列: {columns}")
    st.stop()

if status == "empty" or df.empty:
    st.warning("⚠️ 未找到带「融资」标签的文章数据。")
    st.stop()

# 分离有金额和无金额的数据
has_amount = df["amount"].notna()
df_with_amount = df[has_amount].copy()
df_without_amount = df[~has_amount].copy()

st.sidebar.title("💰 量子科技投融资看板")
st.sidebar.caption(f"数据库: `{DB_PATH}`")
st.sidebar.metric("融资文章总数", len(df))
st.sidebar.metric("已提取金额文章", len(df_with_amount))
if len(df_without_amount) > 0:
    st.sidebar.metric("未提取金额文章", len(df_without_amount))

if df_with_amount.empty:
    st.warning("⚠️ 未能从任何文章中提取到投融资金额。请检查数据格式或手动补充金额信息。")
    st.stop()

# ═══ 月度统计 ═══
monthly = (
    df_with_amount.groupby("month")
    .agg(
        total_amount=("amount", "sum"),
        deal_count=("amount", "count"),
    )
    .reset_index()
)
monthly["month"] = monthly["month"].dt.to_timestamp()
monthly["total_amount_yi"] = monthly["total_amount"] / 10000  # 万元 → 亿元

# 全部文章月度笔数（含无金额的）
monthly_all = (
    df.groupby("month")
    .agg(deal_count_all=("id", "count"))
    .reset_index()
)
monthly_all["month"] = monthly_all["month"].dt.to_timestamp()

# ═══ 地区统计 ═══
area_stats = (
    df_with_amount.groupby("area_clean")
    .agg(
        total_amount=("amount", "sum"),
        deal_count=("amount", "count"),
    )
    .reset_index()
    .sort_values("total_amount", ascending=False)
)
area_stats["amount_pct"] = (
    area_stats["total_amount"] / area_stats["total_amount"].sum() * 100
)
area_stats["count_pct"] = (
    area_stats["deal_count"] / area_stats["deal_count"].sum() * 100
)

# ═══ 标题 ═══
st.title("💰 量子科技投融资数据看板")
st.caption(f"数据来源: liangke_historical · 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ═══ KPI 指标卡 ═══
total_amount_yi = monthly["total_amount"].sum() / 10000  # 亿人民币
total_deals = len(df_with_amount)
total_months = len(monthly)
total_areas = len(area_stats)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:24px;border-radius:16px;
                    text-align:center;border:1px solid #e94560;">
            <p style="color:#aaa;font-size:14px;margin:0;">💰 投融资总额</p>
            <p style="color:#e94560;font-size:36px;font-weight:800;margin:8px 0;">
                ¥{total_amount_yi:,.1f}亿
            </p>
            <p style="color:#666;font-size:12px;margin:0;">约 {total_amount_yi/7.2:.1f} 亿美元</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi2:
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:24px;border-radius:16px;
                    text-align:center;border:1px solid #0f3460;">
            <p style="color:#aaa;font-size:14px;margin:0;">📊 投融资笔数</p>
            <p style="color:#53d8fb;font-size:36px;font-weight:800;margin:8px 0;">
                {total_deals} 笔
            </p>
            <p style="color:#666;font-size:12px;margin:0;">含金额标签的文章</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi3:
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:24px;border-radius:16px;
                    text-align:center;border:1px solid #0f3460;">
            <p style="color:#aaa;font-size:14px;margin:0;">📅 覆盖月份</p>
            <p style="color:#53d8fb;font-size:36px;font-weight:800;margin:8px 0;">
                {total_months} 个月
            </p>
            <p style="color:#666;font-size:12px;margin:0;">
                {monthly['month'].min().strftime('%Y-%m')} ~ {monthly['month'].max().strftime('%Y-%m')}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi4:
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:24px;border-radius:16px;
                    text-align:center;border:1px solid #0f3460;">
            <p style="color:#aaa;font-size:14px;margin:0;">🌍 覆盖地区</p>
            <p style="color:#53d8fb;font-size:36px;font-weight:800;margin:8px 0;">
                {total_areas} 个
            </p>
            <p style="color:#666;font-size:12px;margin:0;">Top: {area_stats.iloc[0]['area_clean']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ═══ Tab 布局 ═══
tab1, tab2, tab3 = st.tabs(["📈 月度趋势", "🌍 地区分布", "📋 明细数据"])

# ── Tab 1: 月度趋势 ──
with tab1:
    st.subheader("📈 月度投融资趋势")

    # 双轴图：柱状=笔数，折线=总额
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 柱状图：每月笔数
    fig.add_trace(
        go.Bar(
            x=monthly["month"],
            y=monthly["deal_count"],
            name="融资笔数",
            marker_color="#53d8fb",
            hovertemplate="<b>%{x|%Y-%m}</b><br>笔数: %{y}<extra></extra>",
        ),
        secondary_y=False,
    )

    # 折线图：每月总额
    fig.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["total_amount_yi"],
            name="投融资总额（亿元）",
            mode="lines+markers",
            line=dict(color="#e94560", width=3),
            marker=dict(size=8, color="#e94560"),
            hovertemplate="<b>%{x|%Y-%m}</b><br>总额: ¥%{y:.2f}亿<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        hovermode="x unified",
        height=480,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc"),
        legend=dict(orientation="h", y=1.12, x=0),
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#333",
            tickformat="%Y-%m",
        ),
        yaxis=dict(
            title="融资笔数",
            showgrid=True,
            gridcolor="#333",
            color="#53d8fb",
        ),
        yaxis2=dict(
            title="总额（亿元 CNY）",
            showgrid=False,
            color="#e94560",
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 补充：月均统计
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("月均投融资总额", f"¥{monthly['total_amount_yi'].mean():.2f}亿")
        st.metric("月均投融资笔数", f"{monthly['deal_count'].mean():.1f}笔")
    with col_b:
        peak_month = monthly.loc[monthly["total_amount"].idxmax()]
        st.metric(
            "最高单月总额",
            f"¥{peak_month['total_amount_yi']:.2f}亿",
            delta=peak_month["month"].strftime("%Y-%m"),
        )
        peak_count_month = monthly.loc[monthly["deal_count"].idxmax()]
        st.metric(
            "最高单月笔数",
            f"{int(peak_count_month['deal_count'])}笔",
            delta=peak_count_month["month"].strftime("%Y-%m"),
        )

# ── Tab 2: 地区分布 ──
with tab2:
    st.subheader("🌍 地区分布")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 投融资总额占比")
        if len(area_stats) > 1:
            fig_pie_amount = px.pie(
                area_stats,
                names="area_clean",
                values="total_amount",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.45,
            )
            fig_pie_amount.update_traces(
                textposition="outside",
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>总额: ¥%{value:,.0f}万<br>占比: %{percent}",
            )
            fig_pie_amount.update_layout(
                height=420,
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ccc"),
                legend=dict(orientation="h", y=-0.15),
            )
            st.plotly_chart(fig_pie_amount, use_container_width=True)
        else:
            st.info("数据不足，无法绘制饼图")

    with col_right:
        st.markdown("#### 投融资笔数占比")
        if len(area_stats) > 1:
            fig_pie_count = px.pie(
                area_stats,
                names="area_clean",
                values="deal_count",
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.45,
            )
            fig_pie_count.update_traces(
                textposition="outside",
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>笔数: %{value}<br>占比: %{percent}",
            )
            fig_pie_count.update_layout(
                height=420,
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ccc"),
                legend=dict(orientation="h", y=-0.15),
            )
            st.plotly_chart(fig_pie_count, use_container_width=True)
        else:
            st.info("数据不足，无法绘制饼图")

    # 地区表格
    st.divider()
    st.markdown("#### 地区统计明细")
    display_area = area_stats.copy()
    display_area["total_amount"] = display_area["total_amount"].apply(
        lambda x: f"¥{x/10000:.2f}亿"
    )
    display_area["amount_pct"] = display_area["amount_pct"].apply(lambda x: f"{x:.1f}%")
    display_area["count_pct"] = display_area["count_pct"].apply(lambda x: f"{x:.1f}%")
    display_area.columns = ["地区", "投融资总额", "笔数", "总额占比", "笔数占比"]
    st.dataframe(
        display_area,
        use_container_width=True,
        hide_index=True,
        column_config={
            "地区": st.column_config.TextColumn(width="medium"),
            "投融资总额": st.column_config.TextColumn(width="medium"),
            "笔数": st.column_config.NumberColumn(width="small"),
            "总额占比": st.column_config.TextColumn(width="small"),
            "笔数占比": st.column_config.TextColumn(width="small"),
        },
    )

# ── Tab 3: 明细数据 ──
with tab3:
    st.subheader("📋 投融资文章明细")

    # 筛选控件
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        area_filter = st.multiselect(
            "地区筛选",
            options=sorted(df["area_clean"].unique()),
            default=[],
        )
    with col_f2:
        has_amount_filter = st.selectbox(
            "金额状态",
            options=["全部", "已提取金额", "未提取金额"],
            index=0,
        )
    with col_f3:
        search_title = st.text_input("标题搜索", placeholder="输入关键词...")

    # 应用筛选
    detail_df = df.copy()
    if area_filter:
        detail_df = detail_df[detail_df["area_clean"].isin(area_filter)]
    if has_amount_filter == "已提取金额":
        detail_df = detail_df[detail_df["amount"].notna()]
    elif has_amount_filter == "未提取金额":
        detail_df = detail_df[detail_df["amount"].isna()]
    if search_title:
        detail_df = detail_df[
            detail_df["title"].str.contains(search_title, case=False, na=False)
        ]

    # 构建展示表
    display_detail = detail_df[
        ["title", "area_clean", "published_at", "amount", "article_type", "liangke_url"]
    ].copy()
    display_detail["published_at"] = display_detail["published_at"].dt.strftime("%Y-%m-%d")
    display_detail["amount_display"] = display_detail["amount"].apply(
        lambda x: f"¥{x/10000:.2f}亿" if pd.notna(x) else "—"
    )

    # 文章类型映射
    type_map = {"news": "新闻", "flash": "快讯", "reference": "参考文献"}
    display_detail["article_type"] = display_detail["article_type"].map(type_map).fillna(
        display_detail["article_type"]
    )

    display_detail = display_detail.rename(
        columns={
            "title": "标题",
            "area_clean": "地区",
            "published_at": "发布日期",
            "amount_display": "投融资金额",
            "article_type": "类型",
        }
    )

    st.caption(f"共 {len(display_detail)} 条记录")
    st.dataframe(
        display_detail[["标题", "地区", "发布日期", "投融资金额", "类型"]],
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            "标题": st.column_config.TextColumn(width="large"),
            "地区": st.column_config.TextColumn(width="small"),
            "发布日期": st.column_config.TextColumn(width="small"),
            "投融资金额": st.column_config.TextColumn(width="medium"),
            "类型": st.column_config.TextColumn(width="small"),
        },
    )

# ═══ 页脚 ═══
st.divider()
st.caption(
    f"📌 数据来源: liangke_historical · 总文章: {len(df)} · "
    f"可提取金额: {len(df_with_amount)} ({len(df_with_amount)/max(len(df),1)*100:.1f}%) · "
    f"最后刷新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
