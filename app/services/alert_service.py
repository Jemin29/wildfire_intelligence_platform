from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from app.core.errors import AlertDispatchError
from app.core.extensions import db
from app.db.models import Alert
from app.services.notification_service import EmailNotifier, SmsGateway
from app.utils.logging_config import setup_logging

LOGGER = setup_logging("alerts")


@dataclass(frozen=True)
class AlertTrigger:
    risk_score: float
    location: str
    message: str
    source: str = "prediction"
    prediction_id: Optional[int] = None
    user_id: Optional[int] = None


@dataclass
class AlertResult:
    triggered: bool
    risk_score: float
    threshold: float
    severity: str
    delivered: bool
    channels: List[str]
    timestamp: str
    alert_id: Optional[int] = None
    status: str | None = None


class AlertService:
    def __init__(
        self,
        risk_threshold: float,
        recipients: Iterable[str],
        email_notifier: EmailNotifier,
        sms_gateway: SmsGateway,
    ) -> None:
        self.risk_threshold = risk_threshold
        self.recipients = list(recipients)
        self.email_notifier = email_notifier
        self.sms_gateway = sms_gateway

    @classmethod
    def from_config(cls, config: Dict) -> "AlertService":
        email_notifier = EmailNotifier(
            host=config["SMTP_HOST"],
            port=config["SMTP_PORT"],
            username=config["SMTP_USERNAME"],
            password=config["SMTP_PASSWORD"],
            sender=config["SMTP_FROM"],
            use_tls=config["SMTP_USE_TLS"],
        )
        sms_gateway = SmsGateway(provider=config["SMS_PROVIDER"], sender=config["SMS_FROM"])
        return cls(
            risk_threshold=config["ALERT_RISK_THRESHOLD"],
            recipients=config["ALERT_RECIPIENTS"],
            email_notifier=email_notifier,
            sms_gateway=sms_gateway,
        )

    def evaluate_and_notify(self, trigger: AlertTrigger) -> Dict:
        timestamp = datetime.utcnow().isoformat()
        severity = _classify_severity(trigger.risk_score)
        if trigger.risk_score < self.risk_threshold:
            LOGGER.info("Risk %.2f below threshold %.2f", trigger.risk_score, self.risk_threshold)
            return AlertResult(
                triggered=False,
                risk_score=trigger.risk_score,
                threshold=self.risk_threshold,
                severity=severity,
                delivered=False,
                channels=[],
                timestamp=timestamp,
            ).__dict__

        subject = f"Wildfire alert: {trigger.location}"
        body = (
            f"Risk score: {trigger.risk_score:.2f}\n"
            f"Location: {trigger.location}\n"
            f"Message: {trigger.message or 'Threshold exceeded'}\n"
            f"Timestamp: {timestamp} UTC"
        )

        channels: List[str] = []
        delivered = False
        status = "queued"

        if self.recipients:
            LOGGER.info("Sending email alert to %s", self.recipients)
            try:
                self.email_notifier.send(self.recipients, subject, body)
                channels.append("email")
                delivered = True
                status = "sent"
            except Exception as exc:
                LOGGER.exception("Email delivery failed")
                status = "failed"
                raise AlertDispatchError("Email delivery failed") from exc

        if self.sms_gateway.enabled and severity in {"high", "extreme"}:
            LOGGER.info("Queueing SMS alert")
            self.sms_gateway.queue(self.recipients, body)
            channels.append("sms")
            if severity == "extreme":
                status = "escalated"

        alert_id = self._record_alert(
            trigger=trigger,
            severity=severity,
            status=status,
            delivered=delivered,
            channels=channels,
        )

        return AlertResult(
            triggered=True,
            risk_score=trigger.risk_score,
            threshold=self.risk_threshold,
            severity=severity,
            delivered=delivered,
            channels=channels,
            timestamp=timestamp,
            alert_id=alert_id,
            status=status,
        ).__dict__

    def _record_alert(
        self,
        trigger: AlertTrigger,
        severity: str,
        status: str,
        delivered: bool,
        channels: List[str],
    ) -> Optional[int]:
        try:
            alert = Alert(
                user_id=trigger.user_id,
                prediction_id=trigger.prediction_id,
                risk_score=trigger.risk_score,
                threshold=self.risk_threshold,
                channel=",".join(channels) or "none",
                status=status,
                message=_build_message(trigger, severity),
                delivered_at=datetime.utcnow() if delivered else None,
            )
            alert.severity = severity
            db.session.add(alert)
            db.session.commit()
            return alert.id
        except Exception:
            db.session.rollback()
            return None


def _classify_severity(risk_score: float) -> str:
    if risk_score >= 0.85:
        return "extreme"
    if risk_score >= 0.75:
        return "high"
    if risk_score >= 0.6:
        return "moderate"
    return "low"


def _build_message(trigger: AlertTrigger, severity: str) -> str:
    base = trigger.message or "Threshold exceeded"
    return f"[{severity.upper()}] {trigger.location}: {base}"
