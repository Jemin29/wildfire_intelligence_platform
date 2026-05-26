from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Dict, Iterable, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.errors import ExternalServiceError


@dataclass(frozen=True)
class CacheEntry:
    payload: Dict
    expires_at: float


@dataclass(frozen=True)
class WeatherSummary:
    temperature_c: float | None
    humidity_pct: float | None
    wind_speed_mps: float | None
    wind_gust_mps: float | None
    precipitation_mm: float | None
    condition: str | None


class WeatherClient:
    def __init__(
        self,
        api_key: str,
        timeout_seconds: int,
        retry_total: int,
        retry_backoff: float,
    ) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

        retry = Retry(
            total=retry_total,
            backoff_factor=retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get(self, url: str, lat: float, lon: float) -> Dict:
        if not self.api_key:
            raise ExternalServiceError("Weather API key is not configured")

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout_seconds)
        except requests.RequestException as exc:
            raise ExternalServiceError("Weather API request failed", details={"error": str(exc)}) from exc

        if response.status_code >= 400:
            raise ExternalServiceError(
                "Weather API request failed",
                details={"status": response.status_code, "body": response.text},
            )

        return response.json()


class WeatherService:
    def __init__(
        self,
        current_url: str,
        forecast_url: str,
        api_key: str,
        cache_ttl: int,
        timeout_seconds: int,
        retry_total: int,
        retry_backoff: float,
    ) -> None:
        self.current_url = current_url
        self.forecast_url = forecast_url
        self.cache_ttl = cache_ttl
        self.cache: Dict[Tuple[str, float, float], CacheEntry] = {}
        self.client = WeatherClient(
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            retry_total=retry_total,
            retry_backoff=retry_backoff,
        )

    def fetch_current(self, lat: float, lon: float) -> Dict:
        key = ("current", *_cache_key(lat, lon))
        cached = self._get_cached(key)
        if cached:
            return cached

        data = self.client.get(self.current_url, lat, lon)
        summary = _summarize_current(data)
        indicators = _build_indicators(summary)
        payload = {
            "source": "openweathermap",
            "type": "current",
            "data": data,
            "summary": summary.__dict__,
            "indicators": indicators,
        }
        self._set_cache(key, payload)
        return payload

    def fetch_forecast(self, lat: float, lon: float) -> Dict:
        key = ("forecast", *_cache_key(lat, lon))
        cached = self._get_cached(key)
        if cached:
            return cached

        data = self.client.get(self.forecast_url, lat, lon)
        summary = _summarize_forecast(data)
        indicators = _build_indicators(summary)
        payload = {
            "source": "openweathermap",
            "type": "forecast",
            "data": data,
            "summary": summary.__dict__,
            "indicators": indicators,
        }
        self._set_cache(key, payload)
        return payload

    def fetch_analysis(self, lat: float, lon: float) -> Dict:
        current = self.fetch_current(lat, lon)
        forecast = self.fetch_forecast(lat, lon)
        return {
            "source": "openweathermap",
            "type": "analysis",
            "current": current["summary"],
            "forecast": forecast["summary"],
            "indicators": {
                "current": current["indicators"],
                "forecast": forecast["indicators"],
            },
        }

    def _get_cached(self, key: Tuple[str, float, float]) -> Dict | None:
        entry = self.cache.get(key)
        if not entry or entry.expires_at < time():
            return None
        return entry.payload

    def _set_cache(self, key: Tuple[str, float, float], payload: Dict) -> None:
        self.cache[key] = CacheEntry(payload=payload, expires_at=time() + self.cache_ttl)


def _cache_key(lat: float, lon: float) -> Tuple[float, float]:
    return (round(lat, 3), round(lon, 3))


def _summarize_current(data: Dict) -> WeatherSummary:
    main = data.get("main", {})
    wind = data.get("wind", {})
    rain = data.get("rain", {})
    weather = data.get("weather", [])
    condition = weather[0].get("main") if weather else None

    precipitation = rain.get("1h") or rain.get("3h")

    return WeatherSummary(
        temperature_c=main.get("temp"),
        humidity_pct=main.get("humidity"),
        wind_speed_mps=wind.get("speed"),
        wind_gust_mps=wind.get("gust"),
        precipitation_mm=precipitation,
        condition=condition,
    )


def _summarize_forecast(data: Dict) -> WeatherSummary:
    items: Iterable[Dict] = data.get("list", [])
    if not items:
        return WeatherSummary(None, None, None, None, None, None)

    first = items[0]
    main = first.get("main", {})
    wind = first.get("wind", {})
    rain = first.get("rain", {})
    weather = first.get("weather", [])
    condition = weather[0].get("main") if weather else None

    precipitation = rain.get("3h")

    return WeatherSummary(
        temperature_c=main.get("temp"),
        humidity_pct=main.get("humidity"),
        wind_speed_mps=wind.get("speed"),
        wind_gust_mps=wind.get("gust"),
        precipitation_mm=precipitation,
        condition=condition,
    )


def _build_indicators(summary: WeatherSummary) -> Dict:
    humidity = summary.humidity_pct
    temperature = summary.temperature_c
    wind_speed = summary.wind_speed_mps
    precipitation = summary.precipitation_mm

    dryness = _dryness_index(humidity, temperature, wind_speed)
    rainfall_flag = precipitation is not None and precipitation >= 5.0

    risk_score = min(1.0, max(0.0, dryness))
    risk_level = _risk_level(risk_score, rainfall_flag)

    return {
        "dryness_index": round(risk_score, 3),
        "risk_level": risk_level,
        "rainfall_recent": precipitation or 0.0,
        "wind_speed_mps": wind_speed,
        "humidity_pct": humidity,
        "temperature_c": temperature,
        "rainfall_suppressing": rainfall_flag,
    }


def _dryness_index(humidity: float | None, temperature: float | None, wind_speed: float | None) -> float:
    if humidity is None or temperature is None or wind_speed is None:
        return 0.0

    humidity_factor = max(0.0, 1.0 - humidity / 100.0)
    temperature_factor = min(1.0, max(0.0, temperature / 45.0))
    wind_factor = min(1.0, max(0.0, wind_speed / 20.0))

    return (humidity_factor * 0.45) + (temperature_factor * 0.35) + (wind_factor * 0.20)


def _risk_level(score: float, rainfall_suppressing: bool) -> str:
    if rainfall_suppressing and score < 0.6:
        return "low"
    if score >= 0.8:
        return "extreme"
    if score >= 0.6:
        return "high"
    if score >= 0.4:
        return "moderate"
    return "low"
