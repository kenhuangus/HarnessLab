from __future__ import annotations

import unittest

from harnesslab.labs import CHAPTERS, run_all_labs, run_lab


class LabExecutionTest(unittest.TestCase):
    def test_all_registered_labs_run(self) -> None:
        results = run_all_labs()
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertTrue(result.passed, result.to_json())
            self.assertGreaterEqual(result.score, 0.8, result.to_json())
            self.assertTrue(result.decisions, result.to_json())
            self.assertTrue(result.artifacts, result.to_json())

    def test_each_lab_matches_registry_key(self) -> None:
        for chapter in CHAPTERS:
            with self.subTest(chapter=chapter.key):
                result = run_lab(chapter.key)
                self.assertEqual(result.chapter, chapter.key)
                self.assertEqual(result.title, chapter.title)


if __name__ == "__main__":
    unittest.main()

