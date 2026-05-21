from flask import Blueprint, redirect, render_template, session, url_for
from services.user import user_service

setting_bp = Blueprint("setting", __name__, url_prefix="/setting")


@setting_bp.before_request
def require_setting_session():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user.login_page", next="/setting/"))

    user = user_service.get_user(user_id)
    if not user:
        session.pop("user_id", None)
        return redirect(url_for("user.login_page", next="/setting/"))

    if not user.get("onboarding_done"):
        return redirect(url_for("user.onboarding_page"))
    return None


@setting_bp.get("/")
def page1():
    return render_template("setting/page1.html")
