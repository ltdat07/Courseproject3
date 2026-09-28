"""Запросы прогресса и выдача достижений. Транзакцией управляет вызывающий код."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Achievement, Attempt, Task, UserAchievement, UserTopicProgress


def get_topic_progress(db: Session, user_id: int, topic_id: int) -> UserTopicProgress | None:
    return db.scalar(select(UserTopicProgress).where(
        UserTopicProgress.user_id == user_id,
        UserTopicProgress.topic_id == topic_id,
    ))


def has_completed_all_tasks(db: Session, user_id: int, topic_id: int) -> bool:
    total_task_count = db.scalar(
        select(func.count(Task.id)).where(Task.topic_id == topic_id)
    ) or 0
    correct_task_count = db.scalar(
        select(func.count(func.distinct(Attempt.task_id)))
        .join(Task, Attempt.task_id == Task.id)
        .where(
            Attempt.user_id == user_id,
            Attempt.is_correct.is_(True),
            Task.topic_id == topic_id,
        )
    ) or 0
    return total_task_count > 0 and correct_task_count == total_task_count


def award_topic_achievement(db: Session, user_id: int, topic_id: int) -> str | None:
    achievement = db.scalar(select(Achievement).where(Achievement.topic_id == topic_id))
    if achievement and db.get(UserAchievement, (user_id, achievement.id)) is None:
        db.add(UserAchievement(user_id=user_id, achievement_id=achievement.id))
        return achievement.title
    return None
