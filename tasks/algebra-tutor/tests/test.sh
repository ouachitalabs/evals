#!/bin/sh
set -eu

case "${JUDGE_MODE:-offline}" in
  offline|live) ;;
  *) echo "JUDGE_MODE must be offline or live" >&2; exit 2 ;;
esac

export PYTHONPATH=/tests
uv run --no-project --offline --python /usr/local/bin/python3 \
  /usr/local/bin/rewardkit "/tests/${JUDGE_MODE:-offline}"
