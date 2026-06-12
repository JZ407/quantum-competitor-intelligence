"""SQLAlchemy ORM models for the Data Projection platform."""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float,
    create_engine, event
)
from sqlalchemy.orm import DeclarativeBase, relationship, Session
from dataprojection.config import PLATFORM_DB_PATH


class Base(DeclarativeBase):
    pass


# ── Users ── (Phase 2, single-user for MVP)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    email = Column(String(255))
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime)

    conversations = relationship("Conversation", back_populates="user")
    dashboards = relationship("Dashboard", back_populates="user")


# ── Conversations & Messages ──

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200))
    system_prompt = Column(Text)  # snapshot for reproducibility
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation",
                          order_by="Message.id")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, tool_result, system
    content = Column(Text, nullable=False)

    # Tool call metadata
    tool_name = Column(String(50))
    tool_input = Column(Text)       # JSON
    tool_result_id = Column(String(64))

    # Embedded chart
    has_chart = Column(Boolean, default=False)
    chart_spec = Column(Text)       # JSON: Vega-Lite spec
    chart_type = Column(String(20)) # "altair" or "plotly"

    # Dashboard reference
    has_dashboard = Column(Boolean, default=False)
    dashboard_id = Column(Integer)

    # Token tracking
    token_count = Column(Integer)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")


# ── Dashboards ── (Phase 2+)

class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    config = Column(Text, nullable=False, default="{}")  # JSON layout
    thumbnail_path = Column(String(500))
    is_published = Column(Boolean, default=False)
    source_conversation_id = Column(Integer, ForeignKey("conversations.id"))
    fork_of = Column(Integer, ForeignKey("dashboards.id"))
    fork_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="dashboards")


# ── Engine & Session ──

engine = create_engine(
    f"sqlite:///{PLATFORM_DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,
)

# Enable WAL mode for concurrent reads
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_session() -> Session:
    """Create a new database session."""
    return Session(engine)


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)
