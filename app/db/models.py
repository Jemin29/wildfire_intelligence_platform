from datetime import datetime

from app.core.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    recipients = db.relationship("AlertRecipient", back_populates="user")
    alerts = db.relationship("Alert", back_populates="user")


class AlertRecipient(db.Model):
    __tablename__ = "alert_recipients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    channel = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="recipients")

    __table_args__ = (
        db.Index("idx_alert_recipients_channel", "channel"),
    )


class WeatherObservation(db.Model):
    __tablename__ = "weather_observations"

    id = db.Column(db.Integer, primary_key=True)
    observed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    vegetation = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)

    predictions = db.relationship("RiskPrediction", back_populates="weather_observation")

    __table_args__ = (
        db.Index("idx_weather_time", "observed_at"),
        db.Index("idx_weather_geo", "lat", "lon"),
    )


class RiskPrediction(db.Model):
    __tablename__ = "risk_predictions"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.Integer, nullable=False)
    probability = db.Column(db.Float)
    model_version = db.Column(db.String(50))
    weather_observation_id = db.Column(
        db.Integer,
        db.ForeignKey("weather_observations.id"),
        nullable=True,
    )

    weather_observation = db.relationship("WeatherObservation", back_populates="predictions")
    alerts = db.relationship("Alert", back_populates="prediction")

    __table_args__ = (
        db.Index("idx_predictions_time", "created_at"),
        db.Index("idx_predictions_geo", "lat", "lon"),
    )


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey("risk_predictions.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    threshold = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), default="moderate", nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="queued", nullable=False)
    message = db.Column(db.Text)
    delivered_at = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="alerts")
    prediction = db.relationship("RiskPrediction", back_populates="alerts")

    __table_args__ = (
        db.Index("idx_alerts_status", "status"),
        db.Index("idx_alerts_time", "created_at"),
    )


class InferenceLog(db.Model):
    __tablename__ = "inference_logs"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    model_version = db.Column(db.String(50))
    latency_ms = db.Column(db.Integer)
    request_id = db.Column(db.String(64))
    status = db.Column(db.String(20), nullable=False)

    __table_args__ = (
        db.Index("idx_inference_logs_time", "created_at"),
        db.Index("idx_inference_logs_status", "status"),
    )


class AnalyticsMetric(db.Model):
    __tablename__ = "analytics_metrics"

    id = db.Column(db.Integer, primary_key=True)
    metric_date = db.Column(db.Date, nullable=False)
    metric_name = db.Column(db.String(80), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    scope = db.Column(db.String(40), default="global", nullable=False)

    __table_args__ = (
        db.Index("idx_analytics_metric_date", "metric_date"),
        db.Index("idx_analytics_metric_name", "metric_name"),
    )


class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(120))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    geojson = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    weather_records = db.relationship("WeatherRecord", back_populates="location")
    historical_wildfires = db.relationship("HistoricalWildfire", back_populates="location")
    risk_scores = db.relationship("RiskScore", back_populates="location")
    predictions = db.relationship("Prediction", back_populates="location")

    __table_args__ = (
        db.Index("idx_locations_geo", "latitude", "longitude"),
        db.Index("idx_locations_region", "region"),
    )


class WeatherRecord(db.Model):
    __tablename__ = "weather_records"

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    observed_at = db.Column(db.DateTime, nullable=False)
    temperature_c = db.Column(db.Float)
    humidity_pct = db.Column(db.Float)
    wind_speed_mps = db.Column(db.Float)
    wind_dir_deg = db.Column(db.Float)
    precipitation_mm = db.Column(db.Float)
    source = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    location = db.relationship("Location", back_populates="weather_records")

    __table_args__ = (
        db.Index("idx_weather_records_location_time", "location_id", "observed_at"),
    )


class HistoricalWildfire(db.Model):
    __tablename__ = "historical_wildfires"

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
    severity = db.Column(db.String(40))
    burned_area_ha = db.Column(db.Float)
    cause = db.Column(db.String(120))
    metadata_json = db.Column("metadata", db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    location = db.relationship("Location", back_populates="historical_wildfires")

    __table_args__ = (
        db.Index("idx_historical_wildfires_location", "location_id"),
        db.Index("idx_historical_wildfires_time", "started_at"),
    )


class RiskScore(db.Model):
    __tablename__ = "risk_scores"

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    scored_at = db.Column(db.DateTime, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    location = db.relationship("Location", back_populates="risk_scores")

    __table_args__ = (
        db.Index("idx_risk_scores_location_time", "location_id", "scored_at"),
    )


class ModelVersion(db.Model):
    __tablename__ = "model_versions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    version = db.Column(db.String(40), nullable=False)
    framework = db.Column(db.String(60))
    artifact_path = db.Column(db.String(255))
    metrics = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    predictions = db.relationship("Prediction", back_populates="model_version")
    insights = db.relationship("AIInsight", back_populates="model_version")

    __table_args__ = (
        db.UniqueConstraint("name", "version", name="uq_model_version"),
    )


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    model_version_id = db.Column(db.Integer, db.ForeignKey("model_versions.id"), nullable=False)
    predicted_at = db.Column(db.DateTime, nullable=False)
    horizon_hours = db.Column(db.Integer, nullable=False)
    probability = db.Column(db.Float, nullable=False)
    risk_score = db.Column(db.Float)
    raw_features = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    location = db.relationship("Location", back_populates="predictions")
    model_version = db.relationship("ModelVersion", back_populates="predictions")
    insights = db.relationship("AIInsight", back_populates="prediction")

    __table_args__ = (
        db.Index("idx_predictions_location_time", "location_id", "predicted_at"),
        db.Index("idx_predictions_model", "model_version_id"),
    )


class AIInsight(db.Model):
    __tablename__ = "ai_insights"

    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey("predictions.id"), nullable=False)
    model_version_id = db.Column(db.Integer, db.ForeignKey("model_versions.id"), nullable=False)
    method = db.Column(db.String(60), nullable=False)
    summary = db.Column(db.JSON)
    feature_importance = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    prediction = db.relationship("Prediction", back_populates="insights")
    model_version = db.relationship("ModelVersion", back_populates="insights")

    __table_args__ = (
        db.Index("idx_ai_insights_prediction", "prediction_id"),
    )


class UserActivity(db.Model):
    __tablename__ = "user_activity"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(120), nullable=False)
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    metadata_json = db.Column("metadata", db.JSON)

    __table_args__ = (
        db.Index("idx_user_activity_time", "occurred_at"),
    )


class ExportHistory(db.Model):
    __tablename__ = "export_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    export_type = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(20), default="queued", nullable=False)
    file_path = db.Column(db.String(255))
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (
        db.Index("idx_export_history_status", "status"),
        db.Index("idx_export_history_time", "requested_at"),
    )


class AnalyticsEvent(db.Model):
    __tablename__ = "analytics_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    event_type = db.Column(db.String(80), nullable=False)
    event_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    metadata_json = db.Column("metadata", db.JSON)

    __table_args__ = (
        db.Index("idx_analytics_events_type", "event_type"),
        db.Index("idx_analytics_events_time", "event_time"),
    )
