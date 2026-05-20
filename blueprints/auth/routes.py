from flask import Blueprint

from core.responses.api_response import success

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.get("/ping")
def ping_auth():
    return success({"module": "auth"}, "Auth blueprint ready")
