"""Назначает логин и пароль существующему профилю с сохранением прогресса."""
from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select

from app.auth import hash_password
from app.config import DEMO_USER_ID
from app.database import SessionLocal, init_db
from app.models import User
from app.schemas import Registration


def claim_profile(db, data: Registration) -> None:
    user = db.get(User, DEMO_USER_ID)
    if user is None or user.password_hash:
        raise ValueError("Прежний профиль не найден или уже защищён паролем.")
    if db.scalar(select(User.id).where(User.username == data.username, User.id != user.id)):
        raise ValueError("Логин занят. Выбери другой: прогресс принадлежит прежнему профилю.")
    user.username = data.username
    user.display_name = data.display_name
    user.password_hash = hash_password(data.password)
    db.commit()


def main() -> None:
    print("Личный аккаунт на основе прежнего профиля. Баллы и история сохранятся.")
    username = input("Логин (3–30 латинских букв, цифр или _): ")
    name = input("Имя героя: ")
    password = getpass("Пароль (12–128 символов, ввод скрыт): ")
    if password != getpass("Повтори пароль: "):
        raise SystemExit("Пароли не совпали. Изменений нет.")
    try:
        data = Registration(username=username, display_name=name, password=password)
    except ValidationError:
        raise SystemExit("Проверь логин, имя героя и длину пароля. Изменений нет.") from None
    init_db()
    with SessionLocal() as db:
        try:
            claim_profile(db, data)
        except ValueError as exc:
            raise SystemExit(str(exc)) from None
    print("Готово. Войди в тренажёр с новым логином. Прежний прогресс сохранён.")


if __name__ == "__main__":
    main()
