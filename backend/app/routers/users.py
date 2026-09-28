from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.auth import require_user
from app.database import get_db
from app.models import (
    Achievement,
    Attempt,
    Task,
    Topic,
    User,
    UserAchievement,
    UserTopicProgress,
)
from app.schemas import (
    AttemptHistoryItemResponse,
    TopicAnalyticsResponse,
    UserAnalyticsResponse,
    UserProgressResponse,
    UserResponse,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user(user: User = Depends(require_user)):
    return user


@router.get("/me/progress", response_model=UserProgressResponse)
def get_current_user_progress(db: Session = Depends(get_db), user: User = Depends(require_user)):
    progress_records = db.scalars(
        select(UserTopicProgress)
        .where(UserTopicProgress.user_id == user.id)
        .order_by(UserTopicProgress.topic_id)
    ).all()
    achievement_records = db.scalars(
        select(Achievement)
        .join(
            UserAchievement,
            UserAchievement.achievement_id == Achievement.id,
        )
        .where(UserAchievement.user_id == user.id)
        .order_by(Achievement.id)
    ).all()

    return UserProgressResponse(
        total_xp=user.total_xp,
        unlocked_topic_ids=[
            progress.topic_id for progress in progress_records if progress.is_unlocked
        ],
        completed_topic_ids=[
            progress.topic_id for progress in progress_records if progress.is_completed
        ],
        achievements=list(achievement_records),
    )


@router.get("/me/analytics", response_model=UserAnalyticsResponse)
def get_current_user_analytics(db: Session = Depends(get_db), user: User = Depends(require_user)):
    topic_records = db.scalars(select(Topic).order_by(Topic.level)).all()
    statistic_rows = db.execute(
        select(
            Task.topic_id,
            func.count(Attempt.id),
            func.sum(case((Attempt.is_correct.is_(True), 1), else_=0)),
        )
        .join(Task, Attempt.task_id == Task.id)
        .where(Attempt.user_id == user.id)
        .group_by(Task.topic_id)
    ).all()
    statistics_by_topic = {
        topic_id: (total_answers, correct_answers or 0)
        for topic_id, total_answers, correct_answers in statistic_rows
    }

    topic_analytics = []

    for topic in topic_records:
        total_answers, correct_answers = statistics_by_topic.get(topic.id, (0, 0))
        accuracy_percent = (
            round(correct_answers / total_answers * 100, 1) if total_answers else 0.0
        )
        is_weak = total_answers > 0 and accuracy_percent < 60

        topic_analytics.append(
            TopicAnalyticsResponse(
                topic_id=topic.id,
                title=topic.title,
                total_answers=total_answers,
                correct_answers=correct_answers,
                accuracy_percent=accuracy_percent,
                is_weak=is_weak,
                recommendation="Повтори эту тему" if is_weak else None,
            )
        )

    total_answers = sum(topic.total_answers for topic in topic_analytics)
    correct_answers = sum(topic.correct_answers for topic in topic_analytics)
    accuracy_percent = (
        round(correct_answers / total_answers * 100, 1) if total_answers else 0.0
    )
    recent_rows = db.execute(
        select(Attempt, Task, Topic)
        .join(Task, Attempt.task_id == Task.id)
        .join(Topic, Task.topic_id == Topic.id)
        .where(Attempt.user_id == user.id)
        .order_by(Attempt.created_at.desc(), Attempt.id.desc())
        .limit(10)
    ).all()
    recent_attempts = [
        AttemptHistoryItemResponse(
            id=attempt.id,
            task_id=task.id,
            topic_id=topic.id,
            topic_title=topic.title,
            question=task.question,
            selected_option_id=attempt.selected_option_id,
            is_correct=attempt.is_correct,
            earned_points=attempt.earned_points,
            created_at=attempt.created_at,
        )
        for attempt, task, topic in recent_rows
    ]

    return UserAnalyticsResponse(
        total_answers=total_answers,
        correct_answers=correct_answers,
        accuracy_percent=accuracy_percent,
        weak_topic_count=sum(topic.is_weak for topic in topic_analytics),
        topics=topic_analytics,
        recent_attempts=recent_attempts,
    )
