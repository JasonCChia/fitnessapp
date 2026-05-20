from core.exceptions.app_exceptions import AppError
from core.responses.api_response import error, success
from core.utils.serialization import row_to_json_safe
from flask import Blueprint
from services.system.system_service import health_db, init_db

system_bp = Blueprint("system_api", __name__, url_prefix="/api/system")


@system_bp.get("/health/db")
def db_health():
    try:
        row = health_db()
        return success(row_to_json_safe(row), message="Database connection is healthy")
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.detail)
    except Exception as exc:
        return error("MySQL connection failed", 500, str(exc))


@system_bp.post("/init-db")
def initialize_db():
    try:
        result = init_db()
        return success(result, message="Schema initialized")
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.detail)
    except Exception as exc:
        return error("Failed to initialize schema", 500, str(exc))
