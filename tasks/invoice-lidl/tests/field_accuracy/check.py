"""Compare the six factual fields with the published labels."""

from decimal import Decimal
import json
from pathlib import Path
import re
import unicodedata

from rewardkit import criterion


EXPECTED = json.loads(Path("/tests/expected.json").read_text(encoding="utf-8"))
MONEY = re.compile(r"(?:0|[1-9][0-9]*)\.[0-9]{2}\Z")


def output(workspace: Path) -> dict | None:
    try:
        value = json.loads((workspace / "response.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def seller_name_key(value: str) -> str:
    # Ignore case, accents, and repeated whitespace, but preserve whole names.
    unaccented = "".join(
        char for char in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(char)
    )
    return " ".join(unaccented.split())


def matches(workspace: Path, key: str) -> bool:
    data = output(workspace)
    if data is None or not isinstance(data.get(key), str):
        return False
    actual, expected = data[key], EXPECTED[key]
    if key == "seller_name":
        return seller_name_key(actual) == seller_name_key(expected)
    if key == "seller_tax_id":
        return actual == expected
    if key == "invoice_date":
        return actual == expected
    if key == "invoice_number":
        return " ".join(actual.casefold().split()) == " ".join(expected.casefold().split())
    if key in {"total", "tax_amount"}:
        return bool(MONEY.fullmatch(actual)) and Decimal(actual) == Decimal(expected)
    raise ValueError(key)


@criterion(description="Seller trading name matches the invoice")
def seller_name(workspace: Path) -> bool:
    return matches(workspace, "seller_name")


@criterion(description="Seller NIF or NIPC matches the invoice")
def seller_tax_id(workspace: Path) -> bool:
    return matches(workspace, "seller_tax_id")


@criterion(description="Document date matches the invoice")
def invoice_date(workspace: Path) -> bool:
    return matches(workspace, "invoice_date")


@criterion(description="Document number matches the invoice")
def invoice_number(workspace: Path) -> bool:
    return matches(workspace, "invoice_number")


@criterion(description="Final total matches the invoice")
def total(workspace: Path) -> bool:
    return matches(workspace, "total")


@criterion(description="VAT amount matches the invoice")
def tax_amount(workspace: Path) -> bool:
    return matches(workspace, "tax_amount")
