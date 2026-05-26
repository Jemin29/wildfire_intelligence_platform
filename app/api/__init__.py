from flask import Flask

from app.api.ai_insights_api_routes import ai_insights_api_bp
from app.api.ai_insights_routes import ai_insights_bp
from app.api.alert_api_routes import alert_api_bp
from app.api.alert_routes import alert_bp
from app.api.alerts_routes import alerts_page_bp
from app.api.analytics_api_routes import analytics_api_bp
from app.api.analytics_routes import analytics_bp
from app.api.dashboard_routes import dashboard_bp
from app.api.health_routes import health_bp
from app.api.historical_api_routes import historical_api_bp
from app.api.historical_routes import historical_bp
from app.api.map_routes import map_bp, map_page_bp
from app.api.prediction_routes import prediction_bp, prediction_page_bp
from app.api.report_api_routes import report_api_bp
from app.api.risk_routes import risk_bp
from app.api.weather_routes import weather_bp, weather_page_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(alert_bp)
    app.register_blueprint(alert_api_bp)
    app.register_blueprint(alerts_page_bp)
    app.register_blueprint(ai_insights_api_bp)
    app.register_blueprint(ai_insights_bp)
    app.register_blueprint(analytics_api_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(historical_api_bp)
    app.register_blueprint(historical_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(map_page_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(prediction_page_bp)
    app.register_blueprint(report_api_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(weather_page_bp)
