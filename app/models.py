from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class PostType(StrEnum):
    STARTUP = "startup"
    VACANCY = "vacancy"


class PostStatus(StrEnum):
    PUBLISHED = "published"
    CLOSED = "closed"


class ResponseStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    posts: Mapped[list["Post"]] = relationship(back_populates="author")
    responses: Mapped[list["Response"]] = relationship(back_populates="applicant")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[PostType] = mapped_column(Enum(PostType), index=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text)
    looking_for: Mapped[str] = mapped_column(String(500))
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), default=PostStatus.PUBLISHED, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    author: Mapped[User] = relationship(back_populates="posts")
    responses: Mapped[list["Response"]] = relationship(back_populates="post", cascade="all, delete-orphan")


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (UniqueConstraint("post_id", "applicant_id", name="uq_response_post_applicant"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"), index=True)
    applicant_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    message: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ResponseStatus] = mapped_column(Enum(ResponseStatus), default=ResponseStatus.PENDING, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    post: Mapped[Post] = relationship(back_populates="responses")
    applicant: Mapped[User] = relationship(back_populates="responses")
