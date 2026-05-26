from flask import Blueprint, request

from app.api.schemas import HorizonQuerySchema, LookbackQuerySchema
from app.core.api_utils import ok, validate_query
from app.services.analytics_service import AnalyticsService

analytics_api_bp = Blueprint("analytics_api", __name__)


@analytics_api_bp.get("/api/analytics/overview")
def analytics_overview():
    params = validate_query(LookbackQuerySchema())
    service = AnalyticsService(lookback_days=params["days"])
    return ok(service.overview_kpis())


@analytics_api_bp.get("/api/analytics/risk-trends")
def analytics_risk_trends():
    params = validate_query(LookbackQuerySchema())
    service = AnalyticsService(lookback_days=params["days"])
    return ok(service.risk_trends())


@analytics_api_bp.get("/api/analytics/regions")
def analytics_regions():
    service = AnalyticsService()
    return ok(service.regional_summary())


@analytics_api_bp.get("/api/analytics/ai-performance")
def analytics_ai_performance():
    params = validate_query(LookbackQuerySchema())
    service = AnalyticsService(lookback_days=params["days"])
    return ok(service.ai_performance())


@analytics_api_bp.get("/api/analytics/anomalies")
def analytics_anomalies():
    params = validate_query(LookbackQuerySchema())
    service = AnalyticsService(lookback_days=params["days"])
    return ok(service.anomalies())


@analytics_api_bp.get("/api/analytics/feature-importance")
def analytics_feature_importance():
    service = AnalyticsService()
    return ok(service.feature_importance())


@analytics_api_bp.get("/api/analytics/forecasting")
def analytics_forecasting():
    params = validate_query(HorizonQuerySchema())
    service = AnalyticsService()
    return ok(service.forecasting(horizon_days=params["horizon"]))


@analytics_api_bp.get("/api/analytics/kpis")
def analytics_kpis():
    service = AnalyticsService()
    return ok(service.kpi_metrics())
