from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func

from app.core.extensions import db
from app.db.models import HistoricalWildfire, Location


@dataclass(frozen=True)
class TimeSeriesPoint:
    label: str
    value: float


class HistoricalService:
    def __init__(self, lookback_years: int = 5) -> None:
        self.lookback_years = lookback_years

    def trend_series(self) -> Dict:
        since = datetime.utcnow() - timedelta(days=365 * self.lookback_years)
        rows = (
            db.session.query(
                func.date_trunc("month", HistoricalWildfire.started_at).label("month"),
                func.count(HistoricalWildfire.id).label("count"),
                func.avg(HistoricalWildfire.burned_area_ha).label("avg_area"),
            )
            .filter(HistoricalWildfire.started_at.isnot(None))
            .filter(HistoricalWildfire.started_at >= since)
            .group_by("month")
            .order_by("month")
            .all()
        )

        points = [
            {
                "label": row.month.strftime("%Y-%m"),
                "value": float(row.count),
                "avg_area": round(float(row.avg_area or 0.0), 2),
            }
            for row in rows
        ]
        return {"series": "historical_trend", "data": points}

    def seasonal_profile(self) -> Dict:
        rows = (
            db.session.query(
                func.extract("month", HistoricalWildfire.started_at).label("month"),
                func.count(HistoricalWildfire.id).label("count"),
                func.avg(HistoricalWildfire.burned_area_ha).label("avg_area"),
            )
            .filter(HistoricalWildfire.started_at.isnot(None))
            .group_by("month")
            .order_by("month")
            .all()
        )

        return {
            "seasonality": [
                {
                    "month": int(row.month),
                    "count": int(row.count),
                    "avg_area": round(float(row.avg_area or 0.0), 2),
                }
                for row in rows
            ]
        }

    def regional_summary(self, limit: int = 12) -> Dict:
        rows = (
            db.session.query(
                Location.region,
                func.count(HistoricalWildfire.id).label("count"),
                func.avg(HistoricalWildfire.burned_area_ha).label("avg_area"),
            )
            .join(Location, HistoricalWildfire.location_id == Location.id)
            .group_by(Location.region)
            .order_by(func.count(HistoricalWildfire.id).desc())
            .limit(limit)
            .all()
        )

        return {
            "regions": [
                {
                    "region": row.region or "Unknown",
                    "count": int(row.count),
                    "avg_area": round(float(row.avg_area or 0.0), 2),
                }
                for row in rows
            ]
        }

    def severity_breakdown(self) -> Dict:
        rows = (
            db.session.query(
                HistoricalWildfire.severity,
                func.count(HistoricalWildfire.id).label("count"),
            )
            .group_by(HistoricalWildfire.severity)
            .order_by(func.count(HistoricalWildfire.id).desc())
            .all()
        )

        return {
            "severity": [
                {
                    "label": row.severity or "unknown",
                    "value": int(row.count),
                }
                for row in rows
            ]
        }

    def comparative_years(self, years: int = 3) -> Dict:
        current_year = datetime.utcnow().year
        min_year = current_year - years + 1
        rows = (
            db.session.query(
                func.extract("year", HistoricalWildfire.started_at).label("year"),
                func.count(HistoricalWildfire.id).label("count"),
                func.avg(HistoricalWildfire.burned_area_ha).label("avg_area"),
            )
            .filter(HistoricalWildfire.started_at.isnot(None))
            .filter(func.extract("year", HistoricalWildfire.started_at) >= min_year)
            .group_by("year")
            .order_by("year")
            .all()
        )

        return {
            "years": [
                {
                    "year": int(row.year),
                    "count": int(row.count),
                    "avg_area": round(float(row.avg_area or 0.0), 2),
                }
                for row in rows
            ]
        }

    def forecast(self, horizon_months: int = 6) -> Dict:
        trend = self.trend_series()
        values = [point["value"] for point in trend["data"]]
        if not values:
            return {"forecast": []}

        last = float(values[-1])
        delta = float(values[-1] - values[-2]) if len(values) > 1 else 0.0
        forecast = []
        for step in range(1, horizon_months + 1):
            forecast.append(
                {
                    "month": step,
                    "value": round(last + delta * step, 2),
                }
            )

        return {"forecast": forecast, "method": "naive_delta"}
