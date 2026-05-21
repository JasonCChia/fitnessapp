from flask import g, request, session

from core.responses.api_response import error
from services.auth import auth_service


def get_authenticated_user_id():
    session_user_id = session.get("user_id")
    if isinstance(session_user_id, str) and session_user_id:
        g.current_user_id = session_user_id
        return session_user_id, None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        return None, error("Authentication required", 401)
    if not auth_header.startswith("Bearer "):
        return None, error("Invalid Authorization header", 401)

    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        return None, error("Missing bearer token", 401)

    user_id = auth_service.verify_access_token(token)
    if not user_id:
        return None, error("Invalid or expired token", 401)

    g.current_user_id = user_id
    return user_id, None


def ensure_user_scope(route_user_id: str | None):
    user_id, auth_error = get_authenticated_user_id()
    if auth_error:
        return auth_error

    if route_user_id and route_user_id != user_id:
        return error("Forbidden: you can only access your own user data", 403)
    return None
