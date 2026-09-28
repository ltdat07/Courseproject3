import unittest

from app.ai_practice_content import AI_PRACTICES, get_ai_practice, get_public_ai_practices
from app.schemas import AiPracticeResponse
from scripts.check_cloud_ai import INCORRECT_SOLUTIONS


class AiPracticeCatalogTestCase(unittest.TestCase):
    def test_catalog_has_unique_ids_and_complete_content(self) -> None:
        self.assertEqual(len(AI_PRACTICES), 9)
        ids = [practice["id"] for practice in AI_PRACTICES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[:3], ["safe_division", "find_max", "hero_damage"])
        for practice in AI_PRACTICES:
            with self.subTest(practice_id=practice["id"]):
                for field in ("title", "story", "assignment", "starter_code", "reference_solution"):
                    self.assertTrue(practice[field].strip())
                self.assertNotEqual(practice["starter_code"], practice["reference_solution"])
                self.assertGreaterEqual(len(practice["evaluation_criteria"]), 3)
                self.assertLessEqual(len(practice["reference_solution"]), 8000)
                self.assertIs(get_ai_practice(practice["id"]), practice)

    def test_public_catalog_contains_only_safe_fields(self) -> None:
        expected = {"id", "topic_title", "title", "story", "assignment", "starter_code"}
        for practice in get_public_ai_practices():
            with self.subTest(practice_id=practice["id"]):
                self.assertEqual(set(practice), expected)
                AiPracticeResponse.model_validate(practice)
        self.assertIsNone(get_ai_practice("missing"))

    def test_opt_in_cloud_checks_cover_every_practice(self) -> None:
        self.assertEqual(set(INCORRECT_SOLUTIONS), {practice["id"] for practice in AI_PRACTICES})
        for practice in AI_PRACTICES:
            self.assertNotEqual(INCORRECT_SOLUTIONS[practice["id"]], practice["reference_solution"])


if __name__ == "__main__":
    unittest.main()
