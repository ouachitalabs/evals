import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "shared_math", ROOT / "tasks/algebra-tutor/tests/shared_math.py"
)
shared_math = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared_math)


class MathCheckTests(unittest.TestCase):
    def test_contrasting_examples(self):
        expected = {
            "good.json": True,
            "correct-but-poor-teaching.json": True,
            "fluent-but-wrong.json": False,
            "metadata-claim-only.json": False,
        }
        for filename, correct in expected.items():
            with self.subTest(filename=filename):
                self.assertEqual(shared_math.is_correct(ROOT / "examples" / filename), correct)

    def test_missing_file_fails(self):
        self.assertFalse(shared_math.is_correct(ROOT / "examples/missing.json"))


if __name__ == "__main__":
    unittest.main()
