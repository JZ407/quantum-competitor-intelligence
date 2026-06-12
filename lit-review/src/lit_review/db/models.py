from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint,
    Table,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


paper_authors = Table(
    "paper_authors",
    Base.metadata,
    Column("paper_id", ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
    Column("position", Integer, nullable=False, default=1),
)

paper_tags = Table(
    "paper_tags",
    Base.metadata,
    Column("paper_id", ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Paper(Base):
    __tablename__ = "papers"
    __table_args__ = (
        UniqueConstraint("doi"),
        UniqueConstraint("arxiv_id"),
        CheckConstraint(
            "reading_status IN ('unread', 'reading', 'done')",
            name="ck_reading_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None] = mapped_column(Integer)
    journal: Mapped[str | None] = mapped_column(String(500))
    doi: Mapped[str | None] = mapped_column(String(200), unique=True)
    arxiv_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    reading_status: Mapped[str] = mapped_column(String(20), default="unread")
    notes: Mapped[str | None] = mapped_column(Text)
    pdf_path: Mapped[str | None] = mapped_column(String(1000))
    source: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    authors: Mapped[list["Author"]] = relationship(
        secondary=paper_authors, back_populates="papers", order_by="paper_authors.c.position"
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary=paper_tags, back_populates="papers"
    )

    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title[:60]}...')>"


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)

    papers: Mapped[list["Paper"]] = relationship(
        secondary=paper_authors, back_populates="authors"
    )

    def __repr__(self):
        return f"<Author(full_name='{self.full_name}')>"


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    papers: Mapped[list["Paper"]] = relationship(
        secondary=paper_tags, back_populates="tags"
    )

    def __repr__(self):
        return f"<Tag(name='{self.name}')>"


class Citation(Base):
    __tablename__ = "citations"
    __table_args__ = (
        UniqueConstraint("paper_id", "cited_paper_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )
    cited_paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )
    context_snippet: Mapped[str | None] = mapped_column(Text)


class ApiCache(Base):
    __tablename__ = "api_cache"
    __table_args__ = (
        UniqueConstraint("endpoint", "params_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)
    params_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_json: Mapped[str] = mapped_column(Text, nullable=False)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    ttl_seconds: Mapped[int] = mapped_column(Integer, default=86400)
