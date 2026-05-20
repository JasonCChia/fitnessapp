from flask import Flask, render_template
from blueprints.admin import admin_bp
from blueprints.ai import ai_bp
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
    app.register_blueprint(reviews_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(health_bp)

    @app.get("/")
    def index():
        return render_template("user/home.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
        debug=app.config["DEBUG"],
    )
