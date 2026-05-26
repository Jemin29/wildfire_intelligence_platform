from flask import Blueprint, Response, render_template, request

from app.core.api_utils import ok
from app.services.map_service import MapService

map_bp = Blueprint("map", __name__)
map_page_bp = Blueprint("map_page", __name__)


@map_bp.get("/map/wildfire")
def wildfire_map() -> Response:
    show_heat = request.args.get("heat", "1") == "1"
    show_markers = request.args.get("markers", "1") == "1"
    show_zones = request.args.get("zones", "1") == "1"
    show_satellite = request.args.get("satellite", "0") == "1"
    show_weather = request.args.get("weather", "0") == "1"
    min_risk = request.args.get("min_risk", type=float) or 0.0
    hours = request.args.get("hours", default=24, type=int)
    bbox = _parse_bbox(request.args.get("bbox"))

    service = MapService()
    map_html = service.build_map(
        show_heat=show_heat,
        show_markers=show_markers,
        show_zones=show_zones,
        show_satellite=show_satellite,
        show_weather=show_weather,
        min_risk=min_risk,
        hours=hours,
        bbox=bbox,
    )
    return Response(map_html, mimetype="text/html")


@map_page_bp.get("/live-map")
def live_map_page():
    return render_template("live_map.html", active_page="live_map")


@map_bp.get("/api/map/points")
def map_points():
    min_risk = request.args.get("min_risk", type=float) or 0.0
    hours = request.args.get("hours", default=24, type=int)
    bbox = _parse_bbox(request.args.get("bbox"))

    service = MapService()
    return ok(service.points(min_risk=min_risk, hours=hours, bbox=bbox))


@map_bp.get("/api/map/analytics")
def map_analytics():
    hours = request.args.get("hours", default=24, type=int)
    service = MapService()
    return ok(service.analytics(hours=hours))


def _parse_bbox(raw: str | None) -> tuple[float, float, float, float] | None:
    if not raw:
        return None
    try:
        parts = [float(part) for part in raw.split(",")]
    except ValueError:
        return None
    if len(parts) != 4:
        return None
    min_lat, min_lon, max_lat, max_lon = parts
    return (min_lat, min_lon, max_lat, max_lon)
