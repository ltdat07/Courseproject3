from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    attempts: Mapped[list[Attempt]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    topic_progress: Mapped[list[UserTopicProgress]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[list[UserAchievement]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserSession(Base):
    __tablename__ = "user_sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), unique=True)
    quest_title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    theory: Mapped[str] = mapped_column(Text)
    level: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    points: Mapped[int] = mapped_column(Integer, default=30)

    tasks: Mapped[list[Task]] = relationship(
        back_populates="topic", cascade="all, delete-orphan", order_by="Task.id"
    )
    achievement: Mapped[Achievement | None] = relationship(
        back_populates="topic", cascade="all, delete-orphan", uselist=False
    )
    user_progress: Mapped[list[UserTopicProgress]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True
    )
    story: Mapped[str] = mapped_column(Text)
    question: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50))
    code: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_option_id: Mapped[int] = mapped_column(Integer)
    success_message: Mapped[str] = mapped_column(Text)
    error_message: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)

    topic: Mapped[Topic] = relationship(back_populates="tasks")
    options: Mapped[list[TaskOption]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskOption.option_id",
    )
    attempts: Mapped[list[Attempt]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class TaskOption(Base):
    __tablename__ = "task_options"
    __table_args__ = (
        UniqueConstraint("task_id", "option_id", name="uq_task_option_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), index=True
    )
    option_id: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)

    task: Mapped[Task] = relationship(back_populates="options")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), index=True
    )
    selected_option_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    student_solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    earned_points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    user: Mapped[User] = relationship(back_populates="attempts")
    task: Mapped[Task] = relationship(back_populates="attempts")


class UserTopicProgress(Base):
    __tablename__ = "user_topic_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic_progress"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True
    )
    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    earned_points: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[User] = relationship(back_populates="topic_progress")
    topic: Mapped[Topic] = relationship(back_populates="user_progress")


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), unique=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    topic: Mapped[Topic | None] = relationship(back_populates="achievement")
    users: Mapped[list[UserAchievement]] = relationship(
        back_populates="achievement", cascade="all, delete-orphan"
    )


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True
    )
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="achievements")
    achievement: Mapped[Achievement] = relationship(back_populates="users")
