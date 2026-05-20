from flask import Blueprint

from core.responses.api_response import success

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.get("/ping")
def ping_ai():
    return success({"module": "ai"}, "AI blueprint ready")
