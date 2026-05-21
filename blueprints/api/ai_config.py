from flask import Blueprint, request

from core.exceptions.app_exceptions import ValidationError
from core.responses.api_response import error, success
from core.security import ensure_user_scope
from core.utils.serialization import row_to_json_safe, rows_to_json_safe
from schemas.request.json_body import get_json_body
from schemas.validators.payload_validator import (
    validate_payload_columns,
    validate_required_insert_fields,
)
from services.prompt import prompt_service

ai_config_bp = Blueprint("ai_config_api", __name__, url_prefix="/api/users/<string:user_id>/ai-prompts")


@ai_config_bp.before_request
def authorize_prompt_routes():
    route_user_id = request.view_args.get("user_id") if request.view_args else None
    return ensure_user_scope(route_user_id)


@ai_config_bp.get("")
def list_ai_prompt_configs(user_id: str):
    try:
        rows = prompt_service.list_ai_prompt_configs(user_id, request.args.get("method_name"))
        return success(rows_to_json_safe(rows))
    except Exception as exc:
        return error("Failed to list AI prompt configs", 500, str(exc))


@ai_config_bp.put("/<string:method_name>")
def upsert_ai_prompt_config(user_id: str, method_name: str):
    try:
        payload = get_json_body()
        validate_payload_columns(
            payload,
            "ai_prompt_configs",
            excluded={"config_id", "user_id", "method_name", "updated_at"},
        )
        validate_required_insert_fields(
            {"user_id": user_id, "method_name": method_name, **payload},
            "ai_prompt_configs",
            excluded={"config_id", "updated_at"},
        )
        row = prompt_service.upsert_ai_prompt_config(user_id, method_name, payload)
        return success(row_to_json_safe(row), "AI prompt config saved")
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to save AI prompt config", 500, str(exc))
