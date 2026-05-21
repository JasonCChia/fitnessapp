from flask import Blueprint, session

from core.exceptions.app_exceptions import ValidationError
from core.responses.api_response import error, success
from core.security import get_authenticated_user_id
from core.utils.serialization import sanitize_user_row
from schemas.request.json_body import get_json_body
from schemas.validators.payload_validator import (
    validate_payload_columns,
    validate_required_insert_fields,
)
from services.auth import auth_service
from services.user import user_service

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _extract_password(payload: dict):
    password = payload.pop("password", None)
    if not isinstance(password, str) or len(password.strip()) < 8:
        raise ValidationError("Field 'password' is required and must be at least 8 characters")
    return password


@auth_bp.post("/register")
def register():
    try:
        payload = get_json_body()
        password = _extract_password(payload)

        validate_payload_columns(
            payload,
            "users",
            excluded={"user_id", "created_at", "onboarding_done", "password_hash"},
        )
        validate_required_insert_fields(
            payload,
            "users",
            excluded={"user_id", "created_at", "onboarding_done", "password_hash"},
        )

        email = payload.get("email")
        if not email:
            return error("Email is required", 400)

        if user_service.get_user_by_email(email):
            return error("Email already registered", 409)

        payload["password_hash"] = auth_service.hash_password(password)
        row = user_service.create_user(payload)
        token = auth_service.issue_access_token(row["user_id"])
        session["user_id"] = row["user_id"]
        return success(
            {"access_token": token, "token_type": "Bearer", "user": sanitize_user_row(row)},
            "Register success",
            201,
        )
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to register", 500, str(exc))


@auth_bp.post("/login")
def login():
    try:
        payload = get_json_body()
        email = payload.get("email")
        password = payload.get("password")
        if not isinstance(email, str) or not isinstance(password, str):
            return error("Fields 'email' and 'password' are required", 400)

        auth_user = user_service.get_user_auth_by_email(email)
        if not auth_user:
            return error("Invalid email or password", 401)

        if not auth_service.verify_password(password, auth_user["password_hash"]):
            return error("Invalid email or password", 401)

        user = user_service.get_user(auth_user["user_id"])
        token = auth_service.issue_access_token(auth_user["user_id"])
        session["user_id"] = auth_user["user_id"]
        return success(
            {"access_token": token, "token_type": "Bearer", "user": sanitize_user_row(user)},
            "Login success",
        )
    except ValidationError as exc:
        return error(exc.message, 400, exc.detail)
    except Exception as exc:
        return error("Failed to login", 500, str(exc))


@auth_bp.get("/me")
def me():
    user_id, auth_error = get_authenticated_user_id()
    if auth_error:
        return auth_error

    user = user_service.get_user(user_id)
    if not user:
        return error("User not found", 404)
    return success({"user": sanitize_user_row(user)})


@auth_bp.post("/logout")
def logout():
    session.pop("user_id", None)
    return success(message="Logout success")


@auth_bp.get("/ping")
def ping_auth():
    return success({"module": "auth"}, "Auth blueprint ready")
