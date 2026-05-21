from db.connection import db_cursor
from repositories.common_repository import fetch_all, new_uuid


def create_ai_request_log(user_id: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        log_id = new_uuid(cursor)
        data = {"log_id": log_id, "user_id": user_id, **payload}
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO ai_request_logs ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        cursor.execute("SELECT * FROM ai_request_logs WHERE log_id=%s", (log_id,))
        return cursor.fetchone()


def list_ai_request_logs(
    user_id: str,
    provider: str | None,
    method_name: str | None,
    status: str | None,
    limit: int,
):
    query = "SELECT * FROM ai_request_logs WHERE user_id=%s"
    params: list = [user_id]

    if provider:
        query += " AND provider=%s"
        params.append(provider)
    if method_name:
        query += " AND method_name=%s"
        params.append(method_name)
    if status:
        query += " AND status=%s"
        params.append(status)

    query += " ORDER BY requested_at DESC LIMIT %s"
    params.append(limit)
    return fetch_all(query, tuple(params))
