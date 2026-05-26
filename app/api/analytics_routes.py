from flask import Blueprint, render_template

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/analytics")
def analytics_page():
    return render_template("analytics.html", active_page="analytics")
