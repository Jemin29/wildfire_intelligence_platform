from flask import Blueprint, render_template

ai_insights_bp = Blueprint("ai_insights", __name__)


@ai_insights_bp.get("/model-insights")
def model_insights_page():
    return render_template("model_insights.html", active_page="model_insights")
