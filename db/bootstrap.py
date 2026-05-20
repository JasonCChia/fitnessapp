from pathlib import Path

from db.connection import db_cursor


def execute_schema_file(schema_path: str | None = None) -> dict:
    resolved_path = Path(schema_path or "db/schema.sql")
    if not resolved_path.exists():
        raise FileNotFoundError(f"Schema file not found: {resolved_path}")

    sql_text = resolved_path.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]

    executed = 0
    with db_cursor(commit=True) as (_, cursor):
        for statement in statements:
            cursor.execute(statement)
            executed += 1

    return {"schema_file": str(resolved_path), "statements_executed": executed}
