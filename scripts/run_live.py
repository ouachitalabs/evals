"""Launch Harbor with the local OpenRouter secret available to its verifier."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
KEY_LINE = re.compile(r"^\s*(?:export\s+)?OPENROUTER_API_KEY\s*=\s*([^\s#]+)")


def main():
    path = Path.home() / ".secrets"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        print(f"Cannot read {path}", file=sys.stderr)
        return 2
    matches = [match.group(1).strip("\"'") for line in lines
               if (match := KEY_LINE.match(line))]
    if len(matches) != 1 or not matches[0]:
        print("Expected one OPENROUTER_API_KEY assignment in ~/.secrets", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = matches[0]
    env["EVAL_JUDGE_MODE"] = "live"
    arguments = sys.argv[1:] or [
        "--agent", "terminus-2",
        "--model", "openrouter/deepseek/deepseek-v4.1-flash",
        "--agent-kwarg", "max_turns=8",
        "--agent-kwarg", "record_terminal_session=false",
    ]
    command = ["uvx", "--from", "harbor==0.23.0", "harbor", "run", "--yes",
               "--path", "tasks/algebra-tutor", *arguments]
    return subprocess.run(command, cwd=ROOT, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
