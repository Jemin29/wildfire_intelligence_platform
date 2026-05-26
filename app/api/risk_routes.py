from flask import Blueprint, render_template

risk_bp = Blueprint("risk", __name__)


@risk_bp.get("/risk")
def risk_page():
    return render_template("risk.html", active_page="risk")
