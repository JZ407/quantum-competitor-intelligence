"""Workspace Manager — user isolation, app registry, port management, process control.

Directory structure:
    workspaces/
      {username}/
        apps.json          # app metadata
        {app_slug}/
          app.py           # generated Streamlit app
          requirements.txt
          ...

Port range: 8510-8599 (90 ports available)
Each app gets a unique port managed by the global app registry.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# ── Paths ──
WORKSPACES_ROOT = Path(__file__).parent.parent.parent / "workspaces"
PORT_RANGE_START = 8510
PORT_RANGE_END = 8599

# In-memory process registry: {port: subprocess.Popen}
_running_apps: dict[int, subprocess.Popen] = {}


def _ensure_workspaces():
    WORKSPACES_ROOT.mkdir(parents=True, exist_ok=True)


def get_user_workspace(username: str) -> Path:
    """Get the workspace directory for a user."""
    _ensure_workspaces()
    ws = WORKSPACES_ROOT / username
    ws.mkdir(parents=True, exist_ok=True)
    return ws


def get_app_dir(username: str, app_slug: str) -> Path:
    """Get the directory for a specific app."""
    ws = get_user_workspace(username)
    app_dir = ws / app_slug
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


# ── App Registry ──

def _get_apps_json_path(username: str) -> Path:
    return get_user_workspace(username) / "apps.json"


def load_user_apps(username: str) -> list[dict]:
    """Load app metadata for a user."""
    path = _get_apps_json_path(username)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return []


def save_user_apps(username: str, apps: list[dict]):
    """Save app metadata for a user."""
    path = _get_apps_json_path(username)
    path.write_text(json.dumps(apps, ensure_ascii=False, indent=2), encoding="utf-8")


def register_app(username: str, slug: str, name: str, description: str = "",
                 port: int = None, is_published: bool = False) -> dict:
    """Register a new app in the user's app registry."""
    apps = load_user_apps(username)

    # Check slug uniqueness
    for app in apps:
        if app["slug"] == slug:
            # Update existing
            app["name"] = name
            app["description"] = description
            app["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_user_apps(username, apps)
            return app

    if port is None:
        port = _allocate_port()

    app = {
        "slug": slug,
        "name": name,
        "description": description,
        "port": port,
        "is_published": is_published,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    apps.append(app)
    save_user_apps(username, apps)
    return app


def unregister_app(username: str, slug: str):
    """Remove an app from the registry."""
    apps = load_user_apps(username)
    apps = [a for a in apps if a["slug"] != slug]
    save_user_apps(username, apps)


def get_app(username: str, slug: str) -> dict | None:
    """Get a single app's metadata."""
    apps = load_user_apps(username)
    for app in apps:
        if app["slug"] == slug:
            return app
    return None


def get_all_published_apps() -> list[dict]:
    """Get all published apps from all users (for marketplace)."""
    all_apps = []
    _ensure_workspaces()
    for user_dir in WORKSPACES_ROOT.iterdir():
        if user_dir.is_dir():
            username = user_dir.name
            apps = load_user_apps(username)
            for app in apps:
                if app.get("is_published"):
                    app["author"] = username
                    all_apps.append(app)
    return all_apps


# ── Port Management ──

def _allocate_port() -> int:
    """Find a free port in the configured range."""
    used_ports = set()
    _ensure_workspaces()
    for user_dir in WORKSPACES_ROOT.iterdir():
        if user_dir.is_dir():
            for app in load_user_apps(user_dir.name):
                used_ports.add(app.get("port", 0))

    # Also check running apps
    for port in _running_apps:
        used_ports.add(port)

    for port in range(PORT_RANGE_START, PORT_RANGE_END + 1):
        if port not in used_ports and _is_port_free(port):
            return port

    raise RuntimeError("No free ports available in range 8510-8599")


def _is_port_free(port: int) -> bool:
    """Check if a port is free."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


# ── File Operations (sandboxed to user workspace) ──

def read_file(username: str, app_slug: str, file_path: str) -> dict:
    """Read a file from the user's app directory.

    Returns {"content": str} or {"error": str}
    """
    app_dir = get_app_dir(username, app_slug)
    full_path = (app_dir / file_path).resolve()

    # Security: ensure path is within the app directory
    if not str(full_path).startswith(str(app_dir.resolve())):
        return {"error": f"Access denied: '{file_path}' is outside the app workspace"}

    if not full_path.exists():
        return {"error": f"File not found: {file_path}"}

    if full_path.is_dir():
        return {"error": f"'{file_path}' is a directory, use list_files instead"}

    try:
        content = full_path.read_text(encoding="utf-8")
        # Truncate very large files
        if len(content) > 50000:
            content = content[:50000] + "\n... (truncated)"
        return {"path": file_path, "content": content, "size": len(content)}
    except UnicodeDecodeError:
        return {"error": f"File '{file_path}' is not a text file"}
    except Exception as e:
        return {"error": str(e)}


def write_file(username: str, app_slug: str, file_path: str, content: str) -> dict:
    """Write a file to the user's app directory.

    Creates parent directories if needed.
    Returns {"path": str, "size": int} or {"error": str}
    """
    app_dir = get_app_dir(username, app_slug)
    full_path = (app_dir / file_path).resolve()

    # Security check
    if not str(full_path).startswith(str(app_dir.resolve())):
        return {"error": f"Access denied: '{file_path}' is outside the app workspace"}

    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return {"path": file_path, "size": len(content),
                "message": f"Wrote {len(content)} bytes to {file_path}"}
    except Exception as e:
        return {"error": str(e)}


def list_files(username: str, app_slug: str, subdir: str = "") -> dict:
    """List files in the app directory.

    Returns {"files": [...], "path": str} or {"error": str}
    """
    app_dir = get_app_dir(username, app_slug)
    target = (app_dir / subdir).resolve() if subdir else app_dir.resolve()

    if not str(target).startswith(str(app_dir.resolve())):
        return {"error": f"Access denied: '{subdir}' is outside the app workspace"}

    if not target.exists():
        return {"files": [], "path": subdir or "."}

    try:
        files = []
        for entry in sorted(target.iterdir()):
            info = {
                "name": entry.name,
                "type": "dir" if entry.is_dir() else "file",
                "size": entry.stat().st_size if entry.is_file() else 0,
            }
            files.append(info)
        return {"files": files, "path": subdir or ".",
                "count": len(files)}
    except Exception as e:
        return {"error": str(e)}


# ── Process Management ──

def start_app(username: str, app_slug: str, port: int = None) -> dict:
    """Start a Streamlit app on a given port.

    Returns {"status": "running", "port": int, "url": str} or {"status": "error", ...}
    """
    app_dir = get_app_dir(username, app_slug)
    app_file = app_dir / "app.py"

    if not app_file.exists():
        return {"status": "error", "error": f"app.py not found in {app_dir}"}

    if port is None:
        app = get_app(username, app_slug)
        port = app["port"] if app else _allocate_port()

    # Check if already running
    if port in _running_apps:
        proc = _running_apps[port]
        if proc.poll() is None:
            return {"status": "running", "port": port,
                    "url": f"http://localhost:{port}"}

    # Kill anything on that port
    _kill_port(port)

    # Install requirements if present
    req_file = app_dir / "requirements.txt"
    if req_file.exists():
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_file), "-q"],
                cwd=str(app_dir),
                timeout=60,
                capture_output=True,
            )
        except subprocess.TimeoutExpired:
            pass

    # Start Streamlit
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py",
             "--server.port", str(port),
             "--server.headless", "true",
             "--server.address", "0.0.0.0",
             "--browser.gatherUsageStats", "false"],
            cwd=str(app_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _running_apps[port] = proc

        # Wait a moment for startup
        time.sleep(3)

        if proc.poll() is None:
            return {"status": "running", "port": port,
                    "url": f"http://localhost:{port}"}
        else:
            return {"status": "error",
                    "error": f"App failed to start (exit code: {proc.returncode})"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def stop_app(username: str, app_slug: str) -> dict:
    """Stop a running Streamlit app."""
    app = get_app(username, app_slug)
    if not app:
        return {"status": "error", "error": f"App '{app_slug}' not found"}

    port = app["port"]
    if port in _running_apps:
        proc = _running_apps[port]
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        del _running_apps[port]

    _kill_port(port)
    return {"status": "stopped", "app": app_slug, "port": port}


def get_app_status(username: str, app_slug: str) -> dict:
    """Get the running status of an app."""
    app = get_app(username, app_slug)
    if not app:
        return {"status": "not_found", "slug": app_slug}

    port = app["port"]
    running = port in _running_apps and _running_apps[port].poll() is None

    return {
        "slug": app_slug,
        "name": app.get("name", ""),
        "port": port,
        "running": running,
        "url": f"http://localhost:{port}" if running else None,
    }


def _kill_port(port: int):
    """Kill any process on the given port."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/PID",
             str(_find_pid_on_port(port))],
            capture_output=True, timeout=5,
        )
    except Exception:
        pass


def _find_pid_on_port(port: int) -> int | None:
    """Find PID of process listening on a port."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.split("\n"):
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                return int(parts[-1])
    except Exception:
        pass
    return None
