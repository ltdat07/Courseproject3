from datetime import datetime, timedelta, timezone
import unittest

from pydantic import TypeAdapter
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from app.database import Base, create_db_engine
from app.models import Attempt, User, UserSession
from app.schemas import UserResponse, UtcDateTime


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_db_engine("sqlite://")
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)

    def test_foreign_keys_are_enabled_on_new_connections(self):
        for _ in range(2):
            with self.engine.connect() as connection:
                self.assertEqual(connection.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)
            self.engine.dispose()

    def test_orphan_attempt_is_rejected(self):
        with self.assertRaises(IntegrityError):
            with self.engine.begin() as connection:
                connection.execute(insert(Attempt).values(
                    user_id=999, task_id=999, is_correct=True, earned_points=10,
                ))

    def test_deleting_user_removes_sessions(self):
        with self.engine.begin() as connection:
            connection.execute(insert(User).values(id=1, username="test_user"))
            connection.execute(insert(UserSession).values(
                token_hash="test-token", user_id=1, expires_at=datetime(2030, 1, 1),
            ))
            connection.execute(User.__table__.delete().where(User.id == 1))
            self.assertIsNone(connection.execute(select(UserSession.token_hash)).first())

    def test_sqlite_account_date_is_serialized_with_utc_timezone(self):
        with self.engine.begin() as connection:
            connection.execute(insert(User).values(
                id=1, username="test_user", created_at=datetime(2026, 9, 28, 12, 30),
            ))
            user = connection.execute(select(User.__table__)).mappings().one()
            self.assertEqual(
                UserResponse.model_validate(user).model_dump(mode="json")["created_at"],
                "2026-09-28T12:30:00Z",
            )

    def test_explicit_timezone_preserves_the_instant(self):
        value = datetime(2026, 9, 28, 15, 30, tzinfo=timezone(timedelta(hours=3)))
        adapter = TypeAdapter(UtcDateTime)
        self.assertEqual(adapter.validate_python(value), datetime(2026, 9, 28, 12, 30, tzinfo=timezone.utc))


if __name__ == "__main__":
    unittest.main()
