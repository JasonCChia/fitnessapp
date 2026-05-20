from datetime import date, timedelta

from repositories import tracking_repository


def resolve_date_range(start: str | None, end: str | None, default_days: int = 30):
    end_date = end or date.today().isoformat()
    date.fromisoformat(end_date)
    if start:
        date.fromisoformat(start)
        return start, end_date
    start_date = date.fromisoformat(end_date) - timedelta(days=default_days)
    return start_date.isoformat(), end_date


def create_weight_log(user_id: str, payload: dict):
    return tracking_repository.create_weight_log(user_id, payload)


def list_weight_logs(user_id: str, start: str | None, end: str | None):
    start_date, end_date = resolve_date_range(start, end, 30)
    return tracking_repository.list_weight_logs(user_id, start_date, end_date)


def create_workout_session(user_id: str, payload: dict):
    return tracking_repository.create_workout_session(user_id, payload)


def list_workout_sessions(user_id: str, start: str | None, end: str | None):
    start_date, end_date = resolve_date_range(start, end, 30)
    return tracking_repository.list_workout_sessions(user_id, start_date, end_date)


def create_meal_log(user_id: str, payload: dict):
    return tracking_repository.create_meal_log(user_id, payload)


def list_meal_logs(user_id: str, start: str | None, end: str | None):
    start_date, end_date = resolve_date_range(start, end, 30)
    return tracking_repository.list_meal_logs(user_id, start_date, end_date)


def upsert_day_score(user_id: str, score_date: str, payload: dict):
    date.fromisoformat(score_date)
    return tracking_repository.upsert_day_score(user_id, score_date, payload)


def list_day_scores(user_id: str, start: str | None, end: str | None):
    start_date, end_date = resolve_date_range(start, end, 7)
    return tracking_repository.list_day_scores(user_id, start_date, end_date)


def append_fitness_capability(user_id: str, payload: dict):
    return tracking_repository.append_fitness_capability(user_id, payload)


def list_fitness_capabilities(user_id: str):
    rows = tracking_repository.list_fitness_capabilities(user_id)
    return {"latest": rows[0] if rows else None, "history": rows}
