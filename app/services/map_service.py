from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from time import time
from typing import Dict, Iterable, List, Tuple

import folium
from branca.element import MacroElement, Template
from folium import FeatureGroup
from folium.plugins import HeatMap
from sqlalchemy import func

from app.core.extensions import db
from app.db.models import RiskPrediction, WeatherObservation


@dataclass(frozen=True)
class CacheEntry:
    payload: str
    expires_at: float


class MapService:
    def __init__(self, cache_ttl: int = 120) -> None:
        self.cache_ttl = cache_ttl
        self.cache: Dict[Tuple, CacheEntry] = {}

    def build_map(
        self,
        show_heat: bool = True,
        show_markers: bool = True,
        show_zones: bool = True,
        show_satellite: bool = False,
        show_weather: bool = False,
        min_risk: float = 0.0,
        hours: int = 24,
        bbox: Tuple[float, float, float, float] | None = None,
    ) -> str:
        cache_key = (
            show_heat,
            show_markers,
            show_zones,
            show_satellite,
            show_weather,
            round(min_risk, 2),
            hours,
            bbox,
        )
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        risk_points = _load_risk_points(min_risk=min_risk, hours=hours, bbox=bbox)
        weather_points = _load_weather_points(hours=hours, bbox=bbox)
        zones = _sample_risk_zones()

        center = _center_from_points(risk_points, default=(36.5, -119.6))
        map_obj = folium.Map(location=center, zoom_start=6, tiles=None, control_scale=True)

        folium.TileLayer(
            tiles="cartodb dark_matter",
            name="Command Dark",
            control=False,
        ).add_to(map_obj)

        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            name="Satellite",
            attr="Esri",
            overlay=True,
            show=show_satellite,
        ).add_to(map_obj)

        if show_heat and risk_points:
            heat_layer = FeatureGroup(name="Wildfire Heatmap", show=True)
            HeatMap(
                [[p["lat"], p["lon"], p["risk"]] for p in risk_points],
                min_opacity=0.3,
                max_zoom=10,
                radius=22,
                blur=18,
                gradient={0.2: "#22c55e", 0.5: "#fbbf24", 0.8: "#f97316", 1.0: "#ef4444"},
            ).add_to(heat_layer)
            heat_layer.add_to(map_obj)

        if show_markers and risk_points:
            marker_layer = FeatureGroup(name="Live Markers", show=True)
            for point in risk_points:
                color = _risk_color(point["risk"])
                folium.CircleMarker(
                    location=[point["lat"], point["lon"]],
                    radius=7 + point["risk"] * 6,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.75,
                    popup=f"Risk score: {point['risk']:.2f}",
                ).add_to(marker_layer)
            marker_layer.add_to(map_obj)

        if show_zones:
            zone_layer = FeatureGroup(name="Danger Zones", show=True)
            for zone in zones:
                folium.Polygon(
                    locations=zone["coords"],
                    color=zone["color"],
                    fill=True,
                    fill_opacity=0.25,
                    popup=zone["name"],
                ).add_to(zone_layer)
            zone_layer.add_to(map_obj)

        if show_weather and weather_points:
            weather_layer = FeatureGroup(name="Weather Overlay", show=True)
            for point in weather_points:
                folium.Marker(
                    location=[point["lat"], point["lon"]],
                    popup=(
                        f"Temp: {point['temp']} C<br>"
                        f"Humidity: {point['humidity']}%<br>"
                        f"Wind: {point['wind']} m/s"
                    ),
                    icon=folium.Icon(color="blue", icon="cloud"),
                ).add_to(weather_layer)
            weather_layer.add_to(map_obj)

        folium.LayerControl(position="topright", collapsed=False).add_to(map_obj)
        map_obj.get_root().add_child(_legend())

        html = map_obj.get_root().render()
        self._set_cache(cache_key, html)
        return html

    def points(self, min_risk: float = 0.0, hours: int = 24, bbox: Tuple[float, float, float, float] | None = None) -> Dict:
        return {
            "risk_points": _load_risk_points(min_risk=min_risk, hours=hours, bbox=bbox),
            "weather_points": _load_weather_points(hours=hours, bbox=bbox),
        }

    def analytics(self, hours: int = 24) -> Dict:
        since = datetime.utcnow() - timedelta(hours=hours)
        total = (
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
        return {
            "points": int(total),
            "avg_risk": round(float(avg_risk), 3),
            "window_hours": hours,
        }

    def _get_cached(self, key: Tuple) -> str | None:
        entry = self.cache.get(key)
        if not entry or entry.expires_at < time():
            return None
        return entry.payload

    def _set_cache(self, key: Tuple, payload: str) -> None:
        self.cache[key] = CacheEntry(payload=payload, expires_at=time() + self.cache_ttl)


def _load_risk_points(
    min_risk: float = 0.0,
    hours: int = 24,
    limit: int = 500,
    bbox: Tuple[float, float, float, float] | None = None,
) -> List[Dict[str, float]]:
    since = datetime.utcnow() - timedelta(hours=hours)
    query = db.session.query(RiskPrediction).filter(RiskPrediction.created_at >= since)
    if min_risk > 0:
        query = query.filter(RiskPrediction.probability >= min_risk)
    if bbox:
        min_lat, min_lon, max_lat, max_lon = bbox
        query = query.filter(RiskPrediction.lat.between(min_lat, max_lat))
        query = query.filter(RiskPrediction.lon.between(min_lon, max_lon))

    rows = query.order_by(RiskPrediction.created_at.desc()).limit(limit).all()
    if not rows:
        return _sample_risk_points()

    return [
        {
            "lat": float(row.lat),
            "lon": float(row.lon),
            "risk": float(row.probability or 0.0),
        }
        for row in rows
    ]


def _load_weather_points(
    hours: int = 6,
    limit: int = 200,
    bbox: Tuple[float, float, float, float] | None = None,
) -> List[Dict[str, float]]:
    since = datetime.utcnow() - timedelta(hours=hours)
    query = db.session.query(WeatherObservation).filter(WeatherObservation.observed_at >= since)
    if bbox:
        min_lat, min_lon, max_lat, max_lon = bbox
        query = query.filter(WeatherObservation.lat.between(min_lat, max_lat))
        query = query.filter(WeatherObservation.lon.between(min_lon, max_lon))

    rows = query.order_by(WeatherObservation.observed_at.desc()).limit(limit).all()
    if not rows:
        return _sample_weather_points()

    return [
        {
            "lat": float(row.lat),
            "lon": float(row.lon),
            "temp": float(row.temperature or 0.0),
            "humidity": float(row.humidity or 0.0),
            "wind": float(row.wind_speed or 0.0),
        }
        for row in rows
    ]


def _center_from_points(points: Iterable[Dict[str, float]], default: Tuple[float, float]) -> List[float]:
    points = list(points)
    if not points:
        return [default[0], default[1]]
    lat = sum(point["lat"] for point in points) / len(points)
    lon = sum(point["lon"] for point in points) / len(points)
    return [lat, lon]


def _risk_color(score: float) -> str:
    if score >= 0.8:
        return "#ef4444"
    if score >= 0.6:
        return "#f97316"
    if score >= 0.4:
        return "#fbbf24"
    return "#22c55e"


def _sample_risk_points() -> List[Dict[str, float]]:
    return [
        {"lat": 34.05, "lon": -118.25, "risk": 0.82},
        {"lat": 36.77, "lon": -119.41, "risk": 0.67},
        {"lat": 37.77, "lon": -122.42, "risk": 0.54},
        {"lat": 32.72, "lon": -117.16, "risk": 0.71},
    ]


def _sample_weather_points() -> List[Dict[str, float]]:
    return [
        {"lat": 34.05, "lon": -118.25, "temp": 31.2, "humidity": 18, "wind": 7.1},
        {"lat": 36.77, "lon": -119.41, "temp": 28.4, "humidity": 21, "wind": 5.4},
        {"lat": 37.77, "lon": -122.42, "temp": 22.7, "humidity": 42, "wind": 6.3},
    ]


def _sample_risk_zones() -> List[Dict[str, object]]:
    return [
        {
            "name": "Sierra Corridor",
            "color": "#ef4444",
            "coords": [
                [37.2, -120.6],
                [37.8, -120.6],
                [38.1, -119.7],
                [37.4, -119.5],
            ],
        },
        {
            "name": "Coastal Ridge",
            "color": "#f97316",
            "coords": [
                [34.1, -120.2],
                [34.8, -120.3],
                [35.2, -119.6],
                [34.6, -119.2],
            ],
        },
    ]


def _legend() -> MacroElement:
    element = MacroElement()
    element.template = Template(
        """
        {% macro html(this, kwargs) %}
        <div style="
            position: fixed;
            bottom: 30px;
            left: 30px;
            z-index: 9999;
            background: rgba(18, 22, 28, 0.9);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 12px 14px;
            color: #f7f5f2;
            font-family: Arial, sans-serif;
            font-size: 12px;">
            <div style="font-weight: 700; margin-bottom: 6px;">Risk Legend</div>
            <div><span style="color:#ef4444;">■</span> Critical</div>
            <div><span style="color:#f97316;">■</span> High</div>
            <div><span style="color:#fbbf24;">■</span> Moderate</div>
            <div><span style="color:#22c55e;">■</span> Low</div>
        </div>
        {% endmacro %}
        """
    )
    return element
