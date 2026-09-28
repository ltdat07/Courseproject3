"""Проверка ответов, начисление опыта и сохранение прогресса."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from app.models import Attempt, Task, Topic, User, UserTopicProgress
from app.schemas import AnswerRequest, AnswerResponse
from app.services.progress import (
    award_topic_achievement,
    get_topic_progress,
    has_completed_all_tasks,
)


def require_unlocked_progress(db: Session, user_id: int, topic_id: int) -> UserTopicProgress:
    progress = get_topic_progress(db, user_id, topic_id)
    if progress is not None:
        db.refresh(progress)
    if progress is None or not progress.is_unlocked:
        raise HTTPException(status_code=403, detail="Topic is locked")
    return progress


def _record_attempt(
    db: Session, user: User, task: Task, progress: UserTopicProgress,
    selected_option_id: int, is_correct: bool,
) -> int:
    previous_correct_attempt_id = db.scalar(
        select(Attempt.id).where(
            Attempt.user_id == user.id,
            Attempt.task_id == task.id,
            Attempt.is_correct.is_(True),
        ).limit(1)
    )
    earned_points = 10 if is_correct and previous_correct_attempt_id is None else 0
    db.add(Attempt(
        user_id=user.id, task_id=task.id, selected_option_id=selected_option_id,
        is_correct=is_correct, earned_points=earned_points,
    ))
    if earned_points:
        user.total_xp += earned_points
        progress.earned_points += earned_points
    db.flush()
    return earned_points


def _unlock_next_topic(db: Session, user_id: int, topic_id: int) -> int | None:
    current_topic = db.get(Topic, topic_id)
    next_topic = db.scalar(
        select(Topic).where(Topic.level > current_topic.level).order_by(Topic.level).limit(1)
    )
    if next_topic is None:
        return None
    next_progress = get_topic_progress(db, user_id, next_topic.id)
    if next_progress is None:
        db.add(UserTopicProgress(user_id=user_id, topic_id=next_topic.id, is_unlocked=True))
    elif not next_progress.is_unlocked:
        next_progress.is_unlocked = True
    return next_topic.id


def check_answer(task_id: int, answer: AnswerRequest, db: Session, user: User) -> AnswerResponse:
    try:
        # UPDATE получает блокировку записи до чтения наград, в том числе в SQLite.
        db.execute(
            update(User).where(User.id == user.id).values(total_xp=User.total_xp)
            .execution_options(synchronize_session=False)
        )
        db.refresh(user)
        task = db.scalar(
            select(Task).options(selectinload(Task.options)).where(Task.id == task_id)
        )
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if answer.selected_option_id not in {option.option_id for option in task.options}:
            raise HTTPException(status_code=422, detail="Option not found")

        is_correct = answer.selected_option_id == task.correct_option_id
        progress = require_unlocked_progress(db, user.id, task.topic_id)
        earned_points = _record_attempt(
            db, user, task, progress, answer.selected_option_id, is_correct,
        )
        completed_from_attempts = has_completed_all_tasks(db, user.id, task.topic_id)
        achievement_unlocked = None
        unlocked_topic_id = None
        if completed_from_attempts and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.now(timezone.utc)
            achievement_unlocked = award_topic_achievement(db, user.id, task.topic_id)
            unlocked_topic_id = _unlock_next_topic(db, user.id, task.topic_id)

        # Попытка, опыт, достижение и открытие главы сохраняются одной транзакцией.
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Attempt was not saved") from exc

    if is_correct and earned_points == 0:
        response_message = "Ответ верный. Награда за это задание уже получена."
    else:
        response_message = task.success_message if is_correct else task.error_message
    return AnswerResponse(
        is_correct=is_correct, message=response_message, explanation=task.explanation,
        earned_points=earned_points, total_xp=user.total_xp,
        topic_completed=progress.is_completed, achievement_unlocked=achievement_unlocked,
        unlocked_topic_id=unlocked_topic_id,
    )
