from flask import Blueprint, render_template

setting_bp = Blueprint("setting", __name__, url_prefix="/setting")


@setting_bp.get("/")
def page1():
    return render_template("setting/page1.html")
