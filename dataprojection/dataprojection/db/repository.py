"""CRUD operations for platform database."""
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from dataprojection.db.models import (
    User, Conversation, Message, Dashboard, get_session,
)


# ── User ──

def get_or_create_admin(db: Session) -> User:
    """Get or create admin user. Migrates old plain-text passwords to bcrypt."""
    from dataprojection.auth.password import hash_password
    admin = db.query(User).filter(User.role == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            display_name="管理员",
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    elif not admin.password_hash.startswith("$2"):
        admin.password_hash = hash_password("admin123")
        db.commit()
    return admin


def register_user(db: Session, username: str, password: str,
                  display_name: str = None) -> tuple[User | None, str | None]:
    """Register a new user.

    Returns (user, error). One will be None.
    Error cases: username too short, password too short, username taken.
    """
    if not username or len(username.strip()) < 2:
        return None, "用户名至少需要 2 个字符"
    if not password or len(password) < 4:
        return None, "密码至少需要 4 个字符"

    username = username.strip().lower()

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return None, "用户名已被占用"

    from dataprojection.auth.password import hash_password
    user = User(
        username=username,
        password_hash=hash_password(password),
        display_name=display_name or username,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def authenticate_user(db: Session, username: str,
                      password: str) -> tuple[User | None, str | None]:
    """Authenticate a user by username and password.

    Returns (user, error). One will be None.
    """
    from dataprojection.auth.password import verify_password

    user = db.query(User).filter(
        User.username == username.strip().lower(),
        User.is_active == True,
    ).first()

    if not user:
        return None, "用户名或密码错误"

    if not verify_password(password, user.password_hash):
        return None, "用户名或密码错误"

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return user, None


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


def update_user_role(db: Session, user_id: int, new_role: str) -> bool:
    """Update a user's role. Returns True on success."""
    user = get_user_by_id(db, user_id)
    if user:
        user.role = new_role
        db.commit()
        return True
    return False


def delete_user(db: Session, user_id: int):
    """Soft-delete a user by deactivating them."""
    user = get_user_by_id(db, user_id)
    if user:
        user.is_active = False
        db.commit()


# ── Conversations ──

def create_conversation(db: Session, user_id: int, title: str = None,
                        system_prompt: str = None) -> Conversation:
    conv = Conversation(
        user_id=user_id,
        title=title or "新对话",
        system_prompt=system_prompt,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def get_conversations(db: Session, user_id: int) -> list[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


def get_conversation(db: Session, conversation_id: int) -> Conversation | None:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def update_conversation_title(db: Session, conversation_id: int, title: str):
    conv = get_conversation(db, conversation_id)
    if conv:
        conv.title = title
        conv.updated_at = datetime.now(timezone.utc)
        db.commit()


def delete_conversation(db: Session, conversation_id: int):
    conv = get_conversation(db, conversation_id)
    if conv:
        # Delete all messages first (NOT NULL foreign key)
        db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).delete()
        db.delete(conv)
        db.commit()


# ── Messages ──

def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    tool_name: str = None,
    tool_input: dict = None,
    has_chart: bool = False,
    chart_spec: dict = None,
    chart_type: str = None,
    token_count: int = None,
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_name=tool_name,
        tool_input=json.dumps(tool_input) if tool_input else None,
        has_chart=has_chart,
        chart_spec=json.dumps(chart_spec) if chart_spec else None,
        chart_type=chart_type,
        token_count=token_count,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # Update conversation timestamp
    conv = get_conversation(db, conversation_id)
    if conv:
        conv.updated_at = datetime.now(timezone.utc)
        db.commit()

    return msg


def get_messages(db: Session, conversation_id: int) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id)
        .all()
    )


def get_conversation_as_history(db: Session, conversation_id: int) -> list[dict]:
    """Convert stored messages to API-compatible history format."""
    messages = get_messages(db, conversation_id)
    history = []
    for msg in messages:
        if msg.role == "user":
            history.append({"role": "user", "content": msg.content})
        elif msg.role == "assistant":
            history.append({"role": "assistant", "content": msg.content})
    return history


# ── Dashboards ──

def create_dashboard(db: Session, user_id: int, title: str,
                     description: str = "", config: dict = None,
                     conversation_id: int = None) -> Dashboard:
    dashboard = Dashboard(
        user_id=user_id,
        title=title,
        description=description,
        config=json.dumps(config or {}),
        source_conversation_id=conversation_id,
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return dashboard


def get_dashboards(db: Session, user_id: int) -> list[Dashboard]:
    return (
        db.query(Dashboard)
        .filter(Dashboard.user_id == user_id)
        .order_by(Dashboard.updated_at.desc())
        .all()
    )


def get_dashboard(db: Session, dashboard_id: int) -> Dashboard | None:
    return db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()


def update_dashboard(db: Session, dashboard_id: int, **kwargs):
    dashboard = get_dashboard(db, dashboard_id)
    if dashboard:
        for key, value in kwargs.items():
            if hasattr(dashboard, key):
                if key == "config" and isinstance(value, dict):
                    value = json.dumps(value)
                setattr(dashboard, key, value)
        dashboard.updated_at = datetime.now(timezone.utc)
        db.commit()
        return True
    return False


def delete_dashboard(db: Session, dashboard_id: int):
    dashboard = get_dashboard(db, dashboard_id)
    if dashboard:
        db.delete(dashboard)
        db.commit()
