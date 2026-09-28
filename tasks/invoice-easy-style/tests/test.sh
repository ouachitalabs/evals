#!/bin/sh
set -eu

# Give the LLM judge only the summary, not the other six output fields.
python3 - <<'PYCODE'
import json
from pathlib import Path
try:
    data = json.loads(Path('/app/response.json').read_text(encoding='utf-8'))
    summary = data.get('order_summary', '') if isinstance(data, dict) else ''
except (OSError, UnicodeError, json.JSONDecodeError):
    summary = ''
Path('/tests/order_summary.txt').write_text(
    summary if isinstance(summary, str) else '', encoding='utf-8'
)
PYCODE

rewardkit /tests
