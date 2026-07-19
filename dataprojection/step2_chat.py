"""Step 2: Dynamic app pages — Claude writes code, it becomes a nav item."""

import streamlit as st
import subprocess
import json
import os
import threading
import importlib.util
import socket

CLAUDE_BIN = r"C:\Users\zhouj\AppData\Roaming\npm\claude.cmd"
WORK_DIR = os.path.join(os.path.dirname(__file__), "workspaces", "default")
CHAT_FILE = os.path.join(WORK_DIR, "chat_history.json")
os.makedirs(WORK_DIR, exist_ok=True)


def load_chat() -> list[dict]:
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_chat(messages: list[dict]):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="Data Projection", page_icon="💬", layout="wide")

# Session — load from disk on first run
if "messages" not in st.session_state:
    st.session_state.messages = load_chat()
if "session_active" not in st.session_state:
    st.session_state.session_active = os.path.exists(os.path.join(WORK_DIR, "app.py"))
if "app_ready" not in st.session_state:
    st.session_state.app_ready = False


def is_app_running(port=8505) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r = s.connect_ex(("127.0.0.1", port)) == 0
    s.close()
    return r


def start_app(port=8505):
    req = os.path.join(WORK_DIR, "requirements.txt")
    if os.path.exists(req):
        subprocess.run(["pip", "install", "-r", req, "-q"], cwd=WORK_DIR)
    subprocess.run(["taskkill", "/F", "/FI", f"WINDOWTITLE eq *{port}*"],
                   capture_output=True)
    subprocess.Popen(
        ["python", "-m", "streamlit", "run", "app.py",
         "--server.port", str(port), "--server.headless", "true",
         "--server.address", "0.0.0.0",
         "--browser.gatherUsageStats", "false"],
        cwd=WORK_DIR,
    )


def call_claude(prompt: str, is_continue: bool) -> list[dict]:
    cmd = [CLAUDE_BIN]
    if is_continue:
        cmd.append("-c")
    cmd += [
        "--add-dir", WORK_DIR,
        "--permission-mode", "bypassPermissions",
        "--disallowedTools", "Bash",
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
    ]

    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = "https://api.deepseek.com/anthropic"
    env["ANTHROPIC_AUTH_TOKEN"] = os.environ.get("DEEPSEEK_API_KEY", "")
    env["ANTHROPIC_MODEL"] = "deepseek-v4-pro[1m]"
    env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = "deepseek-v4-pro[1m]"
    env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = "deepseek-v4-flash"
    env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = "deepseek-v4-pro[1m]"
    env["CLAUDE_CODE_EFFORT_LEVEL"] = "max"
    env.pop("CLAUDE_CODE_OFFLINE", None)

    proc = subprocess.Popen(
        cmd, cwd=WORK_DIR,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", env=env,
    )

    stderr_lines = []
    def _read_stderr():
        for line in proc.stderr:
            stderr_lines.append(line.strip())
    t = threading.Thread(target=_read_stderr, daemon=True)
    t.start()

    events = []
    for line in proc.stdout:
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                events.append({"type": "raw", "content": line})

    proc.wait(timeout=120)
    t.join(timeout=5)

    if stderr_lines:
        events.append({"type": "stderr", "content": "\n".join(stderr_lines)})

    return events


def sync_app_to_pages():
    """Copy/transform workspace app.py into a Streamlit pages module."""
    app_py = os.path.join(WORK_DIR, "app.py")
    if not os.path.exists(app_py):
        return False

    with open(app_py, "r", encoding="utf-8") as f:
        code = f.read()

    # Wrap user's code: remove set_page_config (we manage that),
    # keep everything else so it renders as a page
    lines = []
    skip = False
    for line in code.split("\n"):
        if "st.set_page_config" in line:
            continue
        if 'st.set_page_config' in line:
            continue
        lines.append(line)

    page_code = "\n".join(lines)

    # Write to pages directory
    page_path = os.path.join(PAGES_DIR, "1_my_app.py")
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(f'''"""User-built application."""
import streamlit as st

# st.set_page_config is handled by Data Projection
{page_code}
''')

    return True


# ═══ SIDEBAR NAVIGATION ═══
app_py = os.path.join(WORK_DIR, "app.py")
has_app = os.path.exists(app_py)

nav_options = ["💬 对话"]
if has_app:
    nav_options.append("📱 我的应用")

nav = st.sidebar.radio("导航", nav_options, key="main_nav")
if nav == "💬 对话":
    st.session_state.page = "chat"
else:
    st.session_state.page = "app"

with st.sidebar:
    st.divider()
    st.caption(f"Workspace: `default/`")
    if os.path.exists(WORK_DIR):
        for f in sorted(os.listdir(WORK_DIR)):
            if not f.startswith(".") and not f.endswith(".db"):
                st.caption(f"📄 {f}")

# ═══ CHAT PAGE ═══
if st.session_state.page == "chat":
    st.title("💬 Data Projection")
    st.caption("和 Claude Code 对话，构建你的应用")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("告诉 Claude Code 你想做什么..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_chat(st.session_state.messages)
        is_continue = st.session_state.session_active

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Claude Code 工作中..."):
                events = call_claude(prompt, is_continue)

            collected_text = []
            collected_tools = []
            error_msg = None

            for event in events:
                t = event.get("type", "")
                if t == "assistant":
                    for block in event.get("message", {}).get("content", []):
                        if block.get("type") == "text":
                            txt = block["text"].strip()
                            if txt:
                                collected_text.append(txt)
                        elif block.get("type") == "tool_use":
                            name = block.get("name", "?")
                            inp = block.get("input", {})
                            desc = f"{name}: {str(inp.get('file_path', inp.get('description', inp.get('command', ''))))[:60]}"
                            collected_tools.append(desc)
                elif t == "error":
                    error_msg = event.get("message", "Unknown")

            final_text = "\n\n".join(collected_text)
            if error_msg and not final_text and not collected_tools:
                st.error(f"✗ {error_msg}")
            if final_text:
                st.markdown(final_text)
            if collected_tools:
                st.caption(f"🔧 {' > '.join(collected_tools[-8:])}")
            if not final_text and not collected_tools:
                st.markdown("(未返回内容)")
                with st.expander("调试"):
                    for e in events[-5:]:
                        st.json(e)

        st.session_state.messages.append({"role": "assistant", "content": final_text})
        st.session_state.session_active = True
        save_chat(st.session_state.messages)

        # Auto-start app if Claude wrote/modified app.py
        if os.path.exists(app_py) and any(
            kw in t for t in collected_tools for kw in ["Write", "Edit"]
        ):
            with st.spinner("正在启动应用..."):
                start_app()
            st.success("✅ 应用已自动启动，切换到「📱 我的应用」查看")

        st.rerun()

# ═══ APP PAGE (iframe in main area) ═══
else:
    running = is_app_running()

    # Auto-start if not running
    if not running:
        if st.button("🚀 启动应用", use_container_width=True, type="primary"):
            start_app()
            st.rerun()
        st.info("应用还未启动，点击上方按钮启动")
    else:
        st.success("🟢 应用运行中")

    # Full-width iframe in main area
    if running or True:  # always show iframe placeholder
        st.components.v1.iframe("http://localhost:8505", height=700, scrolling=True)

    # Show code
    with st.expander("📝 查看源代码"):
        with open(app_py, "r", encoding="utf-8") as f:
            st.code(f.read(), language="python")
