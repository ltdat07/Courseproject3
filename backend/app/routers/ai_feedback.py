from fastapi import APIRouter, Depends, HTTPException

from app.ai_practice_content import get_ai_practice, get_public_ai_practices
from app.auth import require_user
from app.schemas import (
    AiFeedbackRequest,
    AiFeedbackResponse,
    AiFeedbackStatusResponse,
    AiPracticeResponse,
)
from app.services.ai_feedback import (
    AiFeedbackBusy,
    AiFeedbackProviderError,
    AiFeedbackRateLimited,
    AiFeedbackUnavailable,
    generate_ai_feedback,
    get_cloud_ai_status,
)

router = APIRouter(prefix="/ai-feedback", tags=["ai-feedback"], dependencies=[Depends(require_user)])


@router.get("/status", response_model=AiFeedbackStatusResponse)
def get_ai_feedback_status() -> AiFeedbackStatusResponse:
    return get_cloud_ai_status()


@router.get("/practices", response_model=list[AiPracticeResponse])
def get_ai_practices() -> list[dict[str, object]]:
    return get_public_ai_practices()


@router.post("/analyze", response_model=AiFeedbackResponse)
def analyze_ai_solution(request: AiFeedbackRequest) -> AiFeedbackResponse:
    practice = get_ai_practice(request.practice_id)

    if practice is None:
        raise HTTPException(status_code=404, detail="Практическое задание не найдено.")

    try:
        return generate_ai_feedback(practice, request.student_solution)
    except AiFeedbackRateLimited as exc:
        raise HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": str(exc.retry_after)}) from exc
    except AiFeedbackBusy as exc:
        raise HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": "3"}) from exc
    except AiFeedbackUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AiFeedbackProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
