"""Deterministic math gate plus optional OpenRouter teaching judge.

Standard-library only. Harbor calls the offline mode; attendees can also call
this file directly on a response JSON. No response text or API key is logged.
"""

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = "openai/gpt-4.1-nano"
SOLUTION = re.compile(r"(?<![A-Za-z0-9_])x\s*=\s*([+-]?\d+(?:\.\d+)?(?:/\d+)?)\b")
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 4},
        "reason": {"type": "string"},
    },
    "required": ["score", "reason"],
    "additionalProperties": False,
}


def check_correctness(response):
    """Check the structured answer and the explicit answer in the reply."""
    if not isinstance(response, dict) or set(response) != {"final_answer", "reply"}:
        return False, "Expected exactly final_answer and reply."
    answer, reply = response["final_answer"], response["reply"]
    if isinstance(answer, bool) or not isinstance(answer, (int, float)):
        return False, "final_answer must be a JSON number."
    if not isinstance(reply, str) or not reply.strip():
        return False, "reply must be nonempty text."
    # Solve 3(x - 2) = 12 by isolating x, then verify by substitution.
    expected = Fraction(12, 3) + 2
    try:
        structured = Fraction(str(answer))
    except (ValueError, ZeroDivisionError, OverflowError):
        return False, "final_answer must be a finite number."
    if structured != expected or 3 * (expected - 2) != 12:
        return False, "The structured answer does not solve the equation."
    mentions = SOLUTION.findall(reply)
    if len(mentions) != 1:
        return False, "The reply must contain exactly one explicit x = <number>."
    try:
        stated = Fraction(mentions[0])
    except (ValueError, ZeroDivisionError):
        return False, "The student-facing conclusion is not a valid number."
    if stated != expected:
        return False, "The student-facing conclusion does not solve the equation."
    return True, "Both answers solve the original equation."


def judge_teaching(reply, model):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("Set OPENROUTER_API_KEY for --live.")
    rubric = (ROOT / "rubric.md").read_text(encoding="utf-8")
    request_body = {
        "model": model,
        "messages": [
            {"role": "system", "content": rubric},
            {"role": "user", "content": "Score this reply:\n\n" + reply},
        ],
        "temperature": 0,
        "max_tokens": 180,
        "provider": {"require_parameters": True},
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "teaching_score", "strict": True, "schema": JUDGE_SCHEMA},
        },
    }
    request = Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(request_body).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=25) as response:
            completion = json.load(response)
    except HTTPError as exc:
        # Provider error bodies may echo request data. Never print them.
        raise RuntimeError(f"OpenRouter returned HTTP {exc.code}") from None
    except URLError as exc:
        raise RuntimeError("Could not reach OpenRouter") from None
    try:
        content = completion["choices"][0]["message"]["content"]
        result = json.loads(content)
        score, reason = result["score"], result["reason"]
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 4:
            raise ValueError("invalid score")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("missing reason")
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
        raise RuntimeError("The judge returned an invalid structured response") from None
    return score, reason


def grade(path, live=False, model=DEFAULT_MODEL):
    try:
        response = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        response = None
    correct, detail = check_correctness(response)
    result = {
        "correctness": float(correct),
        "correctness_detail": detail,
        "teaching_score": None,
        "teaching_reason": "Not judged in offline mode.",
        "reward": float(correct),
    }
    if live and isinstance(response, dict) and isinstance(response.get("reply"), str):
        score, reason = judge_teaching(response["reply"], model)
        result.update(teaching_score=score, teaching_reason=reason,
                      reward=float(correct) * score / 4)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response", required=True, help="Candidate response JSON")
    parser.add_argument("--output", help="Write score JSON to this file")
    parser.add_argument("--live", action="store_true", help="Call OpenRouter teaching judge")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter model slug")
    args = parser.parse_args()
    try:
        result = grade(args.response, args.live, args.model)
    except (ValueError, RuntimeError) as exc:
        print(f"Judge unavailable: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
