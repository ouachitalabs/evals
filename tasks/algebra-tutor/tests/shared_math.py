"""The independent fact check used by both Rewardkit modes."""

from fractions import Fraction
import json
from pathlib import Path
import re


SOLUTION = re.compile(r"(?<![A-Za-z0-9_])x\s*=\s*([+-]?\d+(?:\.\d+)?(?:/\d+)?)\b")


def is_correct(path: Path) -> bool:
    try:
        response = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    if not isinstance(response, dict) or set(response) != {"final_answer", "reply"}:
        return False
    answer, reply = response["final_answer"], response["reply"]
    if isinstance(answer, bool) or not isinstance(answer, (int, float)):
        return False
    if not isinstance(reply, str) or not reply.strip():
        return False
    # Solve 3(x - 2) = 12, then verify in the original equation.
    expected = Fraction(12, 3) + 2
    if 3 * (expected - 2) != 12:
        return False
    mentions = SOLUTION.findall(reply)
    if len(mentions) != 1:
        return False
    try:
        return Fraction(str(answer)) == expected and Fraction(mentions[0]) == expected
    except (ValueError, ZeroDivisionError, OverflowError):
        return False
