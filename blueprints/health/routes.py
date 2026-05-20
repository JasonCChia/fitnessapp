from flask import Blueprint

from core.responses.api_response import success

health_bp = Blueprint("health", __name__, url_prefix="/health")


@health_bp.get("")
def health():
    return success({"status": "up"}, "Service healthy")


@health_bp.get("/ready")
def ready():
    return success({"ready": True}, "Service ready")
