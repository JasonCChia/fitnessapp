from flask import Blueprint, redirect, render_template, session, url_for

setting_bp = Blueprint("setting", __name__, url_prefix="/setting")


@setting_bp.before_request
def require_setting_session():
    if session.get("user_id"):
        return None
    return redirect(url_for("user.login_page", next="/setting/"))


@setting_bp.get("/")
def page1():
    return render_template("setting/page1.html")
