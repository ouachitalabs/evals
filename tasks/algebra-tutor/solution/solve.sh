#!/bin/sh
set -eu
uv run --no-project --offline --python /usr/local/bin/python3 - <<'PY'
import json
from fractions import Fraction
from pathlib import Path

coefficient = 3
offset = 2
right_side = 12
answer = Fraction(right_side, coefficient) + offset
assert answer.denominator == 1
reply = (
    f"Almost: the 3 multiplies both terms in the parentheses, so "
    f"3(x - {offset}) becomes 3x - {coefficient * offset}, not 3x - {offset}. "
    f"Then 3x - {coefficient * offset} = {right_side}; add {coefficient * offset} "
    f"and divide by {coefficient} to get x = {answer.numerator}. "
    f"Can you substitute {answer.numerator} into the original equation to check it?"
)
Path('/app/response.json').write_text(json.dumps({
    'final_answer': answer.numerator,
    'reply': reply,
}) + '\n')
PY
