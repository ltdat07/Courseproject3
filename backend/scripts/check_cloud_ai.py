"""Проверка Groq: python -m scripts.check_cloud_ai --send [--all].

Нужны запущенный backend, ключ Groq и подтверждённый бесплатный тариф.
Флаг --send разрешает отправку примеров кода; запросы расходуют квоту аккаунта.
"""

import argparse
import time
from contextlib import contextmanager
from getpass import getpass

import httpx

from app.ai_practice_content import AI_PRACTICES
from app.auth import allowed_origins
from app.schemas import AiFeedbackResponse


INCORRECT_SOLUTIONS = {
    "safe_division": "static double Divide(int a, int b) { return a / b; }",
    "find_max": (
        "static int FindMax(int[] numbers) { "
        "if (numbers == null || numbers.Length == 0) throw new ArgumentException(); "
        "int max = 0; foreach (int n in numbers) if (n > max) max = n; return max; }"
    ),
    "hero_damage": (
        "public class Hero { public string Name { get; } "
        "public int Health { get; private set; } "
        "public Hero(string name, int health) { Name = name; Health = Math.Max(0, health); } "
        "public void TakeDamage(int damage) { Health -= damage; } }"
    ),
    "sum_even": "static long SumEven(int[] numbers) { long sum = 0; foreach (int n in numbers) sum += n; return sum; }",
    "count_words": "static int CountWords(string text) { return text.Split(' ').Length; }",
    "parse_level": "static int ParseLevel(string text) { return int.Parse(text); }",
    "count_loot": (
        "static Dictionary<string, int> CountLoot(string[] items) { "
        "var counts = new Dictionary<string, int>(); "
        "foreach (string item in items) counts[item] = 1; return counts; }"
    ),
    "positive_runes": "static int[] PositiveRunes(int[] numbers) { return numbers.Where(n => n >= 0).ToArray(); }",
    "sum_rewards_async": (
        "static async Task<int> SumRewardsAsync(Task<int> first, Task<int> second) { "
        "return first.Result + second.Result; }"
    ),
}


@contextmanager
def signed_in_client():
    origins = sorted(allowed_origins())
    if not origins:
        raise SystemExit("Настрой AUTH_ALLOWED_ORIGINS перед проверкой.")
    username = input("Логин аккаунта тренажёра: ")
    password = getpass("Пароль аккаунта (ввод скрыт): ")
    with httpx.Client(
        base_url="http://127.0.0.1:8000", timeout=70, trust_env=False,
        headers={"Origin": origins[0], "X-Trainer-Request": "1"},
    ) as client:
        response = client.post("/auth/login", json={"username": username, "password": password})
        del password
        if response.status_code != 200:
            raise SystemExit(f"Вход не выполнен (HTTP {response.status_code}). Проверь логин и пароль на сайте.")
        try:
            yield client
        finally:
            try:
                client.post("/auth/logout").raise_for_status()
            except httpx.HTTPError:
                print("Не удалось закрыть тестовую сессию; она истечёт автоматически через 7 дней.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--send", action="store_true", help="Разрешить отправку учебного кода в Groq")
    parser.add_argument("--all", action="store_true", help="Проверить правильный и ошибочный примеры каждого испытания")
    args = parser.parse_args()
    if not args.send:
        print("Запросов не было. Для проверки Free и ключа сначала настрой backend; затем добавь --send.")
        return
    failures = []
    completed = 0
    with signed_in_client() as client:
        status = client.get("/ai-feedback/status")
        status.raise_for_status()
        print(status.json()["message"], flush=True)
        if not status.json()["available"]:
            raise SystemExit(1)
        progress_before = client.get("/users/me/progress").json()
        analytics_before = client.get("/users/me/analytics").json()
        for practice in (AI_PRACTICES if args.all else AI_PRACTICES[:1]):
            for correct in ((False, True) if args.all else (False,)):
                label = practice["id"] + (" / correct" if correct else " / incorrect")
                started = time.monotonic()
                try:
                    response = client.post("/ai-feedback/analyze", json={
                        "practice_id": practice["id"],
                        "student_solution": practice["reference_solution"] if correct
                        else INCORRECT_SOLUTIONS[practice["id"]],
                    })
                    if response.status_code in (429, 503):
                        raise SystemExit(response.json().get("detail", "Сервис недоступен. Попробуй позже."))
                    response.raise_for_status()
                    feedback = AiFeedbackResponse.model_validate(response.json())
                    valid = (feedback.verdict == "correct") == correct
                    valid = valid and (not feedback.issues if correct else bool(feedback.issues))
                    print(f"{'PASS' if valid else 'FAIL'} {label}: {feedback.verdict} "
                          f"({time.monotonic() - started:.1f}s)", flush=True)
                    print(feedback.summary, flush=True)
                    for issue in feedback.issues:
                        print(" - " + issue, flush=True)
                    if not valid:
                        failures.append(label)
                    completed += 1
                except (httpx.HTTPError, ValueError) as exc:
                    print(f"FAIL {label}: {exc}", flush=True)
                    failures.append(label)
        if client.get("/users/me/progress").json() != progress_before:
            failures.append("Progress changed during check (avoid normal tasks while testing)")
        if client.get("/users/me/analytics").json() != analytics_before:
            failures.append("Analytics changed during check (avoid normal tasks while testing)")
    if failures:
        raise SystemExit("Failed: " + "; ".join(failures))
    print(f"{completed} live verdict checks passed; XP, achievements and attempt history unchanged.")
    print("These checks validate JSON and verdicts, not the factual accuracy of every comment.")


if __name__ == "__main__":
    main()
