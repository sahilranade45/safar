"""
Safar — Weather Tool Tests

Tests for the Open-Meteo weather integration.
Uses mocked HTTP responses — no real API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.tools.weather import get_weather, _wmo_to_condition, _generate_packing_suggestions
from app.models.travel import WeatherDay


class TestWMOCodes:
    """Test WMO weather code conversion."""

    def test_clear_sky(self):
        assert _wmo_to_condition(0) == "Clear sky"

    def test_rain(self):
        assert _wmo_to_condition(63) == "Moderate rain"

    def test_thunderstorm(self):
        assert _wmo_to_condition(95) == "Thunderstorm"

    def test_unknown_code(self):
        assert _wmo_to_condition(999) == "Unknown"


class TestPackingSuggestions:
    """Test packing suggestion generation."""

    def test_hot_weather(self):
        forecast = [WeatherDay(temp_max_c=35, temp_min_c=28, precipitation_mm=0)]
        suggestions = _generate_packing_suggestions(forecast)
        assert any("light" in s.lower() or "hot" in s.lower() for s in suggestions)
        assert any("sunscreen" in s.lower() for s in suggestions)

    def test_rainy_weather(self):
        forecast = [WeatherDay(temp_max_c=25, temp_min_c=20, precipitation_mm=15)]
        suggestions = _generate_packing_suggestions(forecast)
        assert any("rain" in s.lower() or "waterproof" in s.lower() for s in suggestions)

    def test_cool_weather(self):
        forecast = [WeatherDay(temp_max_c=18, temp_min_c=8)]
        suggestions = _generate_packing_suggestions(forecast)
        assert any("warm" in s.lower() or "jacket" in s.lower() or "layers" in s.lower() for s in suggestions)

    def test_empty_forecast(self):
        suggestions = _generate_packing_suggestions([])
        assert len(suggestions) >= 1


class TestGetWeather:
    """Test the main get_weather function with mocked APIs."""

    @pytest.mark.asyncio
    async def test_successful_weather_fetch(self):
        """Test successful geocoding + forecast fetch."""
        mock_geocoding_response = MagicMock()
        mock_geocoding_response.status_code = 200
        mock_geocoding_response.raise_for_status = MagicMock()
        mock_geocoding_response.json.return_value = {
            "results": [{
                "latitude": 15.4989,
                "longitude": 73.8278,
                "name": "Goa",
            }]
        }

        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.raise_for_status = MagicMock()
        mock_forecast_response.json.return_value = {
            "daily": {
                "time": ["2025-01-15", "2025-01-16"],
                "temperature_2m_max": [32.0, 31.5],
                "temperature_2m_min": [24.0, 23.5],
                "weathercode": [0, 1],
                "precipitation_sum": [0.0, 0.0],
            }
        }

        with patch("app.tools.weather.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(
                side_effect=[mock_geocoding_response, mock_forecast_response]
            )
            mock_client_cls.return_value = mock_client

            weather = await get_weather("Goa")

            assert weather.destination == "Goa"
            assert weather.is_fallback is False
            assert len(weather.forecast) == 2
            assert weather.forecast[0].temp_max_c == 32.0
            assert weather.forecast[0].condition == "Clear sky"

    @pytest.mark.asyncio
    async def test_fallback_on_api_failure(self):
        """Test graceful fallback when API is unavailable."""
        with patch("app.tools.weather.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(side_effect=Exception("Connection failed"))
            mock_client_cls.return_value = mock_client

            weather = await get_weather("Unknown Place")

            assert weather.is_fallback is True
            assert len(weather.packing_suggestions) > 0
            assert "unavailable" in weather.summary.lower()

    @pytest.mark.asyncio
    async def test_fallback_on_no_geocoding_results(self):
        """Test fallback when geocoding returns no results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"results": None}

        with patch("app.tools.weather.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            weather = await get_weather("Xyzzyville")

            assert weather.is_fallback is True
