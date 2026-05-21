from datetime import datetime

from db.connection import db_cursor
from repositories.common_repository import fetch_all, fetch_one, new_uuid


def create_user(payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        user_id = new_uuid(cursor)
        data = {"user_id": user_id, **payload}
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO users ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        return cursor.fetchone()


def list_users():
    return fetch_all("SELECT * FROM users ORDER BY created_at DESC")


def get_user(user_id: str):
    return fetch_one("SELECT * FROM users WHERE user_id=%s", (user_id,))


def get_user_by_email(email: str):
    return fetch_one("SELECT * FROM users WHERE email=%s LIMIT 1", (email,))


def get_user_auth_by_email(email: str):
    return fetch_one(
        """
        SELECT user_id, email, password_hash
        FROM users
        WHERE email=%s
        LIMIT 1
        """,
        (email,),
    )


def update_user(user_id: str, payload: dict):
    assignments = ", ".join(f"{key}=%s" for key in payload.keys())
    params = tuple(payload.values()) + (user_id,)
    with db_cursor(commit=True) as (_, cursor):
        affected = cursor.execute(f"UPDATE users SET {assignments} WHERE user_id=%s", params)
        if affected == 0:
            return None
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        return cursor.fetchone()


def upsert_user_preferences(user_id: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        cursor.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
        if cursor.fetchone() is None:
            return None
        cursor.execute(
            """
            INSERT INTO user_preferences (
                user_id, sleep_target_hours, activity_level, goal_type, goal_weight_kg,
                goal_deadline_date, last_monthly_review_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                sleep_target_hours=VALUES(sleep_target_hours),
                activity_level=VALUES(activity_level),
                goal_type=VALUES(goal_type),
                goal_weight_kg=VALUES(goal_weight_kg),
                goal_deadline_date=VALUES(goal_deadline_date),
                last_monthly_review_at=VALUES(last_monthly_review_at)
            """,
            (
                user_id,
                payload.get("sleep_target_hours", 8.0),
                payload.get("activity_level"),
                payload.get("goal_type"),
                payload.get("goal_weight_kg"),
                payload.get("goal_deadline_date"),
                payload.get("last_monthly_review_at"),
            ),
        )
        cursor.execute("SELECT * FROM user_preferences WHERE user_id=%s LIMIT 1", (user_id,))
        return cursor.fetchone()


def get_user_preferences(user_id: str):
    return fetch_one("SELECT * FROM user_preferences WHERE user_id=%s LIMIT 1", (user_id,))


def create_food_preference(user_id: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        preference_id = new_uuid(cursor)
        data = {"preference_id": preference_id, "user_id": user_id, **payload}
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO food_preferences ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        cursor.execute("SELECT * FROM food_preferences WHERE preference_id=%s", (preference_id,))
        return cursor.fetchone()


def list_food_preferences(user_id: str, include_deleted: bool):
    query = "SELECT * FROM food_preferences WHERE user_id=%s"
    if not include_deleted:
        query += " AND deleted_at IS NULL"
    query += " ORDER BY created_at DESC"
    return fetch_all(query, (user_id,))


def soft_delete_food_preference(user_id: str, preference_id: str) -> bool:
    with db_cursor(commit=True) as (_, cursor):
        affected = cursor.execute(
            """
            UPDATE food_preferences
            SET deleted_at=%s
            WHERE user_id=%s AND preference_id=%s AND deleted_at IS NULL
            """,
            (datetime.utcnow(), user_id, preference_id),
        )
        return affected > 0


def create_onboarding(
    user_payload: dict,
    preferences_payload: dict,
    food_preferences: list[dict],
    fitness_snapshot: dict | None,
):
    with db_cursor(commit=True) as (_, cursor):
        user_id = new_uuid(cursor)
        data = {"user_id": user_id, **user_payload}
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO users ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )

        cursor.execute(
            """
            INSERT INTO user_preferences (
                user_id, sleep_target_hours, activity_level, goal_type, goal_weight_kg,
                goal_deadline_date, last_monthly_review_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                preferences_payload.get("sleep_target_hours", 8.0),
                preferences_payload.get("activity_level"),
                preferences_payload.get("goal_type"),
                preferences_payload.get("goal_weight_kg"),
                preferences_payload.get("goal_deadline_date"),
                preferences_payload.get("last_monthly_review_at"),
            ),
        )

        for pref in food_preferences:
            pref_id = new_uuid(cursor)
            pref_data = {"preference_id": pref_id, "user_id": user_id, **pref}
            pref_columns = ", ".join(pref_data.keys())
            pref_placeholders = ", ".join(["%s"] * len(pref_data))
            cursor.execute(
                f"INSERT INTO food_preferences ({pref_columns}) VALUES ({pref_placeholders})",
                tuple(pref_data.values()),
            )

        if fitness_snapshot:
            capability_id = new_uuid(cursor)
            fc_data = {"capability_id": capability_id, "user_id": user_id, **fitness_snapshot}
            fc_columns = ", ".join(fc_data.keys())
            fc_placeholders = ", ".join(["%s"] * len(fc_data))
            cursor.execute(
                f"INSERT INTO fitness_capabilities ({fc_columns}) VALUES ({fc_placeholders})",
                tuple(fc_data.values()),
            )

        cursor.execute("UPDATE users SET onboarding_done=TRUE WHERE user_id=%s", (user_id,))

    return user_id
