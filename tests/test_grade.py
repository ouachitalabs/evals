import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "grade", ROOT / "tasks/algebra-tutor/tests/grade.py"
)
grade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grade)


class GraderTests(unittest.TestCase):
    def test_examples_show_the_gate(self):
        expected = {
            "good.json": 1.0,
            "correct-but-poor-teaching.json": 1.0,
            "fluent-but-wrong.json": 0.0,
            "metadata-claim-only.json": 0.0,
        }
        for filename, correctness in expected.items():
            with self.subTest(filename=filename):
                result = grade.grade(ROOT / "examples" / filename)
                self.assertEqual(result["correctness"], correctness)
                self.assertIsNone(result["teaching_score"])

    def test_missing_or_invalid_files_fail_closed(self):
        self.assertEqual(grade.grade(ROOT / "examples/missing.json")["reward"], 0)
        self.assertFalse(grade.check_correctness({"final_answer": True, "reply": "x = 6"})[0])
        self.assertFalse(grade.check_correctness({"final_answer": 6, "reply": "x = 6 and x = 5"})[0])
        self.assertFalse(grade.check_correctness({"final_answer": 6, "reply": "x = 6/2"})[0])
        self.assertFalse(grade.check_correctness({"final_answer": 6, "reply": "x = 6/0"})[0])


if __name__ == "__main__":
    unittest.main()
