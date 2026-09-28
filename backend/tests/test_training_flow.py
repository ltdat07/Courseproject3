import asyncio
import json
import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import httpx
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import DEMO_USER_ID
from app.ai_practice_content import get_ai_practice
from app.auth import require_user
from app.database import Base, create_db_engine, get_db
from app.main import app
from app.models import (
    Achievement,
    Attempt,
    Task,
    TaskOption,
    Topic,
    User,
    UserAchievement,
    UserSession,
    UserTopicProgress,
)
from app.routers.topics import check_task_answer, get_topic_tasks
from app.routers.users import get_current_user_analytics
from app.schemas import AnswerRequest, TaskResponse
from app.seed import seed_demo_user, seed_learning_content, seed_user_progress


class TrainingFlowTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_db_engine("sqlite://")
        cls.session_factory = sessionmaker(
            bind=cls.engine,
            class_=Session,
            autoflush=False,
            expire_on_commit=False,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.dispose()

    def setUp(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.session_factory()
        seed_demo_user(self.db)
        seed_learning_content(self.db)
        seed_user_progress(self.db)
        self.user = self.db.get(User, DEMO_USER_ID)
        app.dependency_overrides[require_user] = lambda: self.user

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.db.close()

    def count_records(self, model: type[Base]) -> int:
        return self.db.scalar(select(func.count()).select_from(model)) or 0

    def answer(self, task_id: int, option_id: int):
        return check_task_answer(
            task_id,
            AnswerRequest(selected_option_id=option_id),
            self.db,
            self.user,
        )

    def database_snapshot(self):
        return {
            table.name: self.db.execute(
                select(table).order_by(*table.primary_key.columns)
            ).all()
            for table in Base.metadata.sorted_tables
        }

    def complete_topic(self, topic_id: int):
        tasks = get_topic_tasks(topic_id, self.db, self.user)
        return [self.answer(task.id, task.correct_option_id) for task in tasks]

    async def asgi_request(
        self, method: str, path: str, json_body: dict | None = None
    ) -> tuple[int, object]:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            headers={"Origin": "http://localhost:5173", "X-Trainer-Request": "1"},
        ) as client:
            response = await client.request(method, path, json=json_body)
        return response.status_code, response.json() if response.content else None

    def test_seed_is_idempotent_and_creates_expected_catalog(self) -> None:
        seed_demo_user(self.db)
        seed_learning_content(self.db)
        seed_user_progress(self.db)

        self.assertEqual(self.count_records(User), 1)
        self.assertEqual(self.count_records(Topic), 12)
        self.assertEqual(self.count_records(Task), 53)
        self.assertEqual(self.count_records(TaskOption), 212)
        self.assertEqual(self.count_records(Achievement), 12)
        self.assertEqual(self.count_records(UserTopicProgress), 12)

        progress = self.db.scalars(
            select(UserTopicProgress)
            .where(UserTopicProgress.user_id == DEMO_USER_ID)
            .order_by(UserTopicProgress.topic_id)
        ).all()
        self.assertEqual(
            [item.topic_id for item in progress if item.is_unlocked],
            [1],
        )

    def test_attempts_are_saved_and_xp_is_awarded_only_once(self) -> None:
        wrong = self.answer(1, 2)
        first_correct = self.answer(1, 1)
        repeated_correct = self.answer(1, 1)

        self.assertFalse(wrong.is_correct)
        self.assertEqual(wrong.earned_points, 0)
        self.assertEqual(first_correct.earned_points, 10)
        self.assertEqual(repeated_correct.earned_points, 0)
        self.assertEqual(repeated_correct.total_xp, 10)
        self.assertEqual(self.count_records(Attempt), 3)
        self.assertEqual(self.db.get(User, DEMO_USER_ID).total_xp, 10)

    def test_invalid_option_is_rejected_without_attempt(self) -> None:
        with self.assertRaises(HTTPException) as context:
            self.answer(1, 99)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(self.count_records(Attempt), 0)

    def test_locked_topic_opens_after_previous_topic_completion(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_topic_tasks(9, self.db, self.user)

        self.assertEqual(context.exception.status_code, 403)

        responses = [
            self.answer(task_id, option_id)
            for task_id, option_id in (
                (1, 1),
                (2, 1),
                (3, 1),
                (37, 3),
                (49, 2),
            )
        ]

        self.assertTrue(all(not response.topic_completed for response in responses[:-1]))
        self.assertTrue(responses[-1].topic_completed)
        self.assertEqual(responses[-1].unlocked_topic_id, 9)
        self.assertEqual(
            responses[-1].achievement_unlocked,
            "Гражданин королевства C#",
        )
        self.assertEqual(len(get_topic_tasks(9, self.db, self.user)), 4)

        first_progress = self.db.scalar(
            select(UserTopicProgress).where(
                UserTopicProgress.user_id == DEMO_USER_ID,
                UserTopicProgress.topic_id == 1,
            )
        )
        next_progress = self.db.scalar(
            select(UserTopicProgress).where(
                UserTopicProgress.user_id == DEMO_USER_ID,
                UserTopicProgress.topic_id == 9,
            )
        )

        self.assertTrue(first_progress.is_completed)
        self.assertEqual(first_progress.earned_points, 50)
        self.assertTrue(next_progress.is_unlocked)
        self.assertEqual(self.count_records(UserAchievement), 1)

        repeated = self.answer(3, 1)
        self.assertEqual(repeated.earned_points, 0)
        self.assertIsNone(repeated.achievement_unlocked)
        self.assertEqual(self.count_records(UserAchievement), 1)

    def test_analytics_detects_weak_topic_and_returns_history(self) -> None:
        empty = get_current_user_analytics(self.db, self.user)
        self.assertEqual(empty.total_answers, 0)
        self.assertEqual(empty.weak_topic_count, 0)
        self.assertEqual(len(empty.topics), 12)

        self.answer(1, 2)
        weak = get_current_user_analytics(self.db, self.user)

        self.assertEqual(weak.total_answers, 1)
        self.assertEqual(weak.correct_answers, 0)
        self.assertEqual(weak.accuracy_percent, 0)
        self.assertTrue(weak.topics[0].is_weak)
        self.assertEqual(weak.topics[0].recommendation, "Повтори эту тему")

        for task_id in (1, 2, 3):
            self.answer(task_id, 1)

        final = get_current_user_analytics(self.db, self.user)
        self.assertEqual(final.total_answers, 4)
        self.assertEqual(final.correct_answers, 3)
        self.assertEqual(final.accuracy_percent, 75)
        self.assertEqual(final.weak_topic_count, 0)
        self.assertEqual(len(final.recent_attempts), 4)
        self.assertEqual(final.recent_attempts[0].task_id, 3)

    def test_public_task_schema_does_not_expose_answer(self) -> None:
        task_records = get_topic_tasks(1, self.db, self.user)
        payload = [TaskResponse.model_validate(task).model_dump() for task in task_records]

        self.assertEqual(len(payload), 5)

        for task in payload:
            self.assertNotIn("correct_option_id", task)
            self.assertNotIn("success_message", task)
            self.assertNotIn("error_message", task)
            self.assertNotIn("explanation", task)
            self.assertEqual(len(task["options"]), 4)

    def test_fastapi_http_contract_uses_isolated_database(self) -> None:
        def override_get_db():
            yield self.db

        app.dependency_overrides[get_db] = override_get_db

        task_status, task_payload = asyncio.run(
            self.asgi_request("GET", "/topics/1/tasks")
        )
        locked_status, locked_payload = asyncio.run(
            self.asgi_request("GET", "/topics/9/tasks")
        )
        answer_status, answer_payload = asyncio.run(
            self.asgi_request(
                "POST",
                "/topics/tasks/1/check",
                {"selected_option_id": 1},
            )
        )

        self.assertEqual(task_status, 200)
        self.assertEqual(len(task_payload), 5)
        self.assertNotIn("correct_option_id", task_payload[0])
        self.assertNotIn("explanation", task_payload[0])
        self.assertEqual(locked_status, 403)
        self.assertEqual(locked_payload["detail"], "Topic is locked")
        self.assertEqual(answer_status, 200)
        self.assertTrue(answer_payload["is_correct"])
        self.assertEqual(answer_payload["earned_points"], 10)

    def test_theory_access_follows_chapter_unlocks(self) -> None:
        app.dependency_overrides[get_db] = lambda: self.db
        before = self.database_snapshot()

        status, payload = asyncio.run(self.asgi_request("GET", "/topics/1"))
        self.assertEqual(status, 200)
        self.assertTrue(payload["theory"])
        status, payload = asyncio.run(self.asgi_request("GET", "/topics/9"))
        self.assertEqual(status, 403)
        self.assertEqual(payload, {"detail": "Topic is locked"})
        status, _ = asyncio.run(self.asgi_request("GET", "/topics/999"))
        self.assertEqual(status, 404)
        self.assertEqual(self.database_snapshot(), before)

        self.complete_topic(1)
        status, payload = asyncio.run(self.asgi_request("GET", "/topics/9"))
        self.assertEqual(status, 200)
        self.assertEqual(payload["id"], 9)
        self.assertTrue(payload["theory"])
        self.assertEqual(asyncio.run(self.asgi_request("GET", "/topics/1"))[0], 200)

    def test_attempt_history_dates_include_utc_timezone(self) -> None:
        self.answer(1, 1)
        attempt = self.db.scalar(select(Attempt))
        attempt.created_at = datetime(2026, 9, 28, 12, 30)
        self.db.commit()
        self.db.expire_all()
        app.dependency_overrides[get_db] = lambda: self.db
        status, payload = asyncio.run(self.asgi_request("GET", "/users/me/analytics"))
        self.assertEqual(status, 200)
        self.assertEqual(payload["recent_attempts"][0]["created_at"], "2026-09-28T12:30:00Z")

    def test_expanded_course_has_ordered_detailed_chapters(self) -> None:
        topic_records = self.db.scalars(select(Topic).order_by(Topic.level)).all()

        self.assertEqual(
            [topic.id for topic in topic_records],
            [1, 9, 2, 3, 4, 10, 5, 11, 6, 12, 7, 8],
        )
        self.assertTrue(all(len(topic.theory) >= 900 for topic in topic_records))

        task_counts = dict(
            self.db.execute(
                select(Task.topic_id, func.count(Task.id)).group_by(Task.topic_id)
            ).all()
        )
        self.assertEqual(
            task_counts,
            {
                1: 5,
                2: 5,
                3: 5,
                4: 5,
                5: 5,
                6: 4,
                7: 4,
                8: 4,
                9: 4,
                10: 4,
                11: 4,
                12: 4,
            },
        )
        self.assertTrue(
            all(topic.points == task_counts[topic.id] * 10 for topic in topic_records)
        )

        for task in self.db.scalars(select(Task).order_by(Task.id)).all():
            option_ids = set(
                self.db.scalars(
                    select(TaskOption.option_id).where(TaskOption.task_id == task.id)
                ).all()
            )
            self.assertEqual(len(option_ids), 4)
            self.assertIn(task.correct_option_id, option_ids)

    def test_new_strings_chapter_can_be_completed(self) -> None:
        for task_id, option_id in (
            (1, 1),
            (2, 1),
            (3, 1),
            (37, 3),
            (49, 2),
        ):
            self.answer(task_id, option_id)

        first = self.answer(25, 2)
        second = self.answer(26, 4)
        third = self.answer(27, 3)
        fourth = self.answer(38, 2)

        self.assertFalse(first.topic_completed)
        self.assertFalse(second.topic_completed)
        self.assertFalse(third.topic_completed)
        self.assertTrue(fourth.topic_completed)
        self.assertEqual(fourth.unlocked_topic_id, 2)
        self.assertEqual(
            fourth.achievement_unlocked,
            "Переводчик Говорящих Рун",
        )

    def test_complete_course_preserves_order_rewards_and_repeat_answers(self) -> None:
        topic_ids = [1, 9, 2, 3, 4, 10, 5, 11, 6, 12, 7, 8]
        for index, topic_id in enumerate(topic_ids):
            with self.subTest(topic_id=topic_id):
                responses = self.complete_topic(topic_id)
                self.assertTrue(all(item.earned_points == 10 for item in responses))
                self.assertTrue(all(not item.topic_completed for item in responses[:-1]))
                self.assertTrue(responses[-1].topic_completed)
                self.assertIsNotNone(responses[-1].achievement_unlocked)
                self.assertEqual(
                    responses[-1].unlocked_topic_id,
                    topic_ids[index + 1] if index + 1 < len(topic_ids) else None,
                )

        self.assertEqual(self.user.total_xp, 530)
        self.assertEqual(self.count_records(Attempt), 53)
        self.assertEqual(self.count_records(UserAchievement), 12)
        self.assertTrue(all(
            item.is_unlocked and item.is_completed
            for item in self.db.scalars(select(UserTopicProgress)).all()
        ))
        for task in self.db.scalars(select(Task).order_by(Task.id)).all():
            response = self.answer(task.id, task.correct_option_id)
            self.assertEqual(response.earned_points, 0)
            self.assertIsNone(response.achievement_unlocked)
            self.assertIsNone(response.unlocked_topic_id)
        self.assertEqual(self.user.total_xp, 530)
        self.assertEqual(self.count_records(Attempt), 106)
        self.assertEqual(self.count_records(UserAchievement), 12)

    def test_reseeding_populated_database_preserves_all_saved_records(self) -> None:
        self.complete_topic(1)
        self.answer(25, 1)
        self.answer(25, 2)
        self.user.username = "claimed_owner"
        self.user.display_name = "Сохранённый герой"
        self.user.password_hash = "existing-password-hash"
        self.db.add(UserSession(
            token_hash="a" * 64, user_id=self.user.id,
            expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        ))
        # Сохранённое прохождение главы не должно сбрасываться при неполной истории попыток.
        progress = {
            item.topic_id: item
            for item in self.db.scalars(select(UserTopicProgress)).all()
        }
        progress[2].is_completed = True
        progress[2].is_unlocked = True
        progress[2].completed_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        progress[3].is_unlocked = True
        progress[8].is_unlocked = True
        achievement = self.db.scalar(select(Achievement).where(Achievement.topic_id == 2))
        self.db.add(UserAchievement(user_id=self.user.id, achievement_id=achievement.id))
        self.db.commit()
        before = self.database_snapshot()

        for _ in range(2):
            seed_demo_user(self.db)
            seed_learning_content(self.db)
            seed_user_progress(self.db)
            self.assertEqual(self.database_snapshot(), before)

    def test_failed_answer_commit_rolls_back_attempt_reward_and_unlocks(self) -> None:
        tasks = get_topic_tasks(1, self.db, self.user)
        for task in tasks[:-1]:
            self.answer(task.id, task.correct_option_id)
        before = self.database_snapshot()
        with patch.object(self.db, "commit", side_effect=RuntimeError("storage failure")):
            with self.assertRaises(HTTPException) as context:
                self.answer(tasks[-1].id, tasks[-1].correct_option_id)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Attempt was not saved")
        self.assertEqual(self.database_snapshot(), before)
        response = self.answer(tasks[-1].id, tasks[-1].correct_option_id)
        self.assertEqual(response.total_xp, 50)
        self.assertEqual(response.unlocked_topic_id, 9)

    def test_ai_analysis_does_not_change_database_or_progress(self) -> None:
        self.complete_topic(1)
        before = self.database_snapshot()
        practice = get_ai_practice("safe_division")
        draft = {
            "checks": [
                {"criterion": criterion, "is_met": True, "explanation": "Выполнено."}
                for criterion in practice["evaluation_criteria"]
            ],
            "feedback": {
                "verdict": "correct", "summary": "Требования выполнены.",
                "strengths": [], "issues": [], "hints": [], "suggested_fragment": None,
            },
        }

        def respond(request):
            return httpx.Response(200, json={"choices": [{
                "message": {"content": json.dumps(draft)}, "finish_reason": "stop",
            }]})

        def override_get_db():
            yield self.db

        app.dependency_overrides[get_db] = override_get_db
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "test-only-key", "GROQ_MODEL": "qwen/qwen3.8-27b",
            "GROQ_FREE_PLAN_CONFIRMED": "true",
        }), patch("app.services.ai_feedback.Client", side_effect=lambda **kwargs: httpx.Client(
            transport=httpx.MockTransport(respond), **kwargs,
        )):
            status, payload = asyncio.run(self.asgi_request("POST", "/ai-feedback/analyze", {
                "practice_id": practice["id"], "student_solution": practice["reference_solution"],
            }))
        self.assertEqual(status, 200)
        self.assertEqual(payload["verdict"], "correct")
        self.assertEqual(self.database_snapshot(), before)


if __name__ == "__main__":
    unittest.main()
