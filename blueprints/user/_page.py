from flask import Blueprint, render_template

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.get("/")
def user_home():
    return render_template("user/home.html")


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
