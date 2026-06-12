"""Step 1: Verify Claude Code CLI works reliably via subprocess.

Usage: python test_cli.py "你的提示词"
"""

import subprocess
import sys
import os

CLAUDE_BIN = r"C:\Users\zhouj\AppData\Roaming\npm\claude.cmd"
WORK_DIR = os.path.join(os.path.dirname(__file__), "workspaces", "test")
os.makedirs(WORK_DIR, exist_ok=True)


def run(prompt: str):
    cmd = [
        CLAUDE_BIN,
        "--permission-mode", "bypassPermissions",
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
    ]

    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = "https://api.deepseek.com/anthropic"
    env["ANTHROPIC_AUTH_TOKEN"] = "sk-589d0203dd0b4c96a75914a684139df3"
    env["ANTHROPIC_MODEL"] = "deepseek-v4-pro[1m]"
    env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = "deepseek-v4-pro[1m]"
    env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = "deepseek-v4-flash"
    env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = "deepseek-v4-pro[1m]"
    env["CLAUDE_CODE_EFFORT_LEVEL"] = "max"
    env.pop("CLAUDE_CODE_OFFLINE", None)

    print(f"> 工作目录: {WORK_DIR}")
    print(f"> 命令: claude -p \"{prompt[:60]}...\"")
    print("-" * 50)

    proc = subprocess.Popen(
        cmd,
        cwd=WORK_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=env,
    )

    stdout_lines = []
    stderr_lines = []

    # Read stdout line by line
    for line in proc.stdout:
        line = line.strip()
        if line:
            stdout_lines.append(line)
            # Try to parse and show useful info
            import json
            try:
                event = json.loads(line)
                t = event.get("type", "")
                if t == "system":
                    if event.get("subtype") == "init":
                        print("[OK] Claude Code 已连接")
                elif t == "assistant":
                    for block in event.get("message", {}).get("content", []):
                        if block.get("type") == "text":
                            print(f"> {block['text'][:120]}")
                        elif block.get("type") == "tool_use":
                            print(f"🔧 {block.get('name', '?')}")
                elif t == "result":
                    print("[OK] 完成")
                elif t == "error":
                    print(f"✗ 错误: {event.get('message', '')}")
            except json.JSONDecodeError:
                print(f"[非JSON] {line[:100]}")

    proc.wait(timeout=120)

    # Read stderr
    for line in proc.stderr:
        stderr_lines.append(line.strip())

    print("-" * 50)
    print(f"> 退出码: {proc.returncode}")
    print(f"> stdout 行数: {len(stdout_lines)}")
    print(f"> stderr 行数: {len(stderr_lines)}")

    if stderr_lines:
        print("\n--- stderr ---")
        for l in stderr_lines:
            print(l)

    return proc.returncode


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "用中文回复：你好，我是Claude Code CLI测试。请确认你能正常工作，只需说'可以'即可。"
    exit_code = run(prompt)
    print(f"\n{'[OK] 测试通过' if exit_code == 0 else f'✗ 测试失败 (exit {exit_code})'}")
