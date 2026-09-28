"""Validate JSON shape and the requested field formats."""

from datetime import date
import json
from pathlib import Path
import re

from rewardkit import criterion


EXPECTED = json.loads(Path("/tests/expected.json").read_text(encoding="utf-8"))
KEYS = set(EXPECTED)
MONEY = re.compile(r"(?:0|[1-9][0-9]*)\.[0-9]{2}\Z")


def output(workspace: Path) -> dict | None:
    try:
        value = json.loads((workspace / "response.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


@criterion(description="Exactly seven string fields with valid date and amount formats")
def schema(workspace: Path) -> bool:
    data = output(workspace)
    if data is None or set(data) != KEYS:
        return False
    if not all(isinstance(data[key], str) and data[key].strip() for key in KEYS):
        return False
    if not re.fullmatch(r"[0-9]{9}", data["seller_tax_id"]):
        return False
    if not MONEY.fullmatch(data["total"]) or not MONEY.fullmatch(data["tax_amount"]):
        return False
    try:
        return date.fromisoformat(data["invoice_date"]).isoformat() == data["invoice_date"]
    except ValueError:
        return False
