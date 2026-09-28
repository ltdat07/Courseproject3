import hashlib
import hmac
import os
import secrets
import time
from collections import OrderedDict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserSession

COOKIE_NAME = "trainer_session"
SESSION_SECONDS = 7 * 24 * 60 * 60
SCRYPT_N, SCRYPT_R, SCRYPT_P = 32768, 8, 3


def allowed_origins() -> set[str]:
    return {origin.strip().rstrip("/") for origin in os.getenv(
        "AUTH_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",") if origin.strip()}


def require_same_origin(request: Request) -> None:
    # Проверяем Origin и заголовок для защиты от CSRF, в том числе при входе и выходе.
    if request.method not in {"GET", "HEAD", "OPTIONS"} and (
        request.headers.get("origin") not in allowed_origins()
        or request.headers.get("x-trainer-request") != "1"
    ):
        raise HTTPException(403, "Запрос отклонён. Открой тренажёр по разрешённому адресу.")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    key = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=SCRYPT_N,
                         r=SCRYPT_R, p=SCRYPT_P, maxmem=64 * 1024 * 1024, dklen=32)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${key.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded.split("$")
        if (algorithm, int(n), int(r), int(p)) != ("scrypt", SCRYPT_N, SCRYPT_R, SCRYPT_P):
            return False
        actual = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt),
                                n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P,
                                maxmem=64 * 1024 * 1024, dklen=32)
        return hmac.compare_digest(actual, bytes.fromhex(expected))
    except (ValueError, TypeError):
        return False


DUMMY_HASH = hash_password(secrets.token_urlsafe(32))


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME, "")
    if not token or len(token) > 128:
        raise HTTPException(401, "Войди в аккаунт, чтобы продолжить.")
    user = db.scalar(select(User).join(UserSession, UserSession.user_id == User.id).where(
        UserSession.token_hash == token_digest(token),
        UserSession.expires_at > datetime.now(timezone.utc),
        User.password_hash.is_not(None),
    ))
    if user is None:
        raise HTTPException(401, "Сессия закончилась. Войди снова.")
    expected_user = request.headers.get("x-trainer-user")
    if expected_user is not None and expected_user != str(user.id):
        raise HTTPException(401, "В другой вкладке сменился аккаунт. Войди снова.")
    return user


def end_session(request: Request, db: Session) -> None:
    token = request.cookies.get(COOKIE_NAME, "")
    if token and len(token) <= 128:
        db.execute(delete(UserSession).where(UserSession.token_hash == token_digest(token)))


def begin_session(user: User, request: Request, response: Response, db: Session) -> None:
    """Сохраняет сессию и данные регистрации перед установкой cookie."""
    end_session(request, db)
    now = datetime.now(timezone.utc)
    db.execute(delete(UserSession).where(UserSession.expires_at <= now))
    token = secrets.token_urlsafe(32)
    db.add(UserSession(token_hash=token_digest(token), user_id=user.id,
                       expires_at=now + timedelta(seconds=SESSION_SECONDS)))
    db.commit()
    response.set_cookie(COOKIE_NAME, token, max_age=SESSION_SECONDS, httponly=True,
                        secure=os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true",
                        samesite="lax", path="/")
    response.headers["Cache-Control"] = "no-store"


class AuthLimiter:
    """Ограничивает попытки входа по IP и логину в пределах одного процесса."""
    def __init__(self):
        self.lock = Lock()
        self.entries: OrderedDict[str, deque[float]] = OrderedDict()

    def check(self, request: Request, username: str) -> None:
        now = time.monotonic()
        ip = request.client.host if request.client else "unknown"
        with self.lock:
            for key, limit in (("ip:" + ip, 30), ("user:" + username, 10)):
                bucket = self.entries.setdefault(key, deque())
                while bucket and bucket[0] <= now - 900:
                    bucket.popleft()
                if len(bucket) >= limit:
                    raise HTTPException(429, "Слишком много попыток входа. Попробуй через 15 минут.",
                                        headers={"Retry-After": "900"})
            for key in ("ip:" + ip, "user:" + username):
                self.entries[key].append(now)
                self.entries.move_to_end(key)
            while len(self.entries) > 5000:
                self.entries.popitem(last=False)


auth_limiter = AuthLimiter()
