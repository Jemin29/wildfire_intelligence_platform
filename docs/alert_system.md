# Wildfire Alert System

## Architecture

- AlertService evaluates risk scores and triggers notifications.
- EmailNotifier sends SMTP email alerts.
- SmsGateway is a pluggable interface for future SMS providers.
- Flask API exposes a trigger endpoint for predictions or scheduled jobs.

## Trigger Flow

1. Risk score arrives from model predictions.
2. AlertService compares to `ALERT_RISK_THRESHOLD`.
3. If exceeded, it sends email and queues SMS (if configured).
4. Returns JSON with delivery metadata.

## Example Payload

```json
{
  "risk_score": 0.86,
  "location": "Sierra Corridor",
  "message": "Extreme conditions detected."
}
```

## Endpoint

- POST `/api/alerts/trigger`

## Integration

```python
from app.services.alert_service import AlertService, AlertTrigger

service = AlertService.from_config(app.config)
result = service.evaluate_and_notify(
    AlertTrigger(risk_score=0.86, location="Sierra Corridor", message="Extreme conditions")
)
```
