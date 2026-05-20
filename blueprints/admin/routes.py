from flask import Blueprint

from core.responses.api_response import success

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/ping")
def ping_admin():
    return success({"module": "admin"}, "Admin blueprint ready")
