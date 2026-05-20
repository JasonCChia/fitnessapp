from flask import Blueprint, request

from core.exceptions.app_exceptions import ValidationError
from core.responses.api_response import error, success
from core.utils.serialization import row_to_json_safe, rows_to_json_safe
from schemas.request.json_body import get_json_body
from schemas.validators.payload_validator import (
    validate_payload_columns,
    validate_required_insert_fields,
)
from services.user import user_service

users_bp = Blueprint("users_api", __name__, url_prefix="/api/users")


@users_bp.post("")
def create_user():
    try:
        payload = get_json_body()
        validate_payload_columns(payload, "users", excluded={"user_id", "created_at"})
        validate_required_insert_fields(payload, "users", excluded={"user_id", "created_at"})
        row = user_service.create_user(payload)
        return success(row_to_json_safe(row), "User created", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to create user", 500, str(exc))


@users_bp.get("")
def list_users():
    try:
        rows = user_service.list_users()
        return success(rows_to_json_safe(rows))
    except Exception as exc:
        return error("Failed to list users", 500, str(exc))


@users_bp.get("/<string:user_id>")
def get_user(user_id: str):
    try:
        row = user_service.get_user(user_id)
        if not row:
            return error("User not found", 404)
        return success(row_to_json_safe(row))
    except Exception as exc:
        return error("Failed to fetch user", 500, str(exc))


@users_bp.patch("/<string:user_id>")
def update_user(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(payload, "users", excluded={"user_id", "created_at"})
        if not payload:
            return error("No fields provided for update", 400)
        row = user_service.update_user(user_id, payload)
        if not row:
            return error("User not found", 404)
        return success(row_to_json_safe(row), "User updated")
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to update user", 500, str(exc))


@users_bp.put("/<string:user_id>/preferences")
def upsert_user_preferences(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(payload, "user_preferences", excluded={"pref_id", "user_id", "updated_at"})
        validate_required_insert_fields(
            {"user_id": user_id, **payload},
            "user_preferences",
            excluded={"pref_id", "updated_at"},
        )
        row = user_service.upsert_user_preferences(user_id, payload)
        if not row:
            return error("User not found", 404)
        return success(row_to_json_safe(row), "Preferences saved")
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to save preferences", 500, str(exc))


@users_bp.get("/<string:user_id>/preferences")
def get_user_preferences(user_id: str):
    try:
        row = user_service.get_user_preferences(user_id)
        if not row:
            return error("Preferences not found", 404)
        return success(row_to_json_safe(row))
    except Exception as exc:
        return error("Failed to fetch preferences", 500, str(exc))


@users_bp.post("/<string:user_id>/food-preferences")
def create_food_preference(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(
            payload,
            "food_preferences",
            excluded={"preference_id", "user_id", "created_at", "deleted_at"},
        )
        validate_required_insert_fields(
            {"user_id": user_id, **payload},
            "food_preferences",
            excluded={"preference_id", "created_at", "deleted_at"},
        )
        row = user_service.create_food_preference(user_id, payload)
        return success(row_to_json_safe(row), "Food preference created", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to create food preference", 500, str(exc))


@users_bp.get("/<string:user_id>/food-preferences")
def list_food_preferences(user_id: str):
    try:
        include_deleted = request.args.get("include_deleted", "false").lower() == "true"
        rows = user_service.list_food_preferences(user_id, include_deleted)
        return success(rows_to_json_safe(rows))
    except Exception as exc:
        return error("Failed to list food preferences", 500, str(exc))


@users_bp.delete("/<string:user_id>/food-preferences/<string:preference_id>")
def soft_delete_food_preference(user_id: str, preference_id: str):
    try:
        ok = user_service.soft_delete_food_preference(user_id, preference_id)
        if not ok:
            return error("Food preference not found", 404)
        return success(message="Food preference soft-deleted")
    except Exception as exc:
        return error("Failed to delete food preference", 500, str(exc))


@users_bp.post("/onboarding")
def onboarding():
    try:
        payload = get_json_body()
        user_payload = payload.get("user", {})
        preferences_payload = payload.get("preferences", {})
        food_preferences = payload.get("food_preferences", [])
        fitness_snapshot = payload.get("fitness_capability")

        if not isinstance(user_payload, dict) or not isinstance(preferences_payload, dict):
            return error("Fields 'user' and 'preferences' must be objects", 400)
        if not isinstance(food_preferences, list):
            return error("Field 'food_preferences' must be an array", 400)
        if fitness_snapshot is not None and not isinstance(fitness_snapshot, dict):
            return error("Field 'fitness_capability' must be an object", 400)

        validate_payload_columns(user_payload, "users", excluded={"user_id", "created_at", "onboarding_done"})
        validate_required_insert_fields(
            user_payload,
            "users",
            excluded={"user_id", "created_at", "onboarding_done"},
        )
        validate_payload_columns(
            preferences_payload,
            "user_preferences",
            excluded={"pref_id", "user_id", "updated_at"},
        )
        validate_required_insert_fields(
            {"user_id": "temp", **preferences_payload},
            "user_preferences",
            excluded={"pref_id", "user_id", "updated_at"},
        )

        for pref in food_preferences:
            if not isinstance(pref, dict):
                return error("Each item in 'food_preferences' must be an object", 400)
            validate_payload_columns(
                pref,
                "food_preferences",
                excluded={"preference_id", "user_id", "created_at", "deleted_at"},
            )
            validate_required_insert_fields(
                {"user_id": "temp", **pref},
                "food_preferences",
                excluded={"preference_id", "user_id", "created_at", "deleted_at"},
            )

        if fitness_snapshot is not None:
            validate_payload_columns(
                fitness_snapshot,
                "fitness_capabilities",
                excluded={"capability_id", "user_id", "recorded_at"},
            )
            validate_required_insert_fields(
                {"user_id": "temp", **fitness_snapshot},
                "fitness_capabilities",
                excluded={"capability_id", "user_id", "recorded_at"},
            )

        user_id = user_service.onboarding(
            user_payload=user_payload,
            preferences_payload=preferences_payload,
            food_preferences=food_preferences,
            fitness_snapshot=fitness_snapshot,
        )

        user = user_service.get_user(user_id)
        preferences = user_service.get_user_preferences(user_id)
        preference_rows = user_service.list_food_preferences(user_id, include_deleted=False)
        response_data = {
            "user": row_to_json_safe(user),
            "preferences": row_to_json_safe(preferences),
            "food_preferences": rows_to_json_safe(preference_rows),
        }
        return success(response_data, "Onboarding completed", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to process onboarding", 500, str(exc))
