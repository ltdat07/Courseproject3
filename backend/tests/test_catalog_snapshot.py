"""Проверка содержимого, ID и порядка учебных каталогов."""

import hashlib
import json
from pathlib import Path
import unittest

from app.ai_practice_content import AI_PRACTICES
from app.content.practice import TASKS as GROUPED_TASKS
from app.course_content import TOPICS
from app.practice_content import TASKS


class CatalogSnapshotTestCase(unittest.TestCase):
    def test_catalog_ids_order_and_all_fields_are_preserved(self) -> None:
        fixture_path = Path(__file__).parent / "fixtures" / "catalog_snapshot.json"
        expected = json.loads(fixture_path.read_text(encoding="utf-8"))
        catalogs = {
            "TOPICS": TOPICS,
            "TASKS": TASKS,
            "AI_PRACTICES": AI_PRACTICES,
        }
        self.assertEqual(set(catalogs), set(expected))
        for name, items in catalogs.items():
            with self.subTest(catalog=name):
                self.assertEqual([item["id"] for item in items], expected[name]["ids"])
                # Хеш учитывает содержимое и порядок списков, но не порядок полей словаря.
                serialized = json.dumps(
                    items, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
                self.assertEqual(
                    hashlib.sha256(serialized).hexdigest(), expected[name]["sha256"]
                )

    def test_legacy_practice_import_exposes_the_same_catalog(self) -> None:
        self.assertIs(TASKS, GROUPED_TASKS)


if __name__ == "__main__":
    unittest.main()
