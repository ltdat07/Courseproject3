from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import COOKIE_NAME, DUMMY_HASH, auth_limiter, begin_session, end_session, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import Credentials, Registration, UserResponse
from app.seed import seed_user_progress

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: Registration, request: Request, response: Response, db: Session = Depends(get_db)):
    auth_limiter.check(request, data.username)
    if db.scalar(select(User.id).where(User.username == data.username)) is not None:
        raise HTTPException(409, "Этот логин уже занят.")
    user = User(username=data.username, display_name=data.display_name,
                password_hash=hash_password(data.password), total_xp=0)
    try:
        db.add(user)
        db.flush()
        seed_user_progress(db, user.id, commit=False)
    # Аккаунт и прогресс сохраняются вместе с сессией.
        begin_session(user, request, response, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Этот логин уже занят.") from None
    return user


@router.post("/login", response_model=UserResponse)
def login(data: Credentials, request: Request, response: Response, db: Session = Depends(get_db)):
    auth_limiter.check(request, data.username)
    user = db.scalar(select(User).where(User.username == data.username))
    encoded = user.password_hash if user and user.password_hash else DUMMY_HASH
    valid = verify_password(data.password, encoded)
    if not valid or user is None or not user.password_hash:
        raise HTTPException(401, "Неверный логин или пароль.")
    begin_session(user, request, response, db)
    return user


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    end_session(request, db)
    db.commit()
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, samesite="lax")
    response.headers["Cache-Control"] = "no-store"
