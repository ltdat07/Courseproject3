import os
from collections.abc import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import DEFAULT_DATABASE_URL


DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def create_db_engine(database_url: str) -> Engine:
    engine_options: dict[str, object] = {"pool_pre_ping": True}

    if make_url(database_url).get_backend_name() == "sqlite":
        engine_options["connect_args"] = {"check_same_thread": False}

        if make_url(database_url).database in {None, "", ":memory:"}:
            engine_options["poolclass"] = StaticPool

    db_engine = create_engine(database_url, **engine_options)
    if db_engine.dialect.name == "sqlite":
        @event.listens_for(db_engine, "connect")
        def enable_foreign_keys(connection, _):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return db_engine


engine = create_db_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Импорт регистрирует все ORM-модели в metadata перед созданием таблиц.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
