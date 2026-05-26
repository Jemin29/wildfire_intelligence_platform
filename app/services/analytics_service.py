from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np
from sqlalchemy import func

from app.core.extensions import db
from app.db.models import AIInsight, Alert, AnalyticsMetric, InferenceLog, RiskPrediction


@dataclass(frozen=True)
class TimeSeriesPoint:
    label: str
    value: float


class AnalyticsService:
    def __init__(self, lookback_days: int = 30) -> None:
        self.lookback_days = lookback_days

    def overview_kpis(self) -> Dict:
        since = datetime.utcnow() - timedelta(days=self.lookback_days)
        total_predictions = (
            db.session.query(func.count(RiskPrediction.id))
            .filter(RiskPrediction.created_at >= since)
            .scalar()
            or 0
        )
        avg_risk = (
            db.session.query(func.avg(RiskPrediction.probability))
            .filter(RiskPrediction.created_at >= since)
            .scalar()
            or 0.0
        )
        alert_count = (
            db.session.query(func.count(Alert.id))
            .filter(Alert.created_at >= since)
            .scalar()
            or 0
        )
        avg_latency = (
            db.session.query(func.avg(InferenceLog.latency_ms))
            .filter(InferenceLog.created_at >= since)
            .scalar()
            or 0.0
        )

        return {
            "total_predictions": int(total_predictions),
            "average_risk": round(float(avg_risk), 3),
            "alerts_triggered": int(alert_count),
            "avg_inference_ms": round(float(avg_latency), 2),
        }

    def risk_trends(self) -> Dict:
        since = datetime.utcnow() - timedelta(days=self.lookback_days)
        rows = (
            db.session.query(
                func.date_trunc("day", RiskPrediction.created_at).label("day"),
                func.avg(RiskPrediction.probability).label("avg_risk"),
            )
            .filter(RiskPrediction.created_at >= since)
            .group_by("day")
            .order_by("day")
            .all()
        )

        points = [
            TimeSeriesPoint(label=row.day.strftime("%Y-%m-%d"), value=float(row.avg_risk))
            for row in rows
        ]

        return _chart_response("risk_trend", points)

    def regional_summary(self) -> Dict:
        rows = (
            db.session.query(
                RiskPrediction.lat,
                RiskPrediction.lon,
                func.avg(RiskPrediction.probability).label("avg_risk"),
                func.count(RiskPrediction.id).label("count"),
            )
            .group_by(RiskPrediction.lat, RiskPrediction.lon)
            .order_by(func.avg(RiskPrediction.probability).desc())
            .limit(20)
            .all()
        )

        return {
            "regions": [
                {
                    "lat": float(row.lat),
                    "lon": float(row.lon),
                    "avg_risk": round(float(row.avg_risk), 3),
                    "samples": int(row.count),
                }
                for row in rows
            ]
        }

    def ai_performance(self) -> Dict:
        since = datetime.utcnow() - timedelta(days=self.lookback_days)
        rows = (
            db.session.query(
                InferenceLog.status,
                func.count(InferenceLog.id).label("count"),
                func.avg(InferenceLog.latency_ms).label("avg_latency"),
            )
            .filter(InferenceLog.created_at >= since)
            .group_by(InferenceLog.status)
            .all()
        )

        return {
            "statuses": [
                {
                    "status": row.status,
                    "count": int(row.count),
                    "avg_latency_ms": round(float(row.avg_latency or 0.0), 2),
                }
                for row in rows
            ]
        }

    def feature_importance(self) -> Dict:
        rows = (
            db.session.query(AIInsight.feature_importance)
            .filter(AIInsight.feature_importance.isnot(None))
            .order_by(AIInsight.created_at.desc())
            .limit(1)
            .all()
        )
        if not rows:
            return {"available": False, "features": []}

        raw = rows[0].feature_importance or []
        return {
            "available": True,
            "features": raw,
        }

    def anomalies(self) -> Dict:
        since = datetime.utcnow() - timedelta(days=self.lookback_days)
        rows = (
            db.session.query(RiskPrediction.created_at, RiskPrediction.probability)
            .filter(RiskPrediction.created_at >= since)
            .order_by(RiskPrediction.created_at.asc())
            .all()
        )

        if not rows:
            return {"anomalies": []}

        values = np.array([float(row.probability or 0.0) for row in rows])
        mean = float(values.mean())
        std = float(values.std())
        threshold = mean + 2 * std

        anomalies = [
            {
                "timestamp": row.created_at.isoformat(),
                "risk": float(row.probability or 0.0),
            }
            for row in rows
            if float(row.probability or 0.0) >= threshold
        ]

        return {
            "threshold": round(threshold, 3),
            "anomalies": anomalies,
        }

    def forecasting(self, horizon_days: int = 7) -> Dict:
        trend = self.risk_trends()
        values = [point["value"] for point in trend["data"]]
        if not values:
            return {"forecast": []}

        last = values[-1]
        delta = values[-1] - values[-2] if len(values) > 1 else 0.0
        forecast = []
        for step in range(1, horizon_days + 1):
            forecast.append(
                {
                    "day": step,
                    "value": round(float(last + delta * step), 3),
                }
            )

        return {"forecast": forecast, "method": "naive_delta"}

    def kpi_metrics(self) -> Dict:
        rows = (
            db.session.query(AnalyticsMetric.metric_name, AnalyticsMetric.metric_value)
            .order_by(AnalyticsMetric.metric_date.desc())
            .limit(50)
            .all()
        )
        return {
            "metrics": [
                {"name": row.metric_name, "value": float(row.metric_value)}
                for row in rows
            ]
        }


def _chart_response(series_name: str, points: List[TimeSeriesPoint]) -> Dict:
    return {
        "series": series_name,
        "data": [
            {"label": point.label, "value": round(float(point.value), 3)}
            for point in points
        ],
    }
