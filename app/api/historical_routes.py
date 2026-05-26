from flask import Blueprint, render_template

historical_bp = Blueprint("historical", __name__)


@historical_bp.get("/historical")
def historical_page():
    return render_template("historical.html", active_page="historical")
