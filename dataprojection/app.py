"""Data Projection — Conversational App Building Platform.

Users log in, create Streamlit apps through conversation with AI,
and publish them for others to use.
"""

import json
import streamlit as st

from dataprojection.config import LLM_API_KEY, LLM_MODEL
from dataprojection.db.models import init_db, get_session
from dataprojection.db.repository import (
    get_or_create_admin, create_conversation, get_conversations,
    get_conversation, add_message, delete_conversation,
    update_conversation_title, get_conversation_as_history,
    register_user, authenticate_user,
)
from dataprojection.auth.jwt import create_token
from dataprojection.workspace.manager import (
    load_user_apps, register_app, unregister_app, get_app,
    start_app, stop_app, get_app_status, get_all_published_apps,
)
from dataprojection.workspace.context import set_context


st.set_page_config(
    page_title="Data Projection",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    html, body, [class*="css"] { font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; }
    iframe { border: 1px solid #ddd; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ═══ Session ═══

def init_session():
    init_db()
    db = get_session()
    try:
        get_or_create_admin(db)
    finally:
        db.close()

    defaults = {
        "logged_in": False, "user_id": None, "username": None, "role": None, "token": None,
        "conversation_id": None, "messages": [], "chat_history": [],
        "processing": False, "token_total": {"input": 0, "output": 0},
        "page": "apps", "current_app": None, "app_port": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ═══ Auth ═══

def render_auth():
    mode = st.session_state.get("auth_mode", "login")
    st.title("🏗️ Data Projection")
    st.caption("构建你自己的数据应用")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.container(border=True):
            if mode == "login":
                st.subheader("登录")
                u = st.text_input("用户名", key="login_u")
                p = st.text_input("密码", type="password", key="login_p")
                if st.button("登录", use_container_width=True):
                    db = get_session()
                    try:
                        user, err = authenticate_user(db, u, p)
                        if user:
                            st.session_state.update({
                                "logged_in": True, "user_id": user.id,
                                "username": user.username, "role": user.role,
                                "token": create_token(user.id, user.username, user.role),
                                "messages": [], "chat_history": [],
                                "conversation_id": None, "current_app": None,
                            })
                            st.rerun()
                        else:
                            st.error(err)
                    finally:
                        db.close()
                st.divider()
                if st.button("注册新账号", use_container_width=True):
                    st.session_state.auth_mode = "register"
                    st.rerun()
            else:
                st.subheader("注册")
                u = st.text_input("用户名", key="reg_u")
                d = st.text_input("显示名称", key="reg_d")
                p = st.text_input("密码", type="password", key="reg_p")
                p2 = st.text_input("确认密码", type="password", key="reg_p2")
                if st.button("注册", use_container_width=True):
                    if p != p2:
                        st.error("两次密码不一致")
                    else:
                        db = get_session()
                        try:
                            user, err = register_user(db, u, p, d or u)
                            if user:
                                st.success("注册成功！")
                                st.session_state.auth_mode = "login"
                                st.rerun()
                            else:
                                st.error(err)
                        finally:
                            db.close()
                if st.button("返回登录", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()


# ═══ Sidebar ═══

def render_sidebar():
    with st.sidebar:
        st.title("🏗️ Data Projection")
        st.caption(f"👤 {st.session_state.username}")

        if st.button("🚪 退出", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

        st.divider()

        nav = st.radio("导航", ["📱 我的应用", "🏪 应用市场"],
                       index=0 if st.session_state.page in ("apps", "builder") else 1,
                       key="main_nav")

        if nav == "📱 我的应用" and st.session_state.page == "marketplace":
            st.session_state.page = "apps"
            st.rerun()
        elif nav == "🏪 应用市场" and st.session_state.page != "marketplace":
            st.session_state.page = "marketplace"
            st.rerun()

        st.divider()

        # My apps list
        apps = load_user_apps(st.session_state.username)
        if apps:
            st.caption("我的应用")
            for app in apps:
                c1, c2 = st.columns([3, 1])
                with c1:
                    label = f"{'🟢' if _is_app_running(app) else '⚫'} {app['name']}"
                    if st.button(label[:25], key=f"app_{app['slug']}",
                                 use_container_width=True):
                        _open_app_builder(app["slug"])
                with c2:
                    if st.button("🗑️", key=f"del_{app['slug']}"):
                        _delete_app(app["slug"])


def _is_app_running(app: dict) -> bool:
    status = get_app_status(st.session_state.username, app["slug"])
    return status.get("running", False)


def _open_app_builder(slug: str):
    app = get_app(st.session_state.username, slug)
    st.session_state.current_app = slug
    st.session_state.app_port = app["port"] if app else None
    st.session_state.page = "builder"
    st.session_state.messages = []
    st.session_state.chat_history = []
    st.rerun()


def _delete_app(slug: str):
    stop_app(st.session_state.username, slug)
    unregister_app(st.session_state.username, slug)
    if st.session_state.current_app == slug:
        st.session_state.current_app = None
    st.rerun()


# ═══ My Apps Page ═══

def render_my_apps():
    st.title("📱 我的应用")

    apps = load_user_apps(st.session_state.username)

    # Use session state to control form visibility
    if "show_create_form" not in st.session_state:
        st.session_state.show_create_form = False

    if st.button("➕ 创建新应用", use_container_width=True, type="primary"):
        st.session_state.show_create_form = True
        st.rerun()

    if st.session_state.show_create_form:
        _create_new_app_dialog()
        return  # Don't show app list while form is open

    if not apps:
        st.info("还没有应用。点击上方按钮创建你的第一个数据应用！")
        return

    st.divider()

    for app in apps:
        status = get_app_status(st.session_state.username, app["slug"])
        running = status.get("running", False)

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
            with c1:
                status_icon = "🟢" if running else "⚫"
                st.subheader(f"{status_icon} {app['name']}")
                if app.get("description"):
                    st.caption(app["description"])
                st.caption(f"端口: {app['port']} | "
                          f"创建于 {app.get('created_at', '?')[:10]}")

            with c2:
                if running and status.get("url"):
                    st.caption(f"🔗 {status['url']}")

            with c3:
                if st.button("💬 打开" if not running else "🔄 重启",
                             key=f"open_{app['slug']}"):
                    if not running:
                        start_app(st.session_state.username, app["slug"], app["port"])
                    else:
                        stop_app(st.session_state.username, app["slug"])
                        start_app(st.session_state.username, app["slug"], app["port"])
                    st.rerun()

            with c4:
                if st.button("🗑️", key=f"d2_{app['slug']}"):
                    _delete_app(app["slug"])
                    st.rerun()


def _create_new_app_dialog():
    """Form to create a new app — uses regular widgets and session_state to avoid form rerun issues."""
    with st.container(border=True):
        st.subheader("创建新应用")

        name = st.text_input("应用名称", placeholder="例如：融资数据看板",
                            key="new_app_name")
        slug = st.text_input("标识符（英文小写+下划线）",
                            placeholder="例如：funding_dashboard",
                            key="new_app_slug")
        desc = st.text_area("简介（可选）", key="new_app_desc")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 创建", use_container_width=True):
                if name and slug:
                    slug_clean = slug.strip().lower().replace(" ", "_").replace("-", "_")
                    register_app(st.session_state.username, slug_clean, name, desc)
                    st.session_state.show_create_form = False
                    st.session_state.current_app = slug_clean
                    st.session_state.page = "builder"
                    st.session_state.messages = []
                    st.session_state.chat_history = []
                    st.rerun()
                else:
                    st.error("请至少填写应用名称和标识符")
        with col2:
            if st.button("❌ 取消", use_container_width=True):
                st.session_state.show_create_form = False
                st.rerun()


# ═══ App Builder Page ═══

def render_builder():
    """Chat on left, preview on right."""
    slug = st.session_state.current_app
    if not slug:
        st.session_state.page = "apps"
        st.rerun()
        return

    app = get_app(st.session_state.username, slug)
    if not app:
        st.error("应用不存在")
        return

    # Set workspace context for AI tools
    set_context(st.session_state.username, slug)

    # ── Header ──
    st.title(f"🏗️ {app['name']}")

    # Controls row
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        st.caption(f"端口: {app['port']}")
    with c2:
        if st.button("🔄 重启应用", use_container_width=True):
            stop_app(st.session_state.username, slug)
            start_app(st.session_state.username, slug, app["port"])
            st.rerun()
    with c3:
        if st.button("⏹ 停止", use_container_width=True):
            stop_app(st.session_state.username, slug)
            st.rerun()
    with c4:
        pub_text = "✅ 已发布" if app.get("is_published") else "📤 发布"
        if st.button(pub_text, use_container_width=True):
            apps = load_user_apps(st.session_state.username)
            for a in apps:
                if a["slug"] == slug:
                    a["is_published"] = not a.get("is_published")
                    from dataprojection.workspace.manager import save_user_apps
                    save_user_apps(st.session_state.username, apps)
                    st.rerun()

    # ── Two-column layout ──
    left, right = st.columns([1, 1])

    # LEFT: Chat
    with left:
        st.subheader("💬 对话")

        # Message history
        chat_container = st.container(height=450)
        with chat_container:
            if not st.session_state.messages:
                st.info(
                    "👋 在这个对话中，你可以指挥 AI 构建你的应用。\n\n"
                    "试试说：**「帮我做一个融资数据看板，要有文章类型分布饼图、"
                    "月度趋势折线图、和一个总文章数指标」**\n\n"
                    "AI 会写代码、启动应用，你可以在右侧预览。"
                )
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Input
        prompt = st.chat_input(
            "告诉 AI 你想做什么..." if not st.session_state.processing else "AI 正在工作中...",
            disabled=st.session_state.processing,
        )
        if prompt:
            _process_message(prompt, slug)

    # RIGHT: Preview
    with right:
        st.subheader("👁️ 预览")

        status = get_app_status(st.session_state.username, slug)
        if status.get("running"):
            url = status["url"]
            st.caption(f"🟢 {url}")
            st.components.v1.iframe(url, height=500, scrolling=True)
        else:
            st.caption("⚫ 应用未启动")
            st.info("在对话中让 AI 写好代码并启动应用，预览会出现在这里。")
            if st.button("🚀 手动启动"):
                start_app(st.session_state.username, slug, app["port"])
                st.rerun()


def _process_message(prompt: str, slug: str):
    """Send message to Claude Code CLI, display response, persist."""
    if not prompt.strip(): return

    if st.session_state.conversation_id is None:
        db = get_session()
        try:
            conv = create_conversation(db, st.session_state.user_id)
            st.session_state.conversation_id = conv.id
        finally:
            db.close()

    # Track whether this is first message in this app
    if "claude_session_active" not in st.session_state:
        st.session_state.claude_session_active = {}

    is_continue = st.session_state.claude_session_active.get(slug, False)

    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.processing = True

    db = get_session()
    try:
        add_message(db, st.session_state.conversation_id, role="user", content=prompt)
    finally:
        db.close()

    # ── Stream Claude Code CLI in real-time ──
    from dataprojection.claude_cli.adapter import stream_claude
    from dataprojection.workspace.manager import get_app_dir

    app_dir = get_app_dir(st.session_state.username, slug)

    with st.chat_message("assistant"):
        status = st.empty()
        text_output = st.empty()
        tools_log = st.empty()

        status.info("🤖 Claude Code 已连接...")

        collected_text = []
        collected_tools = []
        error_msg = None

        for event in stream_claude(app_dir, prompt, is_continue=is_continue):
            etype = event.get("type", "")

            if etype == "status":
                status.info(f"🤖 {event['message']}")

            elif etype == "thinking":
                tokens = event.get("tokens", 0)
                status.info(f"🤖 思考中... ({tokens} tokens)")

            elif etype == "text":
                collected_text.append(event["content"])
                text_output.markdown("".join(collected_text))

            elif etype == "tool_use":
                collected_tools.append(event["description"])
                status.info(f"🔧 {event['description']}")
                tools_log.caption("🔧 " + " → ".join(collected_tools[-5:]))

            elif etype == "done":
                final = event.get("text", "")
                if final and final not in collected_text:
                    collected_text.append(final)
                    text_output.markdown(final)

                tools = event.get("tools_used", [])
                if tools:
                    tools_log.caption(f"🔧 工具: {', '.join(tools)}")
                status.empty()

            elif etype == "error":
                error_msg = event.get("message", "Unknown error")
                detail = event.get("stderr", "")
                status.error(f"❌ {error_msg}")
                if detail:
                    with st.expander("查看错误详情"):
                        st.code(detail[:2000])

            elif etype == "stderr":
                with st.expander("📋 CLI 输出"):
                    st.code(event.get("content", "")[:2000])

        # After streaming ends
        full_text = "\n\n".join(collected_text)
        if error_msg and not full_text:
            st.error(f"❌ {error_msg}")
        elif not full_text:
            st.markdown("（Claude Code 未返回文本，请重试）")
        else:
            st.markdown(full_text)

        tools_log.empty()

    # Final text for persistence
    final_text = "\n\n".join(collected_text)
    if error_msg and not final_text:
        final_text = f"❌ {error_msg}"

    st.session_state.claude_session_active[slug] = True
    st.session_state.messages.append({"role": "assistant", "content": final_text})

    db = get_session()
    try:
        add_message(db, st.session_state.conversation_id,
                     role="assistant", content=final_text,
                     token_count=len(collected_tools))
        conv = get_conversation(db, st.session_state.conversation_id)
        if conv and (not conv.title or conv.title == "新对话"):
            t = prompt.strip()[:30]
            update_conversation_title(db, st.session_state.conversation_id,
                                      t + ("…" if len(prompt) > 30 else ""))
    finally:
        db.close()

    st.session_state.token_total = {"input": 0, "output": 0}
    st.session_state.processing = False
    st.rerun()


# ═══ Marketplace ═══

def render_marketplace():
    st.title("🏪 应用市场")
    published = get_all_published_apps()

    if not published:
        st.info("还没有人发布应用。成为第一个吧！")
        return

    cols = st.columns(3)
    for i, app in enumerate(published):
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(app.get("name", "未命名")[:25])
                st.caption(f"作者: {app.get('author', '?')}")
                if app.get("description"):
                    st.caption(app["description"][:60])
                st.caption(f"端口: {app.get('port', '?')}")


# ═══ Main ═══

def main():
    init_session()

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    if not st.session_state.logged_in:
        render_auth()
        return

    render_sidebar()

    page = st.session_state.page
    if page == "apps":
        render_my_apps()
    elif page == "builder":
        render_builder()
    elif page == "marketplace":
        render_marketplace()
    else:
        render_my_apps()


if __name__ == "__main__":
    main()
