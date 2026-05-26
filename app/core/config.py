import os
from dataclasses import dataclass, field
from typing import List


def _split_origins(value: str | None) -> List[str]:
    if not value:
        return ["*"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass(frozen=True)
class BaseConfig:
    ENV: str = os.getenv("FLASK_ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_me")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change_me_too")
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///wildfire.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = field(
        default_factory=lambda: {
            "pool_pre_ping": True,
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
        }
    )
    JSON_SORT_KEYS: bool = False
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/best_model_pipeline.joblib")
    WEATHER_API_BASE_URL: str = os.getenv(
        "WEATHER_API_BASE_URL",
        "https://api.openweathermap.org/data/2.5/weather",
    )
    WEATHER_FORECAST_URL: str = os.getenv(
        "WEATHER_FORECAST_URL",
        "https://api.openweathermap.org/data/2.5/forecast",
    )
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_CACHE_TTL: int = int(os.getenv("WEATHER_CACHE_TTL", "600"))
    WEATHER_TIMEOUT_SECONDS: int = int(os.getenv("WEATHER_TIMEOUT_SECONDS", "10"))
    WEATHER_RETRY_TOTAL: int = int(os.getenv("WEATHER_RETRY_TOTAL", "3"))
    WEATHER_RETRY_BACKOFF: float = float(os.getenv("WEATHER_RETRY_BACKOFF", "0.5"))
    ALERT_RISK_THRESHOLD: float = float(os.getenv("ALERT_RISK_THRESHOLD", "0.7"))
    ALERT_RECIPIENTS: List[str] = field(
        default_factory=lambda: _split_origins(os.getenv("ALERT_RECIPIENTS", ""))
    )
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "alerts@wildfire.local")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    SMS_PROVIDER: str = os.getenv("SMS_PROVIDER", "")
    SMS_FROM: str = os.getenv("SMS_FROM", "")
    CORS_ORIGINS: List[str] = field(
        default_factory=lambda: _split_origins(os.getenv("CORS_ORIGINS", "*"))
    )


@dataclass(frozen=True)
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    TESTING: bool = False


@dataclass(frozen=True)
class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    TESTING: bool = False


def get_config() -> BaseConfig:
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
