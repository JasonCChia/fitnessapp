import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any


def json_default(value: Any):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Type {type(value)} is not JSON serializable")


def row_to_json_safe(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return json.loads(json.dumps(row, default=json_default))


def rows_to_json_safe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row_to_json_safe(row) for row in rows]
