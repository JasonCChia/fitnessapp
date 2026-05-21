from flask import Flask, redirect, session, url_for
from blueprints.admin import admin_bp
from blueprints.ai import ai_bp
from blueprints.api.ai_logs import ai_logs_bp
from blueprints.api.ai_config import ai_config_bp
from blueprints.api.plans import plans_bp
from blueprints.api.reviews import reviews_bp
from blueprints.api.system import system_bp
from blueprints.api.tracking import tracking_bp
from blueprints.api.users import users_bp
from blueprints.auth import auth_bp
from blueprints.health import health_bp
from blueprints.setting.page1 import setting_bp
from blueprints.user._page import user_bp
from config import Config
from services.user import user_service


def create_app():
    app = Flask(
        __name__,
        static_folder="assets",
        static_url_path="/assets",
        template_folder="templates",
    )
    app.config.from_object(Config)

    app.register_blueprint(user_bp)
    app.register_blueprint(setting_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(plans_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(ai_config_bp)
    app.register_blueprint(ai_logs_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(health_bp)

    @app.context_processor
    def inject_current_user():
        user_id = session.get("user_id")
        if not user_id:
            return {"current_user": None}
        user = user_service.get_user(user_id)
        if not user:
            session.pop("user_id", None)
            return {"current_user": None}
        return {"current_user": user}

    @app.get("/")
    def index():
        user_id = session.get("user_id")
        if user_id:
            user = user_service.get_user(user_id)
            if not user:
                session.pop("user_id", None)
                return redirect(url_for("user.login_page"))
            if not user.get("onboarding_done"):
                return redirect(url_for("user.onboarding_page"))
            return redirect(url_for("user.home_page"))
        return redirect(url_for("user.login_page"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
        debug=app.config["DEBUG"],
    )
