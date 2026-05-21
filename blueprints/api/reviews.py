from flask import Blueprint, request

from core.responses.api_response import error, success
from core.security import ensure_user_scope
from core.utils.serialization import row_to_json_safe
from services.review import review_service

reviews_bp = Blueprint("reviews_api", __name__, url_prefix="/api/users/<string:user_id>/reviews")


@reviews_bp.before_request
def authorize_review_routes():
    route_user_id = request.view_args.get("user_id") if request.view_args else None
    return ensure_user_scope(route_user_id)


@reviews_bp.get("/weekly")
def weekly_review_data(user_id: str):
    try:
        data = review_service.weekly_review(user_id)
        data["score_summary"] = row_to_json_safe(data["score_summary"])
        data["meal_summary"] = row_to_json_safe(data["meal_summary"])
        data["workout_summary"] = row_to_json_safe(data["workout_summary"])
        return success(data)
    except Exception as exc:
        return error("Failed to build weekly review data", 500, str(exc))


@reviews_bp.post("/monthly/check-trigger")
def monthly_review_trigger_check(user_id: str):
    try:
        data = review_service.monthly_trigger_check(user_id)
        if not data:
            return error("Preferences not found", 404)
        return success(data)
    except Exception as exc:
        return error("Failed to evaluate monthly review trigger", 500, str(exc))


@reviews_bp.post("/monthly/mark-done")
def monthly_review_mark_done(user_id: str):
    try:
        row = review_service.monthly_mark_done(user_id)
        if not row:
            return error("Preferences not found", 404)
        return success(row_to_json_safe(row), "Monthly review timestamp updated")
    except Exception as exc:
        return error("Failed to update monthly review timestamp", 500, str(exc))
