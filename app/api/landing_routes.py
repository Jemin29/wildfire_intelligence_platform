from flask import Blueprint, render_template

landing_bp = Blueprint("landing", __name__)


@landing_bp.get("/")
def home():
    return render_template("landing.html")
