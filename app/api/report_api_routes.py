from flask import Blueprint, request

from app.services.analytics_service import AnalyticsService
from app.services.historical_service import HistoricalService
from app.services.report_service import ReportService

report_api_bp = Blueprint("report_api", __name__)


@report_api_bp.get("/api/reports/analytics/pdf")
def analytics_pdf():
    lookback_days = request.args.get("days", default=30, type=int)
    service = ReportService()
    return service.generate_pdf_report("Wildfire Intelligence Report", lookback_days=lookback_days)


@report_api_bp.get("/api/reports/predictions.csv")
def predictions_csv():
    lookback_days = request.args.get("days", default=30, type=int)
    limit = request.args.get("limit", default=1000, type=int)
    service = ReportService()
    return service.export_predictions_csv(days=lookback_days, limit=limit)


@report_api_bp.get("/api/reports/alerts.csv")
def alerts_csv():
    lookback_days = request.args.get("days", default=30, type=int)
    limit = request.args.get("limit", default=1000, type=int)
    service = ReportService()
    return service.export_alerts_csv(days=lookback_days, limit=limit)


@report_api_bp.get("/api/reports/charts")
def charts_json():
    chart_type = request.args.get("type", default="risk_trend")
    analytics = AnalyticsService()
    historical = HistoricalService()

    if chart_type == "risk_trend":
        return analytics.risk_trends()
    if chart_type == "historical_trend":
        return historical.trend_series()
    if chart_type == "seasonality":
        return historical.seasonal_profile()

    return {"success": False, "error": {"message": "unknown_chart_type", "code": "bad_request", "details": {}}}, 400
