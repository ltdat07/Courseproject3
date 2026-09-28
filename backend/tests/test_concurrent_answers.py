from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
import unittest

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.config import DEMO_USER_ID
from app.database import Base, create_db_engine
from app.models import Attempt, Task, User, UserAchievement, UserTopicProgress
from app.schemas import AnswerRequest
from app.seed import seed_demo_user, seed_learning_content, seed_user_progress
from app.services.training import check_answer


class ConcurrentAnswersTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        database = Path(self.directory.name) / "training.db"
        self.engine = create_db_engine("sqlite:///" + database.as_posix())
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        with self.sessions() as db:
            seed_demo_user(db)
            seed_learning_content(db)
            seed_user_progress(db)

    def answer_together(self, task_ids):
        ready = Barrier(len(task_ids))

        def answer(task_id):
            with self.sessions() as db:
                user = db.get(User, DEMO_USER_ID)
                task = db.get(Task, task_id)
                progress = db.scalar(select(UserTopicProgress).where(
                    UserTopicProgress.user_id == user.id, UserTopicProgress.topic_id == task.topic_id,
                ))
                self.assertIsNotNone(progress)
                ready.wait(timeout=10)
                return check_answer(task_id, AnswerRequest(selected_option_id=task.correct_option_id), db, user)

        with ThreadPoolExecutor(max_workers=len(task_ids)) as pool:
            return list(pool.map(answer, task_ids))

    def assert_rewards(self, expected_xp, attempts):
        with self.sessions() as db:
            self.assertEqual(db.get(User, DEMO_USER_ID).total_xp, expected_xp)
            self.assertEqual(db.scalar(select(func.sum(Attempt.earned_points))), expected_xp)
            self.assertEqual(db.scalar(select(func.count(Attempt.id))), attempts)
            self.assertEqual(db.scalar(select(UserTopicProgress.earned_points).where(
                UserTopicProgress.user_id == DEMO_USER_ID, UserTopicProgress.topic_id == 1,
            )), expected_xp)

    def test_different_tasks_do_not_lose_xp(self):
        responses = self.answer_together([1, 2])
        self.assertEqual([item.earned_points for item in responses], [10, 10])
        self.assertEqual(sorted(item.total_xp for item in responses), [10, 20])
        self.assert_rewards(20, 2)

    def test_repeated_task_awards_xp_once(self):
        responses = self.answer_together([1, 1])
        self.assertEqual(sorted(item.earned_points for item in responses), [0, 10])
        self.assert_rewards(10, 2)

    def test_last_answers_award_one_achievement_and_unlock_next_chapter(self):
        with self.sessions() as db:
            user = db.get(User, DEMO_USER_ID)
            for task_id in [1, 2, 3]:
                check_answer(task_id, AnswerRequest(selected_option_id=1), db, user)
        responses = self.answer_together([37, 49])
        self.assert_rewards(50, 5)
        self.assertEqual(sum(item.achievement_unlocked is not None for item in responses), 1)
        with self.sessions() as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(UserAchievement)), 1)
            self.assertTrue(db.scalar(select(UserTopicProgress.is_unlocked).where(
                UserTopicProgress.user_id == DEMO_USER_ID, UserTopicProgress.topic_id == 9,
            )))


if __name__ == "__main__":
    unittest.main()
