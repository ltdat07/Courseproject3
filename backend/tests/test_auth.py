import asyncio
import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.auth import COOKIE_NAME, auth_limiter, hash_password, token_digest, verify_password
from app.database import Base, create_db_engine, get_db
from app.main import app
from app.models import Attempt, User, UserSession, UserTopicProgress
from app.schemas import Registration
from app.seed import seed_demo_user, seed_learning_content, seed_user_progress
from scripts.claim_demo_account import claim_profile

PASSWORD = "Only-for-local-tests-2026"


class AccountsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_db_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine, class_=Session, expire_on_commit=False)()
        seed_demo_user(self.db)
        seed_learning_content(self.db)
        seed_user_progress(self.db)
        app.dependency_overrides.clear()
        def override_db():
            yield self.db
        app.dependency_overrides[get_db] = override_db
        auth_limiter.entries.clear()
        self.cookies = httpx.Cookies()
        self.settings = patch.dict(os.environ, {
            "AUTH_COOKIE_SECURE": "false", "AUTH_ALLOWED_ORIGINS": "http://localhost:5173",
        })
        self.settings.start()

    def tearDown(self):
        self.settings.stop()
        app.dependency_overrides.clear()
        auth_limiter.entries.clear()
        self.db.close()
        self.engine.dispose()

    def request(self, method, path, body=None, headers=None):
        async def send():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://testserver",
                cookies=self.cookies,
                headers=headers if headers is not None else {
                    "Origin": "http://localhost:5173", "X-Trainer-Request": "1",
                },
            ) as client:
                response = await client.request(method, path, json=body)
                self.cookies = client.cookies
                return response
        return asyncio.run(send())

    def register(self, username="alice"):
        return self.request("POST", "/auth/register", {
            "username": username, "display_name": "Герой " + username, "password": PASSWORD,
        })

    def login(self, username="alice", password=PASSWORD):
        return self.request("POST", "/auth/login", {"username": username, "password": password})

    def test_registration_hashes_password_and_creates_private_progress(self):
        response = self.register(" Alice ")
        self.assertEqual(response.status_code, 201)
        account = response.json()
        self.assertEqual(account["username"], "alice")
        self.assertEqual(account["total_xp"], 0)
        self.assertNotIn("password_hash", account)
        self.assertNotIn(PASSWORD, response.text)
        user = self.db.get(User, account["id"])
        self.assertNotEqual(user.password_hash, PASSWORD)
        self.assertTrue(verify_password(PASSWORD, user.password_hash))
        cookie = response.headers["set-cookie"].lower()
        self.assertIn("httponly", cookie)
        self.assertIn("samesite=lax", cookie)
        self.assertIn("max-age=604800", cookie)
        token = self.cookies.get(COOKIE_NAME)
        session = self.db.get(UserSession, token_digest(token))
        self.assertEqual(session.user_id, account["id"])
        self.assertNotEqual(session.token_hash, token)
        progress = self.request("GET", "/users/me/progress").json()
        self.assertEqual(progress["unlocked_topic_ids"], [1])
        self.assertEqual(progress["achievements"], [])
        self.assertEqual(self.db.scalar(select(func.count()).select_from(UserTopicProgress)), 24)

    def test_password_hashes_use_independent_salts_and_verify(self):
        first, second = hash_password(PASSWORD), hash_password(PASSWORD)
        self.assertNotEqual(first, second)
        self.assertTrue(verify_password(PASSWORD, first))
        self.assertFalse(verify_password("wrong password", first))
        self.assertFalse(verify_password(PASSWORD, "broken"))

    def test_guest_cannot_read_progress_answer_or_use_cloud(self):
        with patch("app.services.ai_feedback.Client") as provider:
            for method, path, body in (
                ("GET", "/users/me", None), ("GET", "/users/me/progress", None),
                ("GET", "/users/me/analytics", None), ("GET", "/topics/1/tasks", None),
                ("GET", "/topics/1", None), ("GET", "/topics/9", None),
                ("POST", "/topics/tasks/1/check", {"selected_option_id": 1}),
                ("GET", "/ai-feedback/status", None), ("GET", "/ai-feedback/practices", None),
                ("POST", "/ai-feedback/analyze", {"practice_id": "safe_division", "student_solution": "return a / b;"}),
            ):
                with self.subTest(path=path):
                    self.assertEqual(self.request(method, path, body).status_code, 401)
            provider.assert_not_called()

    def test_two_users_have_separate_points_history_locks_and_achievements(self):
        alice = self.register().json()
        alice_cookies = self.cookies
        for task_id, option_id in ((1, 1), (2, 1), (3, 1), (37, 3), (49, 2)):
            self.assertEqual(self.request("POST", f"/topics/tasks/{task_id}/check", {"selected_option_id": option_id}).status_code, 200)
        alice_progress = self.request("GET", "/users/me/progress").json()
        self.assertEqual(alice_progress["total_xp"], 50)
        self.assertEqual(len(alice_progress["achievements"]), 1)
        self.assertEqual(self.request("GET", "/topics/9/tasks").status_code, 200)
        self.assertEqual(self.request("GET", "/topics/9").status_code, 200)
        # Новый набор cookie имитирует вход из другого браузера.
        self.cookies = httpx.Cookies()
        bob = self.register("bob").json()
        self.assertNotEqual(alice["id"], bob["id"])
        self.assertEqual(self.request("GET", "/users/me/progress").json()["total_xp"], 0)
        self.assertEqual(self.request("GET", "/users/me/analytics").json()["total_answers"], 0)
        self.assertEqual(self.request("GET", "/topics/9/tasks").status_code, 403)
        self.assertEqual(self.request("GET", "/topics/9").status_code, 403)
        self.request("POST", "/topics/tasks/1/check", {"selected_option_id": 1})
        bob_progress = self.request("GET", "/users/me/progress").json()
        self.assertEqual(bob_progress["total_xp"], 10)
        self.assertEqual(bob_progress["achievements"], [])
        self.cookies = alice_cookies
        self.assertEqual(self.request("GET", "/users/me/progress").json(), alice_progress)
        self.assertEqual(self.request("GET", "/users/me/analytics").json()["total_answers"], 5)
        self.assertEqual(self.db.get(User, 1).total_xp, 0)

    def test_login_rotates_session_logout_revokes_and_expiry_is_enforced(self):
        self.register()
        old = self.cookies.get(COOKIE_NAME)
        self.assertEqual(self.login().status_code, 200)
        current = self.cookies.get(COOKIE_NAME)
        self.assertNotEqual(old, current)
        self.assertIsNone(self.db.get(UserSession, token_digest(old)))
        self.assertEqual(self.request("POST", "/auth/logout").status_code, 204)
        self.assertEqual(self.request("GET", "/users/me").status_code, 401)
        self.assertIsNone(self.db.get(UserSession, token_digest(current)))
        self.cookies.set(COOKIE_NAME, current)
        self.assertEqual(self.request("GET", "/users/me").status_code, 401)
        self.cookies = httpx.Cookies()
        self.login()
        session = self.db.get(UserSession, token_digest(self.cookies.get(COOKIE_NAME)))
        session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.db.commit()
        self.assertEqual(self.request("GET", "/users/me").status_code, 401)

    def test_duplicate_registration_wrong_login_and_unclaimed_profile(self):
        self.register()
        self.assertEqual(self.register("ALICE").status_code, 409)
        for username, password in (("alice", "wrong password"), ("unknown", PASSWORD), ("hero", PASSWORD)):
            response = self.login(username, password)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json()["detail"], "Неверный логин или пароль.")

    def test_csrf_rejects_missing_or_foreign_origin_and_header(self):
        body = {"username": "alice", "password": PASSWORD}
        for headers in ({}, {"Origin": "http://localhost:5173"},
                        {"Origin": "https://evil.example", "X-Trainer-Request": "1"},
                        {"Origin": "http://localhost:5173.evil.example", "X-Trainer-Request": "1"},
                        {"Origin": "null", "X-Trainer-Request": "1"}):
            self.assertEqual(self.request("POST", "/auth/login", body, headers=headers).status_code, 403)

    def test_validation_never_echoes_passwords_and_disallows_extra_fields(self):
        for body in (
            {"username": "bad name", "password": PASSWORD},
            {"username": "alice", "password": "secret"},
            {"username": "alice", "password": PASSWORD, "user_id": 1},
        ):
            response = self.request("POST", "/auth/login", body)
            self.assertEqual(response.status_code, 422)
            self.assertNotIn(body["password"], response.text)
            self.assertNotIn('"input"', response.text)

    def test_stale_tab_cannot_write_to_another_account(self):
        account = self.register().json()
        response = self.request("POST", "/topics/tasks/1/check", {"selected_option_id": 1}, headers={
            "Origin": "http://localhost:5173", "X-Trainer-Request": "1",
            "X-Trainer-User": str(account["id"] + 1),
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.db.get(User, account["id"]).total_xp, 0)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Attempt)), 0)

    def test_rate_limit_blocks_repeated_password_guesses(self):
        with patch("app.routers.auth.verify_password", return_value=False):
            for _ in range(10):
                self.assertEqual(self.login("unknown").status_code, 401)
            response = self.login("unknown")
            self.assertEqual(response.status_code, 429)
            self.assertIn("Retry-After", response.headers)

    def test_secure_cookie_flag_for_https_deployment(self):
        with patch.dict(os.environ, {"AUTH_COOKIE_SECURE": "true"}):
            self.assertIn("Secure", self.register().headers["set-cookie"])

    def test_claim_preserves_legacy_id_progress_and_survives_seed(self):
        owner = self.db.get(User, 1)
        owner.total_xp = 10
        self.db.add(Attempt(user_id=1, task_id=1, selected_option_id=1, is_correct=True, earned_points=10))
        self.db.commit()
        claim_profile(self.db, Registration(username="owner", display_name="Владелец", password=PASSWORD))
        seed_demo_user(self.db)
        seed_user_progress(self.db, 1)
        self.assertEqual(owner.username, "owner")
        self.assertEqual(owner.display_name, "Владелец")
        self.assertEqual(owner.total_xp, 10)
        self.assertEqual(self.login("owner").status_code, 200)
        self.assertEqual(self.request("GET", "/users/me/analytics").json()["total_answers"], 1)
        with self.assertRaises(ValueError):
            claim_profile(self.db, Registration(username="other", display_name="Другой", password=PASSWORD))


if __name__ == "__main__":
    unittest.main()
