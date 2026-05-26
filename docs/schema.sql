CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(120),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE alert_recipients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    channel VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alert_recipients_channel ON alert_recipients(channel);

CREATE TABLE weather_observations (
    id SERIAL PRIMARY KEY,
    observed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    rainfall DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    vegetation DOUBLE PRECISION,
    soil_moisture DOUBLE PRECISION
);

CREATE INDEX idx_weather_time ON weather_observations(observed_at);
CREATE INDEX idx_weather_geo ON weather_observations(lat, lon);

CREATE TABLE risk_predictions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    prediction INTEGER NOT NULL,
    probability DOUBLE PRECISION,
    model_version VARCHAR(50),
    weather_observation_id INTEGER REFERENCES weather_observations(id)
);

CREATE INDEX idx_predictions_time ON risk_predictions(created_at);
CREATE INDEX idx_predictions_geo ON risk_predictions(lat, lon);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    prediction_id INTEGER REFERENCES risk_predictions(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    risk_score DOUBLE PRECISION NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    channel VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    message TEXT,
    delivered_at TIMESTAMP
);

CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_time ON alerts(created_at);

CREATE TABLE inference_logs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    model_version VARCHAR(50),
    latency_ms INTEGER,
    request_id VARCHAR(64),
    status VARCHAR(20) NOT NULL
);

CREATE INDEX idx_inference_logs_time ON inference_logs(created_at);
CREATE INDEX idx_inference_logs_status ON inference_logs(status);

CREATE TABLE analytics_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    metric_name VARCHAR(80) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    scope VARCHAR(40) NOT NULL DEFAULT 'global'
);

CREATE INDEX idx_analytics_metric_date ON analytics_metrics(metric_date);
CREATE INDEX idx_analytics_metric_name ON analytics_metrics(metric_name);
