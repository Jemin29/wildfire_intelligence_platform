from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Tuple

from flask import Response

from app.core.errors import ExternalServiceError
from app.core.extensions import db
from app.db.models import Alert, ExportHistory, RiskPrediction
from app.services.analytics_service import AnalyticsService
from app.services.historical_service import HistoricalService


class ReportService:
    def __init__(self, user_id: int | None = None) -> None:
        self.user_id = user_id

    def export_predictions_csv(self, days: int = 30, limit: int = 1000) -> Response:
        since = datetime.utcnow() - timedelta(days=days)
        rows = (
            RiskPrediction.query.filter(RiskPrediction.created_at >= since)
            .order_by(RiskPrediction.created_at.desc())
            .limit(limit)
            .all()
        )
        headers = ["created_at", "lat", "lon", "prediction", "probability", "model_version"]
        data = [
            [
                row.created_at.isoformat(),
                row.lat,
                row.lon,
                row.prediction,
                row.probability,
                row.model_version,
            ]
            for row in rows
        ]
        payload = _write_csv(headers, data)
        self._record_export("predictions_csv", "completed")
        return _csv_response(payload, "predictions_export.csv")

    def export_alerts_csv(self, days: int = 30, limit: int = 1000) -> Response:
        since = datetime.utcnow() - timedelta(days=days)
        rows = (
            Alert.query.filter(Alert.created_at >= since)
            .order_by(Alert.created_at.desc())
            .limit(limit)
            .all()
        )
        headers = ["created_at", "severity", "status", "risk_score", "threshold", "channel", "message"]
        data = [
            [
                row.created_at.isoformat(),
                row.severity,
                row.status,
                row.risk_score,
                row.threshold,
                row.channel,
                row.message,
            ]
            for row in rows
        ]
        payload = _write_csv(headers, data)
        self._record_export("alerts_csv", "completed")
        return _csv_response(payload, "alerts_export.csv")

    def analytics_snapshot(self, lookback_days: int = 30) -> Dict:
        analytics = AnalyticsService(lookback_days=lookback_days)
        historical = HistoricalService()
        return {
            "kpis": analytics.overview_kpis(),
            "risk_trend": analytics.risk_trends(),
            "regional_summary": analytics.regional_summary(),
            "historical_trend": historical.trend_series(),
            "seasonality": historical.seasonal_profile(),
        }

    def generate_pdf_report(self, title: str, lookback_days: int = 30) -> Response:
        snapshot = self.analytics_snapshot(lookback_days=lookback_days)
        content = _render_pdf(title, snapshot)
        self._record_export("analytics_pdf", "completed")
        filename = f"wildfire_report_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.pdf"
        return _pdf_response(content, filename)

    def _record_export(self, export_type: str, status: str) -> None:
        try:
            record = ExportHistory(
                user_id=self.user_id,
                export_type=export_type,
                status=status,
                requested_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            db.session.add(record)
            db.session.commit()
        except Exception:
            db.session.rollback()


def _write_csv(headers: List[str], rows: Iterable[List]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue()


def _csv_response(payload: str, filename: str) -> Response:
    response = Response(payload, mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def _pdf_response(payload: bytes, filename: str) -> Response:
    response = Response(payload, mimetype="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def _render_pdf(title: str, snapshot: Dict) -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception as exc:
        raise ExternalServiceError("PDF generation requires reportlab", details={"error": str(exc)}) from exc

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, height - 50, title)

    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 70, f"Generated: {datetime.utcnow().isoformat()} UTC")

    kpis = snapshot.get("kpis", {})
    y = height - 100
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Executive KPIs")
    pdf.setFont("Helvetica", 10)
    y -= 16
    for key, value in kpis.items():
        pdf.drawString(50, y, f"{key}: {value}")
        y -= 14

    pdf.setFont("Helvetica-Bold", 12)
    y -= 10
    pdf.drawString(40, y, "Risk Trend (Recent)")
    pdf.setFont("Helvetica", 10)
    y -= 16
    for point in snapshot.get("risk_trend", {}).get("data", [])[:8]:
        pdf.drawString(50, y, f"{point['label']}: {point['value']}")
        y -= 12

    pdf.setFont("Helvetica-Bold", 12)
    y -= 10
    pdf.drawString(40, y, "Historical Trend")
    pdf.setFont("Helvetica", 10)
    y -= 16
    for point in snapshot.get("historical_trend", {}).get("data", [])[:8]:
        pdf.drawString(50, y, f"{point['label']}: {point['value']}")
        y -= 12

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.read()
