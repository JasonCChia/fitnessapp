from flask import Blueprint, redirect, render_template, request, session, url_for

from services.auth import auth_service
from services.user import user_service

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.before_request
def require_session_login():
    if request.endpoint in {
        "user.login_page",
        "user.login_submit",
        "user.register_page",
        "user.register_submit",
    }:
        return None

    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user.login_page", next=request.path))

    user = user_service.get_user(user_id)
    if not user:
        session.pop("user_id", None)
        return redirect(url_for("user.login_page", next=request.path))

    if not user.get("onboarding_done") and request.endpoint not in {"user.onboarding_page", "user.logout_submit"}:
        return redirect(url_for("user.onboarding_page"))

    return None


@user_bp.get("/login")
def login_page():
    user_id = session.get("user_id")
    if user_id:
        user = user_service.get_user(user_id)
        if user and not user.get("onboarding_done"):
            return redirect(url_for("user.onboarding_page"))
        if user:
            return redirect(url_for("user.home_page"))
        session.pop("user_id", None)
    return render_template("user/login.html", error=None)


@user_bp.post("/login")
def login_submit():
    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    if not email or not password:
        return render_template("user/login.html", error="Email dan password wajib diisi"), 400

    auth_user = user_service.get_user_auth_by_email(email)
    if not auth_user or not auth_service.verify_password(password, auth_user["password_hash"]):
        return render_template("user/login.html", error="Email atau password salah"), 401

    session["user_id"] = auth_user["user_id"]
    user = user_service.get_user(auth_user["user_id"])
    if user and not user.get("onboarding_done"):
        return redirect(url_for("user.onboarding_page"))

    next_path = request.form.get("next") or request.args.get("next")
    if next_path and next_path.startswith("/"):
        return redirect(next_path)
    return redirect(url_for("user.home_page"))


@user_bp.get("/register")
def register_page():
    user_id = session.get("user_id")
    if user_id:
        user = user_service.get_user(user_id)
        if user and not user.get("onboarding_done"):
            return redirect(url_for("user.onboarding_page"))
        if user:
            return redirect(url_for("user.home_page"))
        session.pop("user_id", None)
    return render_template("user/register.html", error=None)


@user_bp.post("/register")
def register_submit():
    form = request.form
    name = (form.get("name") or "").strip()
    email = (form.get("email") or "").strip()
    gender = (form.get("gender") or "").strip()
    birth_date = (form.get("birth_date") or "").strip()
    height_raw = (form.get("height_cm") or "").strip()
    password = form.get("password") or ""

    if not all([name, email, gender, birth_date, height_raw, password]):
        return render_template("user/register.html", error="Semua field wajib diisi"), 400

    if len(password) < 8:
        return render_template("user/register.html", error="Password minimal 8 karakter"), 400

    try:
        height_cm = float(height_raw)
    except ValueError:
        return render_template("user/register.html", error="Tinggi badan harus berupa angka"), 400

    if user_service.get_user_by_email(email):
        return render_template("user/register.html", error="Email sudah terdaftar"), 409

    payload = {
        "name": name,
        "email": email,
        "gender": gender,
        "birth_date": birth_date,
        "height_cm": height_cm,
        "password_hash": auth_service.hash_password(password),
    }

    try:
        row = user_service.create_user(payload)
    except Exception:
        return render_template("user/register.html", error="Gagal membuat akun, coba lagi"), 500

    session["user_id"] = row["user_id"]
    return redirect(url_for("user.onboarding_page"))


@user_bp.post("/logout")
def logout_submit():
    session.pop("user_id", None)
    return redirect(url_for("user.login_page"))


@user_bp.get("/")
def user_home():
    return redirect(url_for("user.home_page"))


@user_bp.get("/onboarding")
def onboarding_page():
    return render_template("user/onboarding.html")


@user_bp.get("/ai-setup")
def ai_setup_page():
    return render_template("user/ai_setup.html")


@user_bp.get("/home")
def home_page():
    return render_template("user/home.html")


@user_bp.get("/nutrition")
def nutrition_page():
    return render_template("user/log_meals.html")


@user_bp.get("/workout")
def workout_page():
    return render_template("user/log_workout.html")


@user_bp.get("/log-meals")
def log_meals_page():
    return render_template("user/log_meals.html")


@user_bp.get("/log-workout")
def log_workout_page():
    return render_template("user/log_workout.html")


@user_bp.get("/workout-program")
def workout_program_page():
    return render_template("user/workout_program.html")


@user_bp.get("/meal-plan")
def meal_plan_page():
    return render_template("user/meal_plan.html")


@user_bp.get("/progress")
def progress_page():
    return render_template("user/progress.html")


@user_bp.get("/weekly-review")
def weekly_review_page():
    return render_template("user/weekly_review.html")
