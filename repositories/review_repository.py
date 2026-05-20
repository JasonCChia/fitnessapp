from datetime import date, timedelta

from db.connection import db_cursor
from repositories.common_repository import fetch_one


def weekly_review_summary(user_id: str):
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    with db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT
              AVG(total_score) AS avg_score,
              SUM(workout_done = TRUE) AS workout_days,
              SUM(calories_actual) AS total_calories
            FROM day_scores
            WHERE user_id=%s AND score_date BETWEEN %s AND %s
            """,
            (user_id, start_date, end_date),
        )
        score_summary = cursor.fetchone()

        cursor.execute(
            """
            SELECT COUNT(*) AS meal_log_count
            FROM meal_logs
            WHERE user_id=%s AND log_date BETWEEN %s AND %s
            """,
            (user_id, start_date, end_date),
        )
        meal_summary = cursor.fetchone()

        cursor.execute(
            """
            SELECT COUNT(*) AS workout_session_count
            FROM workout_sessions
            WHERE user_id=%s AND session_date BETWEEN %s AND %s
            """,
            (user_id, start_date, end_date),
        )
        workout_summary = cursor.fetchone()

    return {
        "window": {"from": start_date.isoformat(), "to": end_date.isoformat()},
        "score_summary": score_summary,
        "meal_summary": meal_summary,
        "workout_summary": workout_summary,
    }


def get_user_preferences(user_id: str):
    return fetch_one("SELECT * FROM user_preferences WHERE user_id=%s LIMIT 1", (user_id,))


def mark_monthly_review_done(user_id: str) -> bool:
    with db_cursor(commit=True) as (_, cursor):
        affected = cursor.execute(
            """
            UPDATE user_preferences
            SET last_monthly_review_at=NOW()
            WHERE user_id=%s
            """,
            (user_id,),
        )
        return affected > 0
