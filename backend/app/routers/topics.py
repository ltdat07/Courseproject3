from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_user
from app.database import get_db
from app.models import Task as TaskModel
from app.models import Topic as TopicModel
from app.models import User
from app.schemas import (
    AnswerRequest,
    AnswerResponse,
    TaskResponse,
    TopicDetailResponse,
    TopicSummaryResponse,
)
from app.services.training import check_answer, require_unlocked_progress

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/", response_model=list[TopicSummaryResponse])
def get_topics(db: Session = Depends(get_db)):
    return list(db.scalars(select(TopicModel).order_by(TopicModel.level)).all())


@router.get("/{topic_id}", response_model=TopicDetailResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    topic = db.scalar(
        select(TopicModel)
        .options(selectinload(TopicModel.achievement))
        .where(TopicModel.id == topic_id)
    )

    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    require_unlocked_progress(db, user.id, topic_id)

    return TopicDetailResponse(
        id=topic.id,
        title=topic.title,
        quest_title=topic.quest_title,
        description=topic.description,
        theory=topic.theory,
        level=topic.level,
        points=topic.points,
        achievement=topic.achievement.title if topic.achievement else None,
    )


@router.get("/{topic_id}/tasks", response_model=list[TaskResponse])
def get_topic_tasks(topic_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    if db.get(TopicModel, topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    require_unlocked_progress(db, user.id, topic_id)

    return list(
        db.scalars(
            select(TaskModel)
            .options(selectinload(TaskModel.options))
            .where(TaskModel.topic_id == topic_id)
            .order_by(TaskModel.id)
        ).all()
    )


@router.post("/tasks/{task_id}/check", response_model=AnswerResponse)
def check_task_answer(
    task_id: int, answer: AnswerRequest, db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    return check_answer(task_id, answer, db, user)
