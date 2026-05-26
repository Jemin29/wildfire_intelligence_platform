from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func

from app.core.extensions import db
from app.db.models import AIInsight, InferenceLog, ModelVersion, Prediction


@dataclass(frozen=True)
class ChartPoint:
    label: str
    value: float


class AIInsightsService:
    def __init__(self, lookback_days: int = 30) -> None:
        self.lookback_days = lookback_days

    def feature_importance(self) -> Dict:
        insight = (
            AIInsight.query.order_by(AIInsight.created_at.desc())
            .filter(AIInsight.feature_importance.isnot(None))
            .first()
        )
        if not insight or not insight.feature_importance:
            return {"available": False, "features": []}

        return {
            "available": True,
            "features": insight.feature_importance,
            "generated_at": insight.created_at.isoformat(),
        }

    def shap_summary(self) -> Dict:
        try:
            import shap  # noqa: F401
        except Exception:
            return {"available": False, "reason": "shap_not_installed"}

        insight = (
            AIInsight.query.order_by(AIInsight.created_at.desc())
            .filter(AIInsight.summary.isnot(None))
            .first()
        )
        if not insight or not insight.summary:
            return {"available": False, "reason": "no_shap_data"}

        return {
            "available": True,
            "summary": insight.summary,
            "generated_at": insight.created_at.isoformat(),
        }

    def prediction_explanation(self, prediction_id: int) -> Dict:
        insight = AIInsight.query.filter(AIInsight.prediction_id == prediction_id).first()
        if not insight:
            return {"available": False, "reason": "no_explanation"}

        return {
            "available": True,
            "method": insight.method,
            "summary": insight.summary,
            "feature_importance": insight.feature_importance,
            "generated_at": insight.created_at.isoformat(),
        }

    def model_metrics(self) -> Dict:
        model = ModelVersion.query.order_by(ModelVersion.created_at.desc()).first()
        if not model or not model.metrics:
            return {"available": False, "metrics": {}}

        return {
            "available": True,
            "metrics": model.metrics,
            "model": {
                "name": model.name,
                "version": model.version,
                "framework": model.framework,
            },
        }

    def confusion_matrix(self) -> Dict:
        model = ModelVersion.query.order_by(ModelVersion.created_at.desc()).first()
        if not model or not model.metrics:
            return {"available": False, "matrix": []}

        matrix = model.metrics.get("confusion_matrix") if isinstance(model.metrics, dict) else None
        if not matrix:
            return {"available": False, "matrix": []}

        return {
            "available": True,
            "matrix": matrix,
            "labels": model.metrics.get("confusion_labels", ["negative", "positive"]),
        }

    def performance_analytics(self) -> Dict:
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

        total = sum(int(row.count) for row in rows)
        return {
            "lookback_days": self.lookback_days,
            "total_requests": total,
            "statuses": [
                {
                    "status": row.status,
                    "count": int(row.count),
                    "avg_latency_ms": round(float(row.avg_latency or 0.0), 2),
                }
                for row in rows
            ],
        }

    def confidence_distribution(self) -> Dict:
        rows = (
            db.session.query(Prediction.probability)
            .filter(Prediction.probability.isnot(None))
            .order_by(Prediction.created_at.desc())
            .limit(500)
            .all()
        )
        values = [float(row.probability) for row in rows if row.probability is not None]
        buckets = _bucketize(values)
        return {"series": "confidence", "data": buckets}


def _bucketize(values: List[float]) -> List[Dict[str, Any]]:
    if not values:
        return []

    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    counts = [0, 0, 0, 0, 0]
    for value in values:
        for i in range(len(bins) - 1):
            if bins[i] <= value < bins[i + 1]:
                counts[i] += 1
                break
    return [
        {"label": f"{bins[i]:.1f}-{bins[i+1]:.1f}", "value": counts[i]}
        for i in range(len(counts))
    ]
