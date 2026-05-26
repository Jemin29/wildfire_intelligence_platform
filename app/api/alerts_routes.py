from flask import Blueprint, render_template

alerts_page_bp = Blueprint("alerts_page", __name__)


@alerts_page_bp.get("/alerts")
def alerts_page():
    return render_template("alerts.html", active_page="alerts")
