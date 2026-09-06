"""
Safar — Weather Tool

Real external API integration using Open-Meteo (no API key required).
1. Geocodes the destination name → latitude/longitude
2. Fetches 7-day weather forecast
3. Returns structured WeatherInfo

Gracefully falls back if the API is unavailable.
"""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

from app.config import settings
from app.models.travel import WeatherDay, WeatherInfo

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Open-Meteo API endpoints
# ---------------------------------------------------------------------------
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather code descriptions
WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _wmo_to_condition(code: int) -> str:
    """Convert WMO weather code to human-readable condition."""
    return WMO_CODES.get(code, "Unknown")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_weather(destination: str) -> WeatherInfo:
    """
    Fetch weather forecast for a destination.

    Returns WeatherInfo with is_fallback=False on success,
    or is_fallback=True with a message if the API is unavailable.
    """
    timeout = settings.weather_api_timeout_seconds

    try:
        # Step 1: Geocode destination
        lat, lon, resolved_name = await _geocode(destination, timeout)

        # Step 2: Fetch forecast
        forecast_days = await _fetch_forecast(lat, lon, timeout)

        # Step 3: Build summary
        if forecast_days:
            avg_max = sum(d.temp_max_c for d in forecast_days) / len(forecast_days)
            avg_min = sum(d.temp_min_c for d in forecast_days) / len(forecast_days)
            conditions = set(d.condition for d in forecast_days)
            summary = (
                f"Expected temperatures: {avg_min:.0f}°C – {avg_max:.0f}°C. "
                f"Conditions: {', '.join(conditions)}."
            )
        else:
            summary = "Forecast data unavailable."

        # Step 4: Packing suggestions based on weather
        packing = _generate_packing_suggestions(forecast_days)

        return WeatherInfo(
            destination=resolved_name,
            forecast=forecast_days,
            summary=summary,
            packing_suggestions=packing,
            is_fallback=False,
        )

    except Exception as e:
        logger.warning(f"Weather API failed for '{destination}': {e}")
        return WeatherInfo(
            destination=destination,
            forecast=[],
            summary=(
                f"Live weather data is currently unavailable for {destination}. "
                "Please check a weather service before your trip."
            ),
            packing_suggestions=[
                "Pack layers for variable weather",
                "Bring a light rain jacket just in case",
                "Carry sunscreen and sunglasses",
            ],
            is_fallback=True,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _geocode(
    destination: str, timeout: int
) -> tuple[float, float, str]:
    """Geocode a destination name to coordinates."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(
            GEOCODING_URL,
            params={"name": destination, "count": 1, "language": "en"},
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results")
    if not results:
        raise ValueError(f"Could not geocode destination: {destination}")

    loc = results[0]
    return loc["latitude"], loc["longitude"], loc.get("name", destination)


async def _fetch_forecast(
    lat: float, lon: float, timeout: int
) -> list[WeatherDay]:
    """Fetch 7-day daily forecast from Open-Meteo."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum",
                "timezone": "auto",
                "forecast_days": 7,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    t_max = daily.get("temperature_2m_max", [])
    t_min = daily.get("temperature_2m_min", [])
    codes = daily.get("weathercode", [])
    precip = daily.get("precipitation_sum", [])

    forecast: list[WeatherDay] = []
    for i in range(len(dates)):
        forecast.append(
            WeatherDay(
                date=dates[i],
                temp_max_c=t_max[i] if i < len(t_max) else 0,
                temp_min_c=t_min[i] if i < len(t_min) else 0,
                condition=_wmo_to_condition(codes[i] if i < len(codes) else 0),
                precipitation_mm=precip[i] if i < len(precip) else 0,
            )
        )

    return forecast


def _generate_packing_suggestions(forecast: list[WeatherDay]) -> list[str]:
    """Generate packing suggestions based on weather forecast."""
    if not forecast:
        return ["Pack for variable weather conditions"]

    suggestions = []
    max_temp = max(d.temp_max_c for d in forecast)
    min_temp = min(d.temp_min_c for d in forecast)
    has_rain = any(d.precipitation_mm > 1 for d in forecast)
    has_heavy_rain = any(d.precipitation_mm > 10 for d in forecast)

    if max_temp > 30:
        suggestions.append("Pack light, breathable clothing for hot weather")
        suggestions.append("Bring sunscreen (SPF 50+) and a hat")
    elif max_temp > 20:
        suggestions.append("Pack comfortable, light clothing")
    else:
        suggestions.append("Pack warm layers — temperatures can be cool")

    if min_temp < 15:
        suggestions.append("Bring a jacket or sweater for cooler evenings")

    if has_heavy_rain:
        suggestions.append("Pack a waterproof jacket and umbrella — heavy rain expected")
    elif has_rain:
        suggestions.append("Bring a light rain jacket or umbrella")

    suggestions.append("Carry a reusable water bottle")
    suggestions.append("Bring comfortable walking shoes")

    return suggestions
