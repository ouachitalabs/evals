#!/bin/sh
set -u
mkdir -p /logs/verifier
python3 /tests/grade.py --response /app/response.json \
  --output /logs/verifier/score.json >/dev/null
status=$?
if [ "$status" -ne 0 ]; then
  printf '{"reward":0.0,"correctness":0.0}\n' > /logs/verifier/reward.json
  exit 0
fi
python3 - <<'PY'
import json
from pathlib import Path
score = json.loads(Path('/logs/verifier/score.json').read_text())
Path('/logs/verifier/reward.json').write_text(json.dumps({
    'reward': score['reward'],
    'correctness': score['correctness'],
}) + '\n')
PY
