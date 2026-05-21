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
from services.ai_log import ai_log_service

ai_logs_bp = Blueprint("ai_logs_api", __name__, url_prefix="/api/users/<string:user_id>/ai-request-logs")


@ai_logs_bp.before_request
def authorize_ai_log_routes():
    route_user_id = request.view_args.get("user_id") if request.view_args else None
    return ensure_user_scope(route_user_id)


@ai_logs_bp.post("")
def create_ai_request_log(user_id: str):
    try:
        payload = get_json_body()
        validate_payload_columns(
            payload,
            "ai_request_logs",
            excluded={"log_id", "user_id", "requested_at", "total_tokens"},
        )
        validate_required_insert_fields(
            {"user_id": user_id, **payload},
            "ai_request_logs",
            excluded={"log_id", "requested_at", "total_tokens"},
        )
        row = ai_log_service.create_ai_request_log(user_id, payload)
        return success(row_to_json_safe(row), "AI request log created", 201)
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        return error("Failed to create AI request log", 500, str(exc))


@ai_logs_bp.get("")
def list_ai_request_logs(user_id: str):
    try:
        rows = ai_log_service.list_ai_request_logs(
            user_id=user_id,
            provider=request.args.get("provider"),
            method_name=request.args.get("method_name"),
            status=request.args.get("status"),
            limit=request.args.get("limit", 50),
        )
        total_input_tokens = sum(int(row.get("input_tokens") or 0) for row in rows)
        total_output_tokens = sum(int(row.get("output_tokens") or 0) for row in rows)
        return success(
            {
                "items": rows_to_json_safe(rows),
                "summary": {
                    "count": len(rows),
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "total_tokens": total_input_tokens + total_output_tokens,
                },
            }
        )
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        return error("Failed to list AI request logs", 500, str(exc))
