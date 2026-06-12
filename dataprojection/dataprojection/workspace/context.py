"""Thread-local context for AI tools — current user and app being built."""

_context: dict = {"username": "admin", "app_slug": "my_app"}


def set_context(username: str, app_slug: str):
    """Set the current workspace context."""
    _context["username"] = username
    _context["app_slug"] = app_slug


def get_context() -> dict:
    """Get current username and app_slug."""
    return dict(_context)
