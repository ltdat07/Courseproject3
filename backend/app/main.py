from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.database import SessionLocal, init_db
from app.auth import allowed_origins, require_same_origin
from app.models import User
from app.routers import ai_feedback, auth, topics, users
from app.seed import seed_demo_user, seed_learning_content, seed_user_progress


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()

    with SessionLocal() as db:
        seed_demo_user(db)
        seed_learning_content(db)
        for user_id in db.scalars(select(User.id)).all():
            seed_user_progress(db, user_id)

    yield


app = FastAPI(
    title="C# Interactive Trainer API",
    description="Backend API for interactive C# trainer with gamification",
    version="0.1.0",
    lifespan=lifespan,
    dependencies=[Depends(require_same_origin)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins()),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics.router)
app.include_router(users.router)
app.include_router(ai_feedback.router)
app.include_router(auth.router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError):
    # Не возвращаем введённые данные в ошибке: среди них может быть пароль.
    return JSONResponse(status_code=422, content={"detail": [
        {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]})


@app.middleware("http")
async def private_response_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "C# Interactive Trainer API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
