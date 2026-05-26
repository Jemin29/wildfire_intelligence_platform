# ER Diagram Explanation

## Entities

- **users**: Operators or stakeholders who receive alerts.
- **alert_recipients**: Email/SMS addresses linked to a user (or standalone).
- **weather_observations**: Time-stamped weather and environmental signals.
- **risk_predictions**: Model outputs linked to a location and optional weather snapshot.
- **alerts**: Triggered notifications associated to predictions and users.
- **inference_logs**: Request/latency/status logs for model calls.
- **analytics_metrics**: Aggregated daily metrics for dashboards.

## Relationships

- `users (1) -> (many) alert_recipients`
- `users (1) -> (many) alerts`
- `weather_observations (1) -> (many) risk_predictions`
- `risk_predictions (1) -> (many) alerts`

## Cardinality Summary

- A user can have multiple alert recipients and alerts.
- A prediction can generate multiple alerts (email + SMS).
- Analytics metrics are independent and keyed by date + name.

## Notes

- Locations are stored as `lat/lon` for portability; add PostGIS later if needed.
- `inference_logs` isolates operational telemetry for analytics and debugging.
