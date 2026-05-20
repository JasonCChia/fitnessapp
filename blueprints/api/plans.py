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
from services.plan import plan_service

plans_bp = Blueprint("plans_api", __name__, url_prefix="/api/users/<string:user_id>")


@plans_bp.post("/workout-plans")
def create_workout_plan(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(payload, "workout_plans", excluded={"plan_id", "user_id", "created_at", "archived_at"})
        validate_required_insert_fields(
            {"user_id": user_id, **payload},
            "workout_plans",
            excluded={"plan_id", "created_at", "archived_at"},
        )
        payload["weeks_data"] = json.dumps(payload.get("weeks_data", {}))
        row = plan_service.create_workout_plan(user_id, payload)
        return success(row_to_json_safe(row), "Workout plan created", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to create workout plan", 500, str(exc))


@plans_bp.get("/workout-plans")
def list_workout_plans(user_id: str):
    try:
        rows = plan_service.list_workout_plans(user_id, request.args.get("status"))
        return success(rows_to_json_safe(rows))
    except Exception as exc:
        return error("Failed to list workout plans", 500, str(exc))


@plans_bp.post("/workout-plans/<string:plan_id>/activate")
def activate_workout_plan(user_id: str, plan_id: str):
    try:
        row = plan_service.activate_workout_plan(user_id, plan_id)
        if not row:
            return error("Workout plan not found", 404)
        return success(row_to_json_safe(row), "Workout plan activated")
    except Exception as exc:
        return error("Failed to activate workout plan", 500, str(exc))


@plans_bp.post("/meal-plans")
def create_meal_plan(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(payload, "meal_plans", excluded={"plan_id", "user_id", "created_at"})
        validate_required_insert_fields(
            {"user_id": user_id, **payload},
            "meal_plans",
            excluded={"plan_id", "created_at"},
        )
        payload["days_data"] = json.dumps(payload.get("days_data", {}))
        if payload.get("preference_snapshot") is not None:
            payload["preference_snapshot"] = json.dumps(payload["preference_snapshot"])
        row = plan_service.create_meal_plan(user_id, payload)
        return success(row_to_json_safe(row), "Meal plan created", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to create meal plan", 500, str(exc))


@plans_bp.get("/meal-plans")
def list_meal_plans(user_id: str):
    try:
        rows = plan_service.list_meal_plans(user_id, request.args.get("status"))
        return success(rows_to_json_safe(rows))
    except Exception as exc:
        return error("Failed to list meal plans", 500, str(exc))


@plans_bp.post("/meal-plans/<string:plan_id>/activate")
def activate_meal_plan(user_id: str, plan_id: str):
    try:
        row = plan_service.activate_meal_plan(user_id, plan_id)
        if not row:
            return error("Meal plan not found", 404)
        return success(row_to_json_safe(row), "Meal plan activated")
    except Exception as exc:
        return error("Failed to activate meal plan", 500, str(exc))


@plans_bp.get("/active-program")
def get_active_program(user_id: str):
    try:
        data = plan_service.get_active_program(user_id)
        return success(
            {
                "workout_plan": row_to_json_safe(data["workout_plan"]),
                "meal_plan": row_to_json_safe(data["meal_plan"]),
            }
        )
    except Exception as exc:
        return error("Failed to fetch active program", 500, str(exc))
