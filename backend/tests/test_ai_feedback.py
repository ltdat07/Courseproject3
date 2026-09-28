import asyncio
import json
import os
import unittest
from copy import deepcopy
from unittest.mock import patch

import httpx

from app.ai_practice_content import AI_PRACTICES, get_ai_practice
from app.main import app
from app.auth import require_user
from app.models import User
from app.services import ai_feedback as service


MODEL = "qwen/qwen3.8-27b"
TEST_KEY = "test-groq-key-not-a-real-credential"
SOLUTION = "static double Divide(int a, int b) { return a / b; }"


class AiFeedbackTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[require_user] = lambda: User(id=1, username="test")
        self.addCleanup(lambda: app.dependency_overrides.pop(require_user, None))
        self.requests = []
        self.models = [{"id": MODEL}]
        self.chat_status = 200
        self.catalog_status = 200
        self.retry_header = "42"
        self.error_at = None
        self.error_type = httpx.ConnectError
        self.draft = {
            "checks": [
                {"criterion": criterion, "is_met": True, "explanation": "Выполнено."}
                for criterion in get_ai_practice("safe_division")["evaluation_criteria"]
            ],
            "feedback": {
                "verdict": "correct",
                "summary": "Требования выполнены.",
                "strengths": ["Есть точное деление и проверка делителя."],
                "issues": [], "hints": [], "suggested_fragment": None,
            },
        }
        self.envelope = {
            "choices": [{"message": {"role": "assistant", "content": json.dumps(self.draft)},
                         "finish_reason": "stop"}]
        }
        self.env_patch = patch.dict(os.environ, {
            "GROQ_MODEL": MODEL, "GROQ_API_KEY": TEST_KEY, "GROQ_FREE_PLAN_CONFIRMED": "true",
        })
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        self.client_patch = patch(
            "app.services.ai_feedback.Client",
            side_effect=lambda **kwargs: httpx.Client(
                transport=httpx.MockTransport(self.groq), **kwargs
            ),
        )
        self.client_factory = self.client_patch.start()
        self.addCleanup(self.client_patch.stop)
    def request(self, method, path, **kwargs) -> httpx.Response:
        # ASGITransport не запускает lifespan и инициализацию рабочей базы.
        async def send():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://testserver",
                headers={"Origin": "http://localhost:5173", "X-Trainer-Request": "1"},
            ) as client:
                return await client.request(method, path, **kwargs)
        return asyncio.run(send())

    def groq(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "api.groq.com")
        self.assertEqual(request.headers["authorization"], "Bearer " + TEST_KEY)
        self.assertNotIn(TEST_KEY, str(request.url))
        if request.url.path == self.error_at:
            raise self.error_type("Service unavailable", request=request)
        if request.url.path == "/openai/v1/models":
            return httpx.Response(self.catalog_status, json={"data": self.models})
        self.assertEqual(request.url.path, "/openai/v1/chat/completions")
        return httpx.Response(self.chat_status, json=self.envelope,
                              headers={"retry-after": self.retry_header})

    def analyze(self, **overrides) -> httpx.Response:
        return self.request("POST", "/ai-feedback/analyze", json={
            "practice_id": "safe_division", "student_solution": SOLUTION, **overrides,
        })

    def set_draft(self, draft) -> None:
        self.envelope["choices"][0]["message"]["content"] = json.dumps(draft)

    def test_public_practices_do_not_expose_private_fields(self) -> None:
        response = self.request("GET", "/ai-feedback/practices")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 9)
        for practice in response.json():
            self.assertNotIn("reference_solution", practice)
            self.assertNotIn("evaluation_criteria", practice)
            self.assertIn("starter_code", practice)
        self.assertEqual(self.requests, [])

    def test_every_practice_sends_its_own_assignment_reference_and_criteria(self) -> None:
        for practice in AI_PRACTICES:
            with self.subTest(practice_id=practice["id"]):
                self.draft["checks"] = [
                    {"criterion": criterion, "is_met": True, "explanation": "Выполнено."}
                    for criterion in practice["evaluation_criteria"]
                ]
                self.set_draft(self.draft)
                response = self.analyze(
                    practice_id=practice["id"], student_solution=practice["reference_solution"],
                )
                self.assertEqual(response.status_code, 200)
                payload = json.loads(self.requests[-1].content)
                task = json.loads(payload["messages"][1]["content"])
                for field in ("assignment", "reference_solution", "evaluation_criteria"):
                    self.assertEqual(task[field], practice[field])
                self.assertEqual(task["student_solution"], practice["reference_solution"])
                self.assertNotIn("checks", response.json())

    def test_cloud_status_checks_models_without_generation(self) -> None:
        response = self.request("GET", "/ai-feedback/status")
        status = response.json()
        self.assertTrue(status["available"])
        self.assertEqual(status["provider"], "Groq")
        self.assertEqual(status["model"], MODEL)
        self.assertNotIn(TEST_KEY, response.text)
        self.assertEqual([r.url.path for r in self.requests], ["/openai/v1/models"])

    def test_missing_or_invalid_key_sends_no_requests(self) -> None:
        for key in ("", "  ", "has internal space", "non-ascii-ключ"):
            with self.subTest(key=key), patch.dict(os.environ, {"GROQ_API_KEY": key}):
                status = self.request("GET", "/ai-feedback/status").json()
                self.assertFalse(status["available"])
                if not key.strip():
                    self.assertEqual(
                        status["message"],
                        "🧙 Наставник пока недоступен. Продолжай проходить задания — "
                        "магия обучения работает и без него!",
                    )
                else:
                    self.assertIn("GROQ_API_KEY", status["message"])
                self.assertEqual(self.analyze().status_code, 503)
        self.assertEqual(self.requests, [])

    def test_no_requests_before_free_plan_acknowledgement(self) -> None:
        for flag in ("", "false", "1"):
            with self.subTest(flag=flag), patch.dict(os.environ, {"GROQ_FREE_PLAN_CONFIRMED": flag}):
                status = self.request("GET", "/ai-feedback/status").json()
                self.assertFalse(status["available"])
                self.assertIn("Free", status["message"])
                self.assertEqual(self.analyze().status_code, 503)
        self.assertEqual(self.requests, [])

    def test_unknown_models_have_no_silent_fallback(self) -> None:
        with patch.dict(os.environ, {"GROQ_MODEL": "unapproved-model"}):
            self.assertFalse(self.request("GET", "/ai-feedback/status").json()["available"])
            self.assertEqual(self.analyze().status_code, 503)
        self.assertEqual(self.requests, [])

    def test_model_missing_from_catalog_is_unavailable(self) -> None:
        self.models = []
        self.assertFalse(self.request("GET", "/ai-feedback/status").json()["available"])

    def test_offline_status_is_safe_and_recheck_recovers(self) -> None:
        self.error_at = "/openai/v1/models"
        status = self.request("GET", "/ai-feedback/status").json()
        self.assertFalse(status["available"])
        self.assertIn("интернет", status["message"])
        self.error_at = None
        self.assertTrue(self.request("GET", "/ai-feedback/status").json()["available"])

    def test_catalog_errors_are_safe(self) -> None:
        for code in (401, 403, 404, 429, 500, 302):
            with self.subTest(code=code):
                self.catalog_status = code
                response = self.request("GET", "/ai-feedback/status")
                self.assertFalse(response.json()["available"])
                self.assertNotIn(TEST_KEY, response.text)

    def test_invalid_catalog_is_unavailable(self) -> None:
        for models in (None, {}, ["invalid"]):
            with self.subTest(models=models):
                self.models = models
                self.assertFalse(self.request("GET", "/ai-feedback/status").json()["available"])

    def test_input_validation_happens_before_model_call(self) -> None:
        for overrides, code in [
            ({"practice_id": "missing_quest"}, 404),
            ({"student_solution": " " * 100}, 422),
            ({"student_solution": "short"}, 422),
            ({"student_solution": "x" * 8001}, 422),
        ]:
            with self.subTest(overrides=overrides):
                self.assertEqual(self.analyze(**overrides).status_code, code)
        self.assertEqual(self.requests, [])

    def test_structured_cloud_request_returns_only_public_feedback(self) -> None:
        response = self.analyze()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {**self.draft["feedback"], "model": MODEL})
        self.assertEqual(len(self.requests), 1)
        payload = json.loads(self.requests[0].content)
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["model"], MODEL)
        self.assertEqual(payload["temperature"], 0)
        self.assertLessEqual(payload["max_completion_tokens"], 4096)
        self.assertNotIn("tools", payload)
        self.assertNotIn("api_key", payload)
        self.assertNotIn(TEST_KEY, json.dumps(payload))
        fmt = payload["response_format"]
        self.assertEqual(fmt["type"], "json_schema")
        self.assertTrue(fmt["json_schema"]["strict"])
        schema = fmt["json_schema"]["schema"]
        self.assertEqual(schema, service._response_schema())
        for definition in schema["$defs"].values():
            self.assertFalse(definition["additionalProperties"])
            self.assertEqual(set(definition["required"]), set(definition["properties"]))
        self.assertFalse(schema["additionalProperties"])
        instructions = payload["messages"][0]["content"]
        self.assertIn("сигнатура метода", instructions)
        self.assertIn("не является ошибкой компиляции", instructions)
        self.assertIn("Не требуй return на пути, который завершается throw", instructions)
        self.assertIn("скобки — на отдельных строках", instructions)
        self.assertIn(f"{service.MAX_HINT_LINES} строк", instructions)
        task = json.loads(payload["messages"][1]["content"])
        self.assertEqual(task["student_solution"], SOLUTION)
        self.assertEqual(task["reference_solution"], get_ai_practice("safe_division")["reference_solution"])
        self.assertIn("evaluation_criteria", task)
        for call in self.client_factory.call_args_list:
            self.assertFalse(call.kwargs["trust_env"])
            self.assertFalse(call.kwargs["follow_redirects"])

    def test_bad_output_is_rejected_not_rendered_as_feedback(self) -> None:
        invalid_drafts = []
        for changes in ({"verdict": "invented"}, {"summary": ""}, {"issues": "not a list"},
                        {"strengths": [17]}, {"extra_field": True}, {"issues": ["Wrong"]}):
            draft = deepcopy(self.draft)
            draft["feedback"].update(changes)
            invalid_drafts.append(draft)
        missing = deepcopy(self.draft)
        del missing["feedback"]["suggested_fragment"]
        invalid_drafts.append(missing)
        invalid_drafts.append({"checks": [], "feedback": self.draft["feedback"]})
        contradiction = deepcopy(self.draft)
        contradiction["checks"][0]["is_met"] = False
        invalid_drafts.append(contradiction)
        for draft in invalid_drafts:
            with self.subTest(draft=draft):
                self.set_draft(draft)
                self.assertEqual(self.analyze().status_code, 502)

    def test_long_code_hint_is_omitted_without_losing_review(self) -> None:
        for fragment in ("line\n" * (service.MAX_HINT_LINES + 1), "x" * (service.MAX_HINT_CHARS + 1)):
            with self.subTest(fragment=fragment):
                self.draft["feedback"]["suggested_fragment"] = fragment
                self.set_draft(self.draft)
                response = self.analyze()
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(response.json()["suggested_fragment"])

    def test_readable_code_hint_keeps_line_breaks_and_indentation(self) -> None:
        fragment = (
            "for (int i = 1; i < numbers.Length; i++)\n"
            "{\n"
            "    if (numbers[i] > max)\n"
            "    {\n"
            "        max = numbers[i];\n"
            "    }\n"
            "}\n"
            "// Продолжи решение самостоятельно."
        )
        self.assertEqual(len(fragment.splitlines()), service.MAX_HINT_LINES)
        self.draft["feedback"]["suggested_fragment"] = fragment
        self.set_draft(self.draft)
        response = self.analyze()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["suggested_fragment"], fragment)

    def test_malformed_incomplete_and_refusal_envelopes_are_rejected(self) -> None:
        for envelope in (
            [], {}, {"choices": []}, {"choices": [None]},
            {"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]},
            {"choices": [{"finish_reason": "stop", "message": None}]},
            {"choices": [{"finish_reason": "stop", "message": {"refusal": "No"}}]},
            {"choices": [{"finish_reason": "stop", "message": {"content": "```json\n{}\n```"}}]},
            {"choices": [{"finish_reason": "stop", "message": {"content": 123}}]},
        ):
            with self.subTest(envelope=envelope):
                self.envelope = envelope
                self.assertEqual(self.analyze().status_code, 502)

    def test_provider_errors_are_safe_no_retries_and_release_slot(self) -> None:
        for code, expected in ((500, 502), (400, 502), (401, 503), (403, 503), (404, 503), (302, 502)):
            with self.subTest(code=code):
                self.chat_status = code
                before = len(self.requests)
                response = self.analyze()
                self.assertEqual(response.status_code, expected)
                self.assertNotIn(TEST_KEY, response.text)
                self.assertEqual(len(self.requests), before + 1)
        self.chat_status = 200
        for error_type, expected in ((httpx.ReadTimeout, 502), (httpx.ConnectError, 503)):
            with self.subTest(error_type=error_type):
                self.error_at = "/openai/v1/chat/completions"
                self.error_type = error_type
                self.assertEqual(self.analyze().status_code, expected)
        self.error_at = None
        self.assertEqual(self.analyze().status_code, 200)

    def test_rate_limit_or_payment_error_does_not_retry_or_change_provider(self) -> None:
        for status in (429, 402):
            for header, expected in (("42", "42"), ("bad header", "60"), ("0", "1"), ("999999", "86400")):
                with self.subTest(status=status, header=header):
                    self.chat_status = status
                    self.retry_header = header
                    before = len(self.requests)
                    response = self.analyze()
                    self.assertEqual(response.status_code, 429)
                    self.assertEqual(response.headers["Retry-After"], expected)
                    self.assertEqual(len(self.requests), before + 1)

    def test_parallel_analysis_is_rejected_without_another_model_call(self) -> None:
        self.assertTrue(service._generation_slot.acquire(blocking=False))
        try:
            response = self.analyze()
        finally:
            service._generation_slot.release()
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "3")
        self.assertEqual(self.requests, [])
        self.assertEqual(self.analyze().status_code, 200)


if __name__ == "__main__":
    unittest.main()
