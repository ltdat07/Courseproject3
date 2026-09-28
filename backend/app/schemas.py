from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import AfterValidator, AliasChoices, BaseModel, ConfigDict, Field, field_validator


def as_utc(value: datetime) -> datetime:
    # SQLite возвращает даты без часового пояса, хотя сохраняем их в UTC.
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


UtcDateTime = Annotated[datetime, AfterValidator(as_utc)]


class OrmSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-z0-9_]+$")
    password: str = Field(min_length=12, max_length=128, repr=False)

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class Registration(Credentials):
    display_name: str = Field(min_length=1, max_length=60)

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Укажи имя героя")
        return value


class TaskOptionResponse(OrmSchema):
    id: int = Field(validation_alias=AliasChoices("option_id", "id"))
    text: str


class TaskResponse(OrmSchema):
    id: int
    topic_id: int
    story: str
    question: str
    type: str
    code: str | None = None
    options: list[TaskOptionResponse]


class TopicSummaryResponse(OrmSchema):
    id: int
    title: str
    quest_title: str
    description: str
    level: int
    points: int


class TopicDetailResponse(TopicSummaryResponse):
    theory: str
    achievement: str | None = None


class AnswerRequest(BaseModel):
    selected_option_id: int = Field(ge=1)


class AnswerResponse(BaseModel):
    is_correct: bool
    message: str
    explanation: str
    earned_points: int = Field(ge=0)
    total_xp: int = Field(ge=0)
    topic_completed: bool
    achievement_unlocked: str | None = None
    unlocked_topic_id: int | None = None


class UserResponse(OrmSchema):
    id: int
    username: str
    display_name: str | None
    total_xp: int
    created_at: UtcDateTime


class AchievementResponse(OrmSchema):
    id: int
    title: str
    description: str | None


class UserProgressResponse(BaseModel):
    total_xp: int = Field(ge=0)
    unlocked_topic_ids: list[int]
    completed_topic_ids: list[int]
    achievements: list[AchievementResponse]


class TopicAnalyticsResponse(BaseModel):
    topic_id: int
    title: str
    total_answers: int = Field(ge=0)
    correct_answers: int = Field(ge=0)
    accuracy_percent: float = Field(ge=0, le=100)
    is_weak: bool
    recommendation: str | None = None


class AttemptHistoryItemResponse(BaseModel):
    id: int
    task_id: int
    topic_id: int
    topic_title: str
    question: str
    selected_option_id: int | None
    is_correct: bool
    earned_points: int = Field(ge=0)
    created_at: UtcDateTime


class UserAnalyticsResponse(BaseModel):
    total_answers: int = Field(ge=0)
    correct_answers: int = Field(ge=0)
    accuracy_percent: float = Field(ge=0, le=100)
    weak_topic_count: int = Field(ge=0)
    topics: list[TopicAnalyticsResponse]
    recent_attempts: list[AttemptHistoryItemResponse]


class AiFeedbackStatusResponse(BaseModel):
    available: bool
    provider: str
    model: str | None = None
    message: str


class AiPracticeResponse(BaseModel):
    id: str
    topic_title: str
    title: str
    story: str
    assignment: str
    starter_code: str


class AiFeedbackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    practice_id: str = Field(min_length=1, max_length=80)
    student_solution: str = Field(min_length=12, max_length=8000)


class AiFeedbackContent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    verdict: Literal["correct", "partially_correct", "needs_revision"]
    summary: str = Field(min_length=1)
    strengths: list[str]
    issues: list[str]
    hints: list[str]
    suggested_fragment: str | None


class AiFeedbackResponse(AiFeedbackContent):
    model: str


class AiCriterionCheck(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    criterion: str
    is_met: bool
    explanation: str


class AiFeedbackDraft(BaseModel):
    """Ответ модели с проверкой критериев; клиенту передаётся только feedback."""

    model_config = ConfigDict(extra="forbid", strict=True)

    checks: list[AiCriterionCheck]
    feedback: AiFeedbackContent
