import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from db.connection import db_cursor


def json_default(value: Any):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Type {type(value)} is not JSON serializable")


def row_to_json_safe(row: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(row, default=json_default))


def rows_to_json_safe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row_to_json_safe(row) for row in rows]


def fetch_one(query: str, params: tuple | list | None = None):
    with db_cursor() as (_, cursor):
        cursor.execute(query, params or ())
        return cursor.fetchone()


def fetch_all(query: str, params: tuple | list | None = None):
    with db_cursor() as (_, cursor):
        cursor.execute(query, params or ())
        return cursor.fetchall()


def execute_write(query: str, params: tuple | list | None = None) -> int:
    with db_cursor(commit=True) as (_, cursor):
        affected = cursor.execute(query, params or ())
        return affected
