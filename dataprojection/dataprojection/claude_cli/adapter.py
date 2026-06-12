"""Claude Code CLI adapter — streaming events for real-time UI feedback."""

import json
import subprocess
import os
import threading
from pathlib import Path
from typing import Iterator

CLAUDE_BIN = r"C:\Users\zhouj\AppData\Roaming\npm\claude.cmd"


def stream_claude(app_dir: Path, prompt: str,
                  is_continue: bool = False) -> Iterator[dict]:
    """Run Claude Code, yielding events as they arrive in real-time."""
    cmd = [CLAUDE_BIN]
    if is_continue:
        cmd.append("-c")
    cmd += [
        "--add-dir", "D:/Claude_code/liangke_historical",
        "--add-dir", str(app_dir),
        "--permission-mode", "bypassPermissions",
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
    ]

    env = os.environ.copy()
    env.pop("CLAUDE_CODE_OFFLINE", None)

    try:
        proc = subprocess.Popen(
            cmd, cwd=str(app_dir),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", env=env,
        )

        # Collect stderr in background thread
        stderr_lines = []
        def _read_stderr():
            for line in proc.stderr:
                stderr_lines.append(line.strip())
        t = threading.Thread(target=_read_stderr, daemon=True)
        t.start()

        text_parts = []
        tools_seen = []
        token_count = 0

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = event.get("type", "")

            if etype == "system" and event.get("subtype") == "init":
                yield {"type": "status", "message": "Claude Code 已启动"}

            elif etype == "system" and event.get("subtype") == "thinking_tokens":
                token_count = event.get("estimated_tokens", 0)
                yield {"type": "thinking", "tokens": token_count}

            elif etype == "assistant":
                msg = event.get("message", {})
                for block in msg.get("content", []):
                    bt = block.get("type", "")
                    if bt == "text":
                        txt = block.get("text", "").strip()
                        if txt:
                            text_parts.append(txt)
                            yield {"type": "text", "content": txt}
                    elif bt == "tool_use":
                        name = block.get("name", "?")
                        inp = block.get("input", {})
                        tools_seen.append(name)
                        yield {"type": "tool_use", "name": name,
                               "description": _desc(name, inp)}

            elif etype == "result":
                rd = event.get("result", event)
                if isinstance(rd, dict) and rd.get("is_error"):
                    yield {"type": "error",
                           "message": str(rd.get("error", "Unknown"))}

            elif etype == "error":
                yield {"type": "error", "message": event.get("message", str(event))}

        proc.wait(timeout=300)
        t.join(timeout=5)

        # Collect stderr for debugging
        if proc.returncode != 0 or stderr_lines:
            stderr_text = "\n".join(stderr_lines)
            if proc.returncode != 0:
                yield {"type": "error",
                       "message": f"Exit {proc.returncode}",
                       "stderr": stderr_text[:2000]}
            elif stderr_text.strip():
                yield {"type": "stderr", "content": stderr_text[:2000]}

        final = "\n\n".join(text_parts).strip()
        yield {"type": "done", "text": final, "tools_used": tools_seen,
               "token_usage": {"thinking": token_count}}

    except subprocess.TimeoutExpired:
        proc.kill()
        yield {"type": "error", "message": "超时（5分钟）"}
    except FileNotFoundError:
        yield {"type": "error", "message": f"claude 未找到: {CLAUDE_BIN}"}
    except Exception as e:
        yield {"type": "error", "message": str(e)}


def _desc(name: str, inp: dict) -> str:
    if name == "Write": return f"写文件: {inp.get('file_path', '?')}"
    if name == "Edit": return f"编辑: {inp.get('file_path', '?')}"
    if name == "Bash": return f"执行: {str(inp.get('command', inp.get('description', '?')))[:80]}"
    if name == "Read": return f"读取: {inp.get('file_path', '?')}"
    if name == "Grep": return f"搜索: {inp.get('pattern', '?')}"
    if name == "Glob": return f"查找: {inp.get('pattern', '?')}"
    return name
