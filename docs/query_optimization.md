# Indexing and Query Optimization

## Index Strategy

- `weather_observations(observed_at)` for time-series slices.
- `weather_observations(lat, lon)` for geo lookups.
- `risk_predictions(created_at)` for recent prediction dashboards.
- `risk_predictions(lat, lon)` for spatial search.
- `alerts(status, created_at)` for delivery monitoring.
- `analytics_metrics(metric_date, metric_name)` for time-series analytics.

## Query Optimization Recommendations

1. Use `created_at` range filters and avoid full table scans.
2. Aggregate analytics into `analytics_metrics` nightly to avoid heavy dashboard queries.
3. Use batched inserts for weather ingest and predictions.
4. If geo queries become heavy, migrate to PostGIS with `GEOGRAPHY` and `GIST` indexes.
5. Partition `weather_observations` and `risk_predictions` by month for scale.
6. Keep API logs in `inference_logs` and trim with retention policies.
