from flask import Blueprint, current_app, request

from app.api.schemas import AlertTriggerSchema
from app.core.api_utils import ok, validate_json
from app.services.alert_service import AlertService, AlertTrigger

alert_bp = Blueprint("alerts", __name__)


@alert_bp.post("/api/alerts/trigger")
def trigger_alert():
    payload = request.get_json(silent=True)
    data = validate_json(AlertTriggerSchema(), payload)
    trigger = AlertTrigger(**data)

    service = AlertService.from_config(current_app.config)
    result = service.evaluate_and_notify(trigger)
    return ok(result)
