from flask import Blueprint, request

from app.core.api_utils import ok
from app.services.ai_insights_service import AIInsightsService

ai_insights_api_bp = Blueprint("ai_insights_api", __name__)


@ai_insights_api_bp.get("/api/insights/feature-importance")
def feature_importance():
    service = AIInsightsService()
    return ok(service.feature_importance())


@ai_insights_api_bp.get("/api/insights/shap")
def shap_summary():
    service = AIInsightsService()
    return ok(service.shap_summary())


@ai_insights_api_bp.get("/api/insights/prediction/<int:prediction_id>")
def prediction_explanation(prediction_id: int):
    service = AIInsightsService()
    return ok(service.prediction_explanation(prediction_id))


@ai_insights_api_bp.get("/api/insights/metrics")
def model_metrics():
    service = AIInsightsService()
    return ok(service.model_metrics())


@ai_insights_api_bp.get("/api/insights/confusion-matrix")
def confusion_matrix():
    service = AIInsightsService()
    return ok(service.confusion_matrix())


@ai_insights_api_bp.get("/api/insights/performance")
def performance():
    lookback_days = request.args.get("days", default=30, type=int)
    service = AIInsightsService(lookback_days=lookback_days)
    return ok(service.performance_analytics())


@ai_insights_api_bp.get("/api/insights/confidence")
def confidence_distribution():
    service = AIInsightsService()
    return ok(service.confidence_distribution())
