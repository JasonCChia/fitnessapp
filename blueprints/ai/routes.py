from pathlib import Path
from uuid import uuid4

from flask import Blueprint, request
from werkzeug.utils import secure_filename

from core.responses.api_response import error, success
from core.security import get_authenticated_user_id
from schemas.request.json_body import get_json_body
from services.ai.main import AIService
from services.ai_log import ai_log_service
from services.user import user_service

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")
ai_service = AIService()


@ai_bp.get("/ping")
def ping_ai():
    return success({"module": "ai"}, "AI blueprint ready")


@ai_bp.post("/revise-proposal")
def revise_proposal():
    user_id, auth_error = get_authenticated_user_id()
    if auth_error:
        return auth_error

    try:
        payload = get_json_body()
        feedback = (payload.get("feedback") or "").strip()
        prefs = user_service.get_user_preferences(user_id)
        provider_cfg = ai_service.resolve_provider()

        target_calories = int(payload.get("target_calories") or 0) or 2100
        target_protein_g = int(payload.get("target_protein_g") or 0) or 145
        target_carbs_g = int(payload.get("target_carbs_g") or 0) or 230
        target_fat_g = int(payload.get("target_fat_g") or 0) or 70
        sleep_hours = float((prefs or {}).get("sleep_target_hours") or 8.0)

        ai_result = ai_service.revise_proposal(
            provider=provider_cfg["provider"],
            api_key=provider_cfg["api_key"],
            model=provider_cfg["model"],
            feedback=feedback,
            target_calories=target_calories,
            target_protein_g=target_protein_g,
            target_carbs_g=target_carbs_g,
            target_fat_g=target_fat_g,
            sleep_target_hours=sleep_hours,
        )
        if ai_result.get("status") != "ok":
            return error(ai_result.get("error") or "Failed to revise proposal", 400)
        revised = ai_result["data"]

        ai_log_service.create_ai_request_log(
            user_id=user_id,
            payload={
                "provider": provider_cfg["provider"],
                "model_name": ai_result.get("model") or provider_cfg["model"],
                "method_name": "reviseProposal",
                "request_payload": payload,
                "response_payload": revised,
                "input_tokens": int((ai_result.get("usage") or {}).get("input_tokens") or 0),
                "output_tokens": int((ai_result.get("usage") or {}).get("output_tokens") or 0),
                "status": "success",
                "error_message": None,
            },
        )

        return success({"revised": revised}, "Revisi AI berhasil dibuat")
    except Exception as exc:
        return error("Failed to revise proposal", 500, str(exc))


@ai_bp.post("/analyze-food-photo")
def analyze_food_photo():
    user_id, auth_error = get_authenticated_user_id()
    if auth_error:
        return auth_error

    file = request.files.get("food_image")
    if not file or not file.filename:
        return error("Food image is required", 400)

    safe_name = secure_filename(file.filename)
    ext = Path(safe_name).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        return error("Unsupported image format", 400)

    temp_dir = Path("storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    saved_path = temp_dir / f"{uuid4().hex}{ext}"
    file.save(saved_path)

    try:
        provider_cfg = ai_service.resolve_provider()
        detect = ai_service.analyze_food_photo(
            provider=provider_cfg["provider"],
            api_key=provider_cfg["api_key"],
            model=provider_cfg["model"],
            image_path=str(saved_path),
        )
        if detect.get("status") != "ok":
            return error(detect.get("error") or "Failed to analyze image", 400)
        result = detect.get("data") or {}

        ai_log_service.create_ai_request_log(
            user_id=user_id,
            payload={
                "provider": provider_cfg["provider"],
                "model_name": detect.get("model") or provider_cfg["model"],
                "method_name": "analyzeFoodPhoto",
                "request_payload": {"filename": safe_name},
                "response_payload": result,
                "input_tokens": int((detect.get("usage") or {}).get("input_tokens") or 0),
                "output_tokens": int((detect.get("usage") or {}).get("output_tokens") or 0),
                "status": "success",
                "error_message": None,
            },
        )
        return success(result, "Food photo analyzed")
    except Exception as exc:
        return error("Failed to analyze food photo", 500, str(exc))
    finally:
        try:
            saved_path.unlink(missing_ok=True)
        except OSError:
            pass
