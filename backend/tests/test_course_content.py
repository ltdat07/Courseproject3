import unittest
from collections import Counter

from app.course_content import TOPICS
from app.practice_content import TASKS


class CourseContentTestCase(unittest.TestCase):
    def test_topic_ids_and_levels_are_unique(self) -> None:
        self.assertEqual(len({topic["id"] for topic in TOPICS}), len(TOPICS))
        self.assertEqual(
            sorted(topic["level"] for topic in TOPICS),
            list(range(1, len(TOPICS) + 1)),
        )
        for topic in TOPICS:
            with self.subTest(topic_id=topic["id"]):
                self.assertTrue(topic["theory"].strip())

    def test_tasks_reference_existing_topics_and_answers(self) -> None:
        topic_ids = {topic["id"] for topic in TOPICS}
        self.assertEqual(len({task["id"] for task in TASKS}), len(TASKS))
        for task in TASKS:
            with self.subTest(task_id=task["id"]):
                self.assertIn(task["topic_id"], topic_ids)
                option_ids = [option["id"] for option in task["options"]]
                self.assertGreaterEqual(len(option_ids), 2)
                self.assertEqual(len(option_ids), len(set(option_ids)))
                self.assertIn(task["correct_option_id"], option_ids)
                self.assertTrue(task["explanation"].strip())

    def test_topic_rewards_match_the_number_of_tasks(self) -> None:
        task_counts = Counter(task["topic_id"] for task in TASKS)
        for topic in TOPICS:
            with self.subTest(topic_id=topic["id"]):
                self.assertGreater(task_counts[topic["id"]], 0)
                self.assertEqual(topic["points"], task_counts[topic["id"]] * 10)


if __name__ == "__main__":
    unittest.main()
