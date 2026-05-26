from flask import Blueprint, current_app, render_template, request

from app.api.schemas import WeatherQuerySchema
from app.core.api_utils import ok, validate_query
from app.services.weather_service import WeatherService

weather_bp = Blueprint("weather", __name__)
weather_page_bp = Blueprint("weather_page", __name__)


@weather_bp.get("/api/weather")
def weather():
    params = validate_query(WeatherQuerySchema())
    lat = params["lat"]
    lon = params["lon"]

    service = WeatherService(
        current_url=current_app.config["WEATHER_API_BASE_URL"],
        forecast_url=current_app.config["WEATHER_FORECAST_URL"],
        api_key=current_app.config["WEATHER_API_KEY"],
        cache_ttl=current_app.config["WEATHER_CACHE_TTL"],
        timeout_seconds=current_app.config["WEATHER_TIMEOUT_SECONDS"],
        retry_total=current_app.config["WEATHER_RETRY_TOTAL"],
        retry_backoff=current_app.config["WEATHER_RETRY_BACKOFF"],
    )
    data = service.fetch_current(lat, lon)
    return ok(data)


@weather_bp.get("/api/weather/forecast")
def forecast():
    params = validate_query(WeatherQuerySchema())
    lat = params["lat"]
    lon = params["lon"]

    service = WeatherService(
        current_url=current_app.config["WEATHER_API_BASE_URL"],
        forecast_url=current_app.config["WEATHER_FORECAST_URL"],
        api_key=current_app.config["WEATHER_API_KEY"],
        cache_ttl=current_app.config["WEATHER_CACHE_TTL"],
        timeout_seconds=current_app.config["WEATHER_TIMEOUT_SECONDS"],
        retry_total=current_app.config["WEATHER_RETRY_TOTAL"],
        retry_backoff=current_app.config["WEATHER_RETRY_BACKOFF"],
    )
    data = service.fetch_forecast(lat, lon)
    return ok(data)


@weather_bp.get("/api/weather/analysis")
def weather_analysis():
    params = validate_query(WeatherQuerySchema())
    lat = params["lat"]
    lon = params["lon"]

    service = WeatherService(
        current_url=current_app.config["WEATHER_API_BASE_URL"],
        forecast_url=current_app.config["WEATHER_FORECAST_URL"],
        api_key=current_app.config["WEATHER_API_KEY"],
        cache_ttl=current_app.config["WEATHER_CACHE_TTL"],
        timeout_seconds=current_app.config["WEATHER_TIMEOUT_SECONDS"],
        retry_total=current_app.config["WEATHER_RETRY_TOTAL"],
        retry_backoff=current_app.config["WEATHER_RETRY_BACKOFF"],
    )
    data = service.fetch_analysis(lat, lon)
    return ok(data)


@weather_page_bp.get("/weather")
def weather_page():
    return render_template("weather.html", active_page="weather")
