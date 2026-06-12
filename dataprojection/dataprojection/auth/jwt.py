"""JWT token creation and validation."""
import os
from datetime import datetime, timedelta, timezone

import jwt

# Default secret — override via env for production
JWT_SECRET = os.getenv("JWT_SECRET", "dataprojection-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


def create_token(user_id: int, username: str, role: str) -> str:
    """Create a JWT token for an authenticated user."""
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Validate and decode a JWT token. Returns None if invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token: str) -> dict | None:
    """Extract user info from token. Returns {user_id, username, role} or None."""
    payload = decode_token(token)
    if payload is None:
        return None
    return {
        "user_id": int(payload["sub"]),
        "username": payload["username"],
        "role": payload["role"],
    }
