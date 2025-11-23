# This file is part of TravelSytle AI.
#
# Copyright (C) 2025  Trailyn Ventures, LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.weather import WeatherService


class MockAsyncResponse:
    def __init__(self, data):
        self._data = data
        self.raise_for_status = MagicMock(return_value=None)  # Make this a mock

    def json(self):
        return self._data


@pytest.fixture
def weather_service():
    return WeatherService()


@pytest.mark.asyncio
async def test_get_weather_data_cache_hit(weather_service):
    with patch(
        "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_weather_cache",
        new=AsyncMock(return_value={"cached": True}),
    ) as mock_get_cache:
        result = await weather_service.get_weather_data("Paris")
        assert result == {"cached": True}
        mock_get_cache.assert_awaited_once_with("Paris")


@pytest.mark.asyncio
async def test_get_weather_data_cache_miss_success(weather_service):
    """Test get_weather_data with Visual Crossing API response (no dates)."""
    visual_crossing_response = {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "resolvedAddress": "Paris, France",
        "timezone": "Europe/Paris",
        "currentConditions": {
            "datetimeEpoch": 1753246845,
            "temp": 15,
            "feelslike": 14,
            "humidity": 60,
            "pressure": 1012,
            "windspeed": 5,
            "winddir": 180,
            "cloudcover": 20,
            "visibility": 10000,
            "conditions": "Clear",
        },
        "days": [
            {
                "datetime": "2025-01-23",
                "tempmin": 12,
                "tempmax": 18,
                "humidity": 60,
                "conditions": "Clear",
                "precipprob": 0,
                "hours": [],
            }
        ],
    }

    mock_response = MockAsyncResponse(visual_crossing_response)
    mock_response.raise_for_status = MagicMock()

    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch("httpx.AsyncClient") as mock_client,
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.set_weather_cache",
            new=AsyncMock(),
        ) as mock_set_cache,
    ):
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        result = await weather_service.get_weather_data("Paris")
        assert result is not None
        assert result["current"]["main"]["temp"] == 15
        assert result["destination"] == "Paris"
        assert result["forecast"] is not None
        mock_set_cache.assert_awaited_once()

        # Verify URL was constructed correctly (no dates in path)
        call_args = mock_client_instance.__aenter__.return_value.get.call_args
        assert "Paris" in call_args[0][0]  # URL contains location
        assert "/202" not in call_args[0][0]  # No dates in URL


@pytest.mark.asyncio
async def test_get_weather_data_api_error(weather_service):
    """Test get_weather_data when Visual Crossing API raises an error."""
    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch("httpx.AsyncClient") as mock_client,
    ):
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("API error")
        )
        mock_client.return_value = mock_client_instance

        result = await weather_service.get_weather_data("Paris")
        assert result is None


@pytest.mark.asyncio
async def test_get_weather_data_with_single_date(weather_service):
    """Test get_weather_data with a single date in URL path."""
    visual_crossing_response = {
        "latitude": 51.5074,
        "longitude": -0.1278,
        "resolvedAddress": "London, UK",
        "timezone": "Europe/London",
        "currentConditions": {
            "datetimeEpoch": 1601510400,
            "temp": 20,
            "feelslike": 19,
            "humidity": 50,
            "pressure": 1000,
            "windspeed": 7,
            "winddir": 180,
            "cloudcover": 75,
            "visibility": 5000,
            "conditions": "Rain",
        },
        "days": [
            {
                "datetime": "2020-10-01",
                "tempmin": 18,
                "tempmax": 22,
                "humidity": 50,
                "conditions": "Rain",
                "precipprob": 80,
                "hours": [],
            }
        ],
    }

    mock_response = MockAsyncResponse(visual_crossing_response)
    mock_response.raise_for_status = MagicMock()

    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch("httpx.AsyncClient") as mock_client,
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.set_weather_cache",
            new=AsyncMock(),
        ),
    ):
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        result = await weather_service.get_weather_data("London,UK", dates=["2020-10-01"])
        assert result is not None
        assert result["current"]["main"]["temp"] == 20
        assert result["current"]["weather"][0]["main"] == "Rain"

        # Verify URL contains date in path
        call_args = mock_client_instance.__aenter__.return_value.get.call_args
        url = call_args[0][0]
        assert "London,UK" in url
        assert "/2020-10-01" in url
        assert "/2020-12-31" not in url  # No second date


@pytest.mark.asyncio
async def test_get_weather_data_with_date_range(weather_service):
    """Test get_weather_data with date range in URL path."""
    visual_crossing_response = {
        "latitude": 51.5074,
        "longitude": -0.1278,
        "resolvedAddress": "London, UK",
        "timezone": "Europe/London",
        "days": [
            {
                "datetime": "2020-10-01",
                "tempmin": 15,
                "tempmax": 20,
                "humidity": 60,
                "conditions": "Clear",
                "precipprob": 0,
                "hours": [],
            },
            {
                "datetime": "2020-12-31",
                "tempmin": 5,
                "tempmax": 10,
                "humidity": 70,
                "conditions": "Snow",
                "precipprob": 50,
                "hours": [],
            },
        ],
    }

    mock_response = MockAsyncResponse(visual_crossing_response)
    mock_response.raise_for_status = MagicMock()

    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch("httpx.AsyncClient") as mock_client,
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.set_weather_cache",
            new=AsyncMock(),
        ),
    ):
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        result = await weather_service.get_weather_data(
            "London,UK", dates=["2020-10-01", "2020-12-31"]
        )
        assert result is not None
        assert result["forecast"] is not None
        assert len(result["forecast"]["daily_forecasts"]) == 2

        # Verify URL contains both dates in path
        call_args = mock_client_instance.__aenter__.return_value.get.call_args
        url = call_args[0][0]
        assert "London,UK" in url
        assert "/2020-10-01" in url
        assert "/2020-12-31" in url


def test__calculate_precipitation_chance():
    """Test precipitation chance calculation."""
    ws = WeatherService()
    assert ws._calculate_precipitation_chance(["Rain", "Rain"]) == 100
    assert ws._calculate_precipitation_chance(["Rain", "Clear"]) == 50
    assert ws._calculate_precipitation_chance(["Clear", "Clouds"]) == 0
    assert ws._calculate_precipitation_chance([]) == 0


def test__map_conditions_to_icon():
    """Test mapping Visual Crossing conditions to icon codes."""
    ws = WeatherService()
    assert ws._map_conditions_to_icon("Clear") == "01d"
    assert ws._map_conditions_to_icon("Sunny") == "01d"
    assert ws._map_conditions_to_icon("Cloudy") == "03d"
    assert ws._map_conditions_to_icon("Partly Cloudy") == "03d"
    assert ws._map_conditions_to_icon("Rain") == "09d"
    assert ws._map_conditions_to_icon("Rainy") == "09d"
    assert ws._map_conditions_to_icon("Snow") == "13d"
    assert ws._map_conditions_to_icon("Snowy") == "13d"
    assert ws._map_conditions_to_icon("Thunderstorm") == "11d"
    assert ws._map_conditions_to_icon("Thunder") == "11d"
    assert ws._map_conditions_to_icon("Fog") == "02d"  # Default
    assert ws._map_conditions_to_icon("") == "02d"  # Empty string


@pytest.mark.asyncio
async def test_get_weather_data_empty_response(weather_service):
    """Test get_weather_data when Visual Crossing API returns empty data."""
    visual_crossing_response = {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "resolvedAddress": "Paris, France",
        "timezone": "Europe/Paris",
    }

    mock_response = MockAsyncResponse(visual_crossing_response)
    mock_response.raise_for_status = MagicMock()

    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch("httpx.AsyncClient") as mock_client,
    ):
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        result = await weather_service.get_weather_data("Paris")
        assert result is None


@pytest.mark.asyncio
async def test_get_weather_data_service_exception(weather_service):
    """Test get_weather_data when service raises exception."""
    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch("httpx.AsyncClient") as mock_client,
    ):
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Service error")
        )
        mock_client.return_value = mock_client_instance

        result = await weather_service.get_weather_data("Paris")
        assert result is None


@pytest.mark.asyncio
async def test_get_weather_data_with_state_country(weather_service):
    """Test get_weather_data with state and country parameters."""
    visual_crossing_response = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "resolvedAddress": "New York, NY, United States",
        "timezone": "America/New_York",
        "currentConditions": {
            "datetimeEpoch": 1753246845,
            "temp": 20,
            "feelslike": 19,
            "humidity": 50,
            "pressure": 1000,
            "windspeed": 5,
            "winddir": 180,
            "cloudcover": 20,
            "visibility": 10000,
            "conditions": "Clear",
        },
        "days": [
            {
                "datetime": "2025-01-23",
                "tempmin": 15,
                "tempmax": 25,
                "humidity": 50,
                "conditions": "Clear",
                "precipprob": 0,
                "hours": [],
            }
        ],
    }

    mock_response = MockAsyncResponse(visual_crossing_response)
    mock_response.raise_for_status = MagicMock()

    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch("httpx.AsyncClient") as mock_client,
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.set_weather_cache",
            new=AsyncMock(),
        ),
    ):
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        result = await weather_service.get_weather_data("New York", state="NY", country="US")
        assert result is not None
        assert result["destination"] == "New York"

        # Verify location string includes state and country
        call_args = mock_client_instance.__aenter__.return_value.get.call_args
        url = call_args[0][0]
        assert "New York" in url
        assert "NY" in url
        assert "US" in url
