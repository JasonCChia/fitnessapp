from db.connection import db_cursor
from repositories.common_repository import fetch_all, fetch_one, new_uuid


def _archive_active_workout(cursor, user_id: str):
    cursor.execute(
        """
        UPDATE workout_plans
        SET status='archived', archived_at=NOW()
        WHERE user_id=%s AND status='active'
        """,
        (user_id,),
    )


def _archive_active_meal(cursor, user_id: str):
    cursor.execute(
        """
        UPDATE meal_plans
        SET status='archived'
        WHERE user_id=%s AND status='active'
        """,
        (user_id,),
    )


def create_workout_plan(user_id: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        plan_id = new_uuid(cursor)
        data = {"plan_id": plan_id, "user_id": user_id, **payload}
        if data.get("status") == "active":
            _archive_active_workout(cursor, user_id)
            data["archived_at"] = None
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO workout_plans ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        cursor.execute("SELECT * FROM workout_plans WHERE plan_id=%s", (plan_id,))
        return cursor.fetchone()


def list_workout_plans(user_id: str, status: str | None):
    query = "SELECT * FROM workout_plans WHERE user_id=%s"
    params: list = [user_id]
    if status:
        query += " AND status=%s"
        params.append(status)
    query += " ORDER BY created_at DESC"
    return fetch_all(query, tuple(params))


def activate_workout_plan(user_id: str, plan_id: str):
    with db_cursor(commit=True) as (_, cursor):
        _archive_active_workout(cursor, user_id)
        affected = cursor.execute(
            """
            UPDATE workout_plans
            SET status='active', confirmed_at=NOW(), archived_at=NULL
            WHERE user_id=%s AND plan_id=%s
            """,
            (user_id, plan_id),
        )
        if affected == 0:
            return None
        cursor.execute(
            "SELECT * FROM workout_plans WHERE user_id=%s AND plan_id=%s",
            (user_id, plan_id),
        )
        return cursor.fetchone()


def create_meal_plan(user_id: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        plan_id = new_uuid(cursor)
        data = {"plan_id": plan_id, "user_id": user_id, **payload}
        if data.get("status") == "active":
            _archive_active_meal(cursor, user_id)
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO meal_plans ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        cursor.execute("SELECT * FROM meal_plans WHERE plan_id=%s", (plan_id,))
        return cursor.fetchone()


def list_meal_plans(user_id: str, status: str | None):
    query = "SELECT * FROM meal_plans WHERE user_id=%s"
    params: list = [user_id]
    if status:
        query += " AND status=%s"
        params.append(status)
    query += " ORDER BY created_at DESC"
    return fetch_all(query, tuple(params))


def activate_meal_plan(user_id: str, plan_id: str):
    with db_cursor(commit=True) as (_, cursor):
        _archive_active_meal(cursor, user_id)
        affected = cursor.execute(
            """
            UPDATE meal_plans
            SET status='active', confirmed_at=NOW()
            WHERE user_id=%s AND plan_id=%s
            """,
            (user_id, plan_id),
        )
        if affected == 0:
            return None
        cursor.execute(
            "SELECT * FROM meal_plans WHERE user_id=%s AND plan_id=%s",
            (user_id, plan_id),
        )
        return cursor.fetchone()


def get_active_program(user_id: str):
    workout = fetch_one(
        """
        SELECT * FROM workout_plans
        WHERE user_id=%s AND status='active'
        ORDER BY confirmed_at DESC, created_at DESC
        LIMIT 1
        """,
        (user_id,),
    )
    meal = fetch_one(
        """
        SELECT * FROM meal_plans
        WHERE user_id=%s AND status='active'
        ORDER BY confirmed_at DESC, created_at DESC
        LIMIT 1
        """,
        (user_id,),
    )
    return {"workout_plan": workout, "meal_plan": meal}
