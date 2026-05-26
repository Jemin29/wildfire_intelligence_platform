from flask import Blueprint, request

from app.core.api_utils import ok, pagination_meta, pagination_params
from app.core.extensions import db
from app.db.models import Alert

alert_api_bp = Blueprint("alert_api", __name__)


@alert_api_bp.get("/api/alerts")
def list_alerts():
    status = request.args.get("status")
    severity = request.args.get("severity")
    page, limit = pagination_params(default_limit=50, max_limit=500)

    query = Alert.query
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)

    total = query.count()
    alerts = (
        query.order_by(Alert.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    data = [
        {
            "id": alert.id,
            "severity": alert.severity,
            "status": alert.status,
            "risk_score": alert.risk_score,
            "threshold": alert.threshold,
            "channel": alert.channel,
            "message": alert.message,
            "created_at": alert.created_at.isoformat(),
        }
        for alert in alerts
    ]
    return ok({"alerts": data}, meta=pagination_meta(page, limit, total))


@alert_api_bp.get("/api/alerts/summary")
def alert_summary():
    total = Alert.query.count()
    by_severity = (
        db.session.query(Alert.severity, db.func.count(Alert.id))
        .group_by(Alert.severity)
        .all()
    )
    by_status = (
        db.session.query(Alert.status, db.func.count(Alert.id))
        .group_by(Alert.status)
        .all()
    )
    return ok(
        {
            "total": int(total),
            "severity": {row[0]: int(row[1]) for row in by_severity},
            "status": {row[0]: int(row[1]) for row in by_status},
        }
    )


@alert_api_bp.post("/api/alerts/<int:alert_id>/ack")
def acknowledge_alert(alert_id: int):
    alert = Alert.query.get_or_404(alert_id)
    alert.status = "acknowledged"
    db.session.commit()
    return ok({"id": alert.id, "status": alert.status})
