from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import DEMO_DISPLAY_NAME, DEMO_USER_ID, DEMO_USERNAME
from app.models import (
    Achievement,
    Attempt,
    Task,
    TaskOption,
    Topic,
    User,
    UserTopicProgress,
)
from app.practice_content import TASKS
from app.course_content import TOPICS
from app.services.progress import award_topic_achievement, get_topic_progress, has_completed_all_tasks


def seed_demo_user(db: Session) -> None:
    """Сохраняет прежний профиль; после назначения пароля не меняет его имя."""
    try:
        user = db.get(User, DEMO_USER_ID)

        if user is None:
            user = User(id=DEMO_USER_ID, username=DEMO_USERNAME,
                        display_name=DEMO_DISPLAY_NAME, total_xp=0)
            db.add(user)

        db.commit()
    except Exception:
        db.rollback()
        raise


def seed_learning_content(db: Session) -> None:
    """Создаёт или обновляет учебный контент без дублирования записей."""
    try:
        # Временные уровни позволяют переставить главы без конфликта уникальности.
        # ID остаются прежними, чтобы сохранить связи с попытками и прогрессом.
        stored_topics = db.scalars(select(Topic)).all()
        for stored_topic in stored_topics:
            stored_topic.level = 1000 + stored_topic.id
        db.flush()

        for topic_data in TOPICS:
            topic = db.get(Topic, topic_data["id"])

            if topic is None:
                topic = Topic(id=topic_data["id"])
                db.add(topic)

            topic.title = topic_data["title"]
            topic.quest_title = topic_data["quest_title"]
            topic.description = topic_data["description"]
            topic.theory = topic_data["theory"]
            topic.level = topic_data["level"]
            topic.points = topic_data["points"]

            achievement = db.scalar(
                select(Achievement).where(Achievement.topic_id == topic_data["id"])
            )

            if achievement is None:
                achievement = Achievement(topic_id=topic_data["id"])
                db.add(achievement)

            achievement.title = topic_data["achievement"]
            achievement.description = (
                f"Награда за прохождение главы «{topic_data['title']}»."
            )

        db.flush()

        for task_data in TASKS:
            task = db.get(Task, task_data["id"])

            if task is None:
                task = Task(id=task_data["id"])
                db.add(task)

            task.topic_id = task_data["topic_id"]
            task.story = task_data["story"]
            task.question = task_data["question"]
            task.type = task_data["type"]
            task.code = task_data.get("code")
            task.correct_option_id = task_data["correct_option_id"]
            task.success_message = task_data["success_message"]
            task.error_message = task_data["error_message"]
            task.explanation = task_data["explanation"]

            existing_options = {
                option.option_id: option
                for option in db.scalars(
                    select(TaskOption).where(TaskOption.task_id == task_data["id"])
                ).all()
            }

            for option_data in task_data["options"]:
                option = existing_options.get(option_data["id"])

                if option is None:
                    option = TaskOption(
                        task_id=task_data["id"], option_id=option_data["id"]
                    )
                    db.add(option)

                option.text = option_data["text"]

        db.commit()
    except Exception:
        db.rollback()
        raise


def seed_user_progress(db: Session, user_id: int = DEMO_USER_ID, *, commit: bool = True) -> None:
    """Создаёт прогресс по главам и восстанавливает его из сохранённых попыток."""
    try:
        previous_topic_completed = True
        topic_records = db.scalars(select(Topic).order_by(Topic.level)).all()

        for topic in topic_records:
            progress = get_topic_progress(db, user_id, topic.id)

            if progress is None:
                progress = UserTopicProgress(
                    user_id=user_id,
                    topic_id=topic.id,
                    is_unlocked=topic.level == 1,
                )
                db.add(progress)

            completed_from_attempts = has_completed_all_tasks(db, user_id, topic.id)
            attempt_count = db.scalar(
                select(func.count(Attempt.id))
                .join(Task, Attempt.task_id == Task.id)
                .where(
                    Attempt.user_id == user_id,
                    Task.topic_id == topic.id,
                )
            ) or 0
            earned_points = db.scalar(
                select(func.coalesce(func.sum(Attempt.earned_points), 0))
                .join(Task, Attempt.task_id == Task.id)
                .where(
                    Attempt.user_id == user_id,
                    Task.topic_id == topic.id,
                )
            ) or 0

            progress.is_completed = progress.is_completed or completed_from_attempts
            progress.is_unlocked = (
                progress.is_unlocked
                or topic.level == 1
                or previous_topic_completed
                or attempt_count > 0
            )
            progress.earned_points = earned_points

            if progress.is_completed and progress.completed_at is None:
                progress.completed_at = datetime.now(timezone.utc)

            if progress.is_completed:
                award_topic_achievement(db, user_id, topic.id)

            previous_topic_completed = progress.is_completed

        if commit:
            db.commit()
    except Exception:
        db.rollback()
        raise
