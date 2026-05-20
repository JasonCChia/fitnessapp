from db.connection import db_cursor
from repositories.common_repository import fetch_all, new_uuid


def list_ai_prompt_configs(user_id: str, method_name: str | None):
    query = """
        SELECT * FROM ai_prompt_configs
        WHERE (user_id=%s OR user_id IS NULL)
    """
    params: list = [user_id]
    if method_name:
        query += " AND method_name=%s"
        params.append(method_name)
    query += " ORDER BY (user_id IS NULL) ASC, updated_at DESC"
    return fetch_all(query, tuple(params))


def upsert_ai_prompt_config(user_id: str, method_name: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        cursor.execute(
            """
            SELECT config_id FROM ai_prompt_configs
            WHERE user_id=%s AND method_name=%s
            LIMIT 1
            """,
            (user_id, method_name),
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE ai_prompt_configs
                SET system_prompt=%s,
                    user_template=%s,
                    output_schema=%s,
                    temperature=%s,
                    max_tokens=%s,
                    is_default=%s
                WHERE user_id=%s AND method_name=%s
                """,
                (
                    payload.get("system_prompt"),
                    payload.get("user_template"),
                    payload.get("output_schema"),
                    payload.get("temperature", 0.70),
                    payload.get("max_tokens", 2000),
                    payload.get("is_default", False),
                    user_id,
                    method_name,
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO ai_prompt_configs (
                    config_id, user_id, method_name, system_prompt, user_template,
                    output_schema, temperature, max_tokens, is_default
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    new_uuid(cursor),
                    user_id,
                    method_name,
                    payload.get("system_prompt"),
                    payload.get("user_template"),
                    payload.get("output_schema"),
                    payload.get("temperature", 0.70),
                    payload.get("max_tokens", 2000),
                    payload.get("is_default", False),
                ),
            )
        cursor.execute(
            """
            SELECT * FROM ai_prompt_configs
            WHERE user_id=%s AND method_name=%s
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (user_id, method_name),
        )
        return cursor.fetchone()
