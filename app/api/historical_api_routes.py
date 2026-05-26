from flask import Blueprint, request

from app.api.schemas import YearsQuerySchema
from app.core.api_utils import ok, validate_query
from app.services.historical_service import HistoricalService

historical_api_bp = Blueprint("historical_api", __name__)


@historical_api_bp.get("/api/historical/trends")
def historical_trends():
    params = validate_query(YearsQuerySchema())
    service = HistoricalService(lookback_years=params["years"])
    return ok(service.trend_series())


@historical_api_bp.get("/api/historical/seasonality")
def historical_seasonality():
    service = HistoricalService()
    return ok(service.seasonal_profile())


@historical_api_bp.get("/api/historical/regions")
def historical_regions():
    limit = request.args.get("limit", default=12, type=int)
    service = HistoricalService()
    return ok(service.regional_summary(limit=limit))


@historical_api_bp.get("/api/historical/severity")
def historical_severity():
    service = HistoricalService()
    return ok(service.severity_breakdown())


@historical_api_bp.get("/api/historical/comparison")
def historical_comparison():
    params = validate_query(YearsQuerySchema())
    service = HistoricalService()
    return ok(service.comparative_years(years=params["years"]))


@historical_api_bp.get("/api/historical/forecast")
def historical_forecast():
    horizon = request.args.get("horizon", default=6, type=int)
    service = HistoricalService()
    return ok(service.forecast(horizon_months=horizon))
