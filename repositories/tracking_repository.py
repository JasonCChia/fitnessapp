from db.connection import db_cursor
from repositories.common_repository import fetch_all, new_uuid


def create_weight_log(user_id: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        log_id = new_uuid(cursor)
        data = {"log_id": log_id, "user_id": user_id, **payload}
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO weight_logs ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        cursor.execute("SELECT * FROM weight_logs WHERE log_id=%s", (log_id,))
        return cursor.fetchone()


def list_weight_logs(user_id: str, start_date: str, end_date: str):
    return fetch_all(
        """
        SELECT * FROM weight_logs
        WHERE user_id=%s AND log_date BETWEEN %s AND %s
        ORDER BY log_date DESC, created_at DESC
        """,
        (user_id, start_date, end_date),
    )


def create_workout_session(user_id: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        session_id = new_uuid(cursor)
        data = {"session_id": session_id, "user_id": user_id, **payload}
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO workout_sessions ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        cursor.execute("SELECT * FROM workout_sessions WHERE session_id=%s", (session_id,))
        return cursor.fetchone()


def list_workout_sessions(user_id: str, start_date: str, end_date: str):
    return fetch_all(
        """
        SELECT * FROM workout_sessions
        WHERE user_id=%s AND session_date BETWEEN %s AND %s
        ORDER BY session_date DESC, created_at DESC
        """,
        (user_id, start_date, end_date),
    )


def create_meal_log(user_id: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        log_id = new_uuid(cursor)
        data = {"log_id": log_id, "user_id": user_id, **payload}
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO meal_logs ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        cursor.execute("SELECT * FROM meal_logs WHERE log_id=%s", (log_id,))
        return cursor.fetchone()


def list_meal_logs(user_id: str, start_date: str, end_date: str):
    return fetch_all(
        """
        SELECT * FROM meal_logs
        WHERE user_id=%s AND log_date BETWEEN %s AND %s
        ORDER BY log_date DESC, created_at DESC
        """,
        (user_id, start_date, end_date),
    )


def upsert_day_score(user_id: str, score_date: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        cursor.execute(
            """
            INSERT INTO day_scores (
                user_id, score_date, total_score, workout_pts, nutrition_pts, sleep_pts,
                logging_pts, bonus_pts, penalty_pts, workout_done, is_rest_day,
                calories_actual, calories_target, sleep_hours_actual, sleep_hours_target
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                total_score=VALUES(total_score),
                workout_pts=VALUES(workout_pts),
                nutrition_pts=VALUES(nutrition_pts),
                sleep_pts=VALUES(sleep_pts),
                logging_pts=VALUES(logging_pts),
                bonus_pts=VALUES(bonus_pts),
                penalty_pts=VALUES(penalty_pts),
                workout_done=VALUES(workout_done),
                is_rest_day=VALUES(is_rest_day),
                calories_actual=VALUES(calories_actual),
                calories_target=VALUES(calories_target),
                sleep_hours_actual=VALUES(sleep_hours_actual),
                sleep_hours_target=VALUES(sleep_hours_target),
                calculated_at=CURRENT_TIMESTAMP
            """,
            (
                user_id,
                score_date,
                payload.get("total_score"),
                payload.get("workout_pts", 0),
                payload.get("nutrition_pts", 0),
                payload.get("sleep_pts", 0),
                payload.get("logging_pts", 0),
                payload.get("bonus_pts", 0),
                payload.get("penalty_pts", 0),
                payload.get("workout_done", False),
                payload.get("is_rest_day", False),
                payload.get("calories_actual", 0),
                payload.get("calories_target", 0),
                payload.get("sleep_hours_actual", 0.0),
                payload.get("sleep_hours_target", 0.0),
            ),
        )
        cursor.execute(
            "SELECT * FROM day_scores WHERE user_id=%s AND score_date=%s LIMIT 1",
            (user_id, score_date),
        )
        return cursor.fetchone()


def list_day_scores(user_id: str, start_date: str, end_date: str):
    return fetch_all(
        """
        SELECT * FROM day_scores
        WHERE user_id=%s AND score_date BETWEEN %s AND %s
        ORDER BY score_date DESC
        """,
        (user_id, start_date, end_date),
    )


def append_fitness_capability(user_id: str, payload: dict):
    with db_cursor(commit=True) as (_, cursor):
        capability_id = new_uuid(cursor)
        data = {"capability_id": capability_id, "user_id": user_id, **payload}
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        cursor.execute(
            f"INSERT INTO fitness_capabilities ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        cursor.execute("SELECT * FROM fitness_capabilities WHERE capability_id=%s", (capability_id,))
        return cursor.fetchone()


def list_fitness_capabilities(user_id: str):
    return fetch_all(
        """
        SELECT * FROM fitness_capabilities
        WHERE user_id=%s
        ORDER BY recorded_at DESC
        """,
        (user_id,),
    )
