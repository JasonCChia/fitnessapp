import json

from flask import Blueprint, request

from core.exceptions.app_exceptions import ValidationError
from core.responses.api_response import error, success
from core.utils.serialization import row_to_json_safe, rows_to_json_safe
from schemas.request.json_body import get_json_body
from schemas.validators.payload_validator import (
    validate_payload_columns,
    validate_required_insert_fields,
)
from services.tracking import tracking_service

tracking_bp = Blueprint("tracking_api", __name__, url_prefix="/api/users/<string:user_id>")


@tracking_bp.post("/weight-logs")
def create_weight_log(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(payload, "weight_logs", excluded={"log_id", "user_id", "created_at"})
        validate_required_insert_fields(
            {"user_id": user_id, **payload},
            "weight_logs",
            excluded={"log_id", "created_at"},
        )
        row = tracking_service.create_weight_log(user_id, payload)
        return success(row_to_json_safe(row), "Weight log created", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to create weight log", 500, str(exc))


@tracking_bp.get("/weight-logs")
def list_weight_logs(user_id: str):
    try:
        rows = tracking_service.list_weight_logs(
            user_id,
            request.args.get("from"),
            request.args.get("to"),
        )
        return success(rows_to_json_safe(rows))
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        return error("Failed to list weight logs", 500, str(exc))


@tracking_bp.post("/workout-sessions")
def create_workout_session(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(payload, "workout_sessions", excluded={"session_id", "user_id", "created_at"})
        validate_required_insert_fields(
            {"user_id": user_id, **payload},
            "workout_sessions",
            excluded={"session_id", "created_at"},
        )
        payload["exercises_log"] = json.dumps(payload.get("exercises_log", []))
        row = tracking_service.create_workout_session(user_id, payload)
        return success(row_to_json_safe(row), "Workout session created", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to create workout session", 500, str(exc))


@tracking_bp.get("/workout-sessions")
def list_workout_sessions(user_id: str):
    try:
        rows = tracking_service.list_workout_sessions(
            user_id,
            request.args.get("from"),
            request.args.get("to"),
        )
        return success(rows_to_json_safe(rows))
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        return error("Failed to list workout sessions", 500, str(exc))


@tracking_bp.post("/meal-logs")
def create_meal_log(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(payload, "meal_logs", excluded={"log_id", "user_id", "created_at"})
        validate_required_insert_fields(
            {"user_id": user_id, **payload},
            "meal_logs",
            excluded={"log_id", "created_at"},
        )
        row = tracking_service.create_meal_log(user_id, payload)
        return success(row_to_json_safe(row), "Meal log created", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to create meal log", 500, str(exc))


@tracking_bp.get("/meal-logs")
def list_meal_logs(user_id: str):
    try:
        rows = tracking_service.list_meal_logs(
            user_id,
            request.args.get("from"),
            request.args.get("to"),
        )
        return success(rows_to_json_safe(rows))
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        return error("Failed to list meal logs", 500, str(exc))


@tracking_bp.put("/day-scores/<string:score_date>")
def upsert_day_score(user_id: str, score_date: str):
    try:
        payload = get_json_body()
        validate_payload_columns(
            payload,
            "day_scores",
            excluded={"score_id", "user_id", "score_date", "calculated_at"},
        )
        validate_required_insert_fields(
            {"user_id": user_id, "score_date": score_date, **payload},
            "day_scores",
            excluded={"score_id", "calculated_at"},
        )
        row = tracking_service.upsert_day_score(user_id, score_date, payload)
        return success(row_to_json_safe(row), "Day score saved")
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        return error("Failed to save day score", 500, str(exc))


@tracking_bp.get("/day-scores")
def list_day_scores(user_id: str):
    try:
        rows = tracking_service.list_day_scores(
            user_id,
            request.args.get("from"),
            request.args.get("to"),
        )
        return success(rows_to_json_safe(rows))
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        return error("Failed to list day scores", 500, str(exc))


@tracking_bp.post("/fitness-capabilities")
def append_fitness_capability(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(
            payload,
            "fitness_capabilities",
            excluded={"capability_id", "user_id", "recorded_at"},
        )
        validate_required_insert_fields(
            {"user_id": user_id, **payload},
            "fitness_capabilities",
            excluded={"capability_id", "recorded_at"},
        )
        row = tracking_service.append_fitness_capability(user_id, payload)
        return success(row_to_json_safe(row), "Fitness capability snapshot added", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to append fitness capability", 500, str(exc))


@tracking_bp.get("/fitness-capabilities")
def list_fitness_capabilities(user_id: str):
    try:
        data = tracking_service.list_fitness_capabilities(user_id)
        return success(
            {
                "latest": row_to_json_safe(data["latest"]),
                "history": rows_to_json_safe(data["history"]),
            }
        )
    except Exception as exc:
        return error("Failed to list fitness capabilities", 500, str(exc))
