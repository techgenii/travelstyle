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
from app.services.weather_service import WeatherService


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
        "app.services.supabase_cache.supabase_cache.get_weather_cache",
        new=AsyncMock(return_value={"cached": True}),
    ) as mock_get_cache:
        result = await weather_service.get_weather_data("Paris")
        assert result == {"cached": True}
        mock_get_cache.assert_awaited_once_with("Paris")


@pytest.mark.asyncio
async def test_get_weather_data_cache_miss_success(weather_service):
    # Mock cache miss, then mock API calls and cache set
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            weather_service,
            "get_lat_lon_for_city",
            new=AsyncMock(return_value=(48.8566, 2.3522)),  # Paris lat/lon
        ),
        patch.object(
            weather_service,
            "_get_current_weather",
            new=AsyncMock(
                return_value={
                    "coord": {"lon": 2.3522, "lat": 48.8566},
                    "weather": [
                        {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
                    ],
                    "base": "stations",
                    "main": {
                        "temp": 15,
                        "feels_like": 14,
                        "temp_min": 12,
                        "temp_max": 18,
                        "pressure": 1012,
                        "humidity": 60,
                        "sea_level": 1012,
                        "grnd_level": 1000,
                    },
                    "visibility": 10000,
                    "wind": {"speed": 5, "deg": 180},
                    "clouds": {"all": 20},
                    "dt": 1753246845,
                    "sys": {
                        "type": 2,
                        "id": 2027281,
                        "country": "FR",
                        "sunrise": 1753189040,
                        "sunset": 1753239672,
                    },
                    "timezone": 3600,
                    "id": 2988507,
                    "name": "Paris",
                }
            ),
        ),
        patch.object(
            weather_service,
            "_get_forecast",
            new=AsyncMock(
                return_value={
                    "daily_forecasts": [],
                    "temp_range": {"min": 10, "max": 20},
                    "precipitation_chance": 0,
                }
            ),
        ),
        patch(
            "app.services.supabase_cache.supabase_cache.set_weather_cache", new=AsyncMock()
        ) as mock_set_cache,
    ):
        result = await weather_service.get_weather_data("Paris")
        assert result["current"]["main"]["temp"] == 15
        assert result["destination"] == "Paris"
        mock_set_cache.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_weather_data_api_error(weather_service):
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch.object(weather_service, "_get_current_weather", new=AsyncMock(return_value=None)),
    ):
        result = await weather_service.get_weather_data("Paris")
        assert result is None


@pytest.mark.asyncio
async def test__get_current_weather_success(weather_service):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "coord": {"lon": -0.1278, "lat": 51.5074},
        "weather": [{"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}],
        "base": "stations",
        "main": {
            "temp": 20,
            "feels_like": 19,
            "temp_min": 18,
            "temp_max": 22,
            "pressure": 1000,
            "humidity": 50,
            "sea_level": 1000,
            "grnd_level": 990,
        },
        "visibility": 5000,
        "wind": {"speed": 7, "deg": 180},
        "clouds": {"all": 75},
        "dt": 1753246845,
        "sys": {
            "type": 2,
            "id": 2027281,
            "country": "GB",
            "sunrise": 1753189040,
            "sunset": 1753239672,
        },
        "timezone": 0,
        "id": 2643743,
        "name": "London",
    }
    mock_response.raise_for_status = MagicMock()
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await weather_service._get_current_weather(51.5074, -0.1278)  # London lat/lon
        assert result["main"]["temp"] == 20
        assert result["weather"][0]["description"] == "light rain"
        assert result["wind"]["speed"] == 7
        assert result["visibility"] == 5000
        assert result["main"]["pressure"] == 1000


@pytest.mark.asyncio
async def test__get_current_weather_error(weather_service):
    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=Exception("fail"))):
        result = await weather_service._get_current_weather(51.5074, -0.1278)  # London lat/lon
        assert result is None


@pytest.mark.asyncio
async def test__get_forecast_api_error(weather_service):
    """Test _get_forecast when API raises an error."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(side_effect=Exception("API error")),
    ):
        result = await weather_service._get_forecast(48.8566, 2.3522)
        assert result is None


@pytest.mark.asyncio
async def test__get_forecast_empty_data(weather_service):
    """Test _get_forecast with empty forecast data."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=MockAsyncResponse({"list": []})),
    ):
        result = await weather_service._get_forecast(48.8566, 2.3522)
        assert result is not None
        assert result["daily_forecasts"] == []
        assert result["temp_range"]["min"] == 0
        assert result["temp_range"]["max"] == 0
        assert result["precipitation_chance"] == 0


@pytest.mark.asyncio
async def test__get_forecast_success_with_data(weather_service):
    """Test _get_forecast with successful data processing."""
    from datetime import datetime as dt

    now = dt.now()
    # Create timestamps for different days
    day1 = int(now.timestamp())
    day2 = day1 + 86400  # Next day

    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(
            return_value=MockAsyncResponse(
                {
                    "list": [
                        {
                            "dt": day1,
                            "main": {
                                "temp": 15,
                                "feels_like": 14,
                                "temp_min": 12,
                                "temp_max": 18,
                                "pressure": 1012,
                                "humidity": 60,
                                "sea_level": 1012,
                                "grnd_level": 1000,
                                "temp_kf": 0,
                            },
                            "weather": [
                                {
                                    "id": 800,
                                    "main": "Clear",
                                    "description": "clear sky",
                                    "icon": "01d",
                                }
                            ],
                            "clouds": {"all": 20},
                            "wind": {"speed": 5, "deg": 180, "gust": 0},
                            "visibility": 10000,
                            "pop": 0,
                            "sys": {"pod": "d"},
                            "dt_txt": "2025-07-23 12:00:00",
                        },
                        {
                            "dt": day2,
                            "main": {
                                "temp": 20,
                                "feels_like": 19,
                                "temp_min": 18,
                                "temp_max": 22,
                                "pressure": 1010,
                                "humidity": 55,
                                "sea_level": 1010,
                                "grnd_level": 998,
                                "temp_kf": 0,
                            },
                            "weather": [
                                {"id": 800, "main": "Clear", "description": "sunny", "icon": "01d"}
                            ],
                            "clouds": {"all": 10},
                            "wind": {"speed": 6, "deg": 190, "gust": 0},
                            "visibility": 10000,
                            "pop": 0,
                            "sys": {"pod": "d"},
                            "dt_txt": "2025-07-24 12:00:00",
                        },
                    ]
                }
            )
        ),
    ):
        result = await weather_service._get_forecast(48.8566, 2.3522)
        assert result is not None
        assert "daily_forecasts" in result
        assert "temp_range" in result
        assert "precipitation_chance" in result
        # Check new fields for both days
        daily = result["daily_forecasts"]
        assert len(daily) == 2
        # Day 1
        assert daily[0]["humidity_min"] == 60
        assert daily[0]["humidity_max"] == 60
        assert "clear sky" in daily[0]["weather_descriptions"]
        # Day 2
        assert daily[1]["humidity_min"] == 55
        assert daily[1]["humidity_max"] == 55
        assert "sunny" in daily[1]["weather_descriptions"]


def test__calculate_precipitation_chance():
    ws = WeatherService()
    assert ws._calculate_precipitation_chance(["Rain", "Rain"]) == 100
    assert ws._calculate_precipitation_chance(["Rain", "Clear"]) == 50
    assert ws._calculate_precipitation_chance(["Clear", "Clouds"]) == 0
    assert ws._calculate_precipitation_chance([]) == 0


@pytest.mark.asyncio
async def test_get_lat_lon_for_city_success(weather_service):
    """Test successful geocoding with city only."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=MockAsyncResponse([{"lat": 48.8566, "lon": 2.3522}])),
    ):
        lat, lon = await weather_service.get_lat_lon_for_city("Paris")
        assert lat == 48.8566
        assert lon == 2.3522


@pytest.mark.asyncio
async def test_get_lat_lon_for_city_with_state_country(weather_service):
    """Test successful geocoding with city, state, and country."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=MockAsyncResponse([{"lat": 40.7128, "lon": -74.0060}])),
    ):
        lat, lon = await weather_service.get_lat_lon_for_city("New York", "NY", "US")
        assert lat == 40.7128
        assert lon == -74.0060


@pytest.mark.asyncio
async def test_get_lat_lon_for_city_empty_response(weather_service):
    """Test geocoding when API returns empty response."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=MockAsyncResponse([])),
    ):
        lat, lon = await weather_service.get_lat_lon_for_city("NonexistentCity")
        assert lat is None
        assert lon is None


@pytest.mark.asyncio
async def test_get_lat_lon_for_city_api_error(weather_service):
    """Test geocoding when API raises an error."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(side_effect=Exception("API error")),
    ):
        lat, lon = await weather_service.get_lat_lon_for_city("Paris")
        assert lat is None
        assert lon is None


@pytest.mark.asyncio
async def test_get_weather_data_geocoding_failure(weather_service):
    """Test get_weather_data when geocoding fails."""
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            weather_service,
            "get_lat_lon_for_city",
            new=AsyncMock(return_value=(None, None)),
        ),
    ):
        result = await weather_service.get_weather_data("InvalidCity")
        assert result is None


@pytest.mark.asyncio
async def test_get_weather_data_current_weather_failure(weather_service):
    """Test get_weather_data when current weather API fails."""
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            weather_service,
            "get_lat_lon_for_city",
            new=AsyncMock(return_value=(48.8566, 2.3522)),
        ),
        patch.object(
            weather_service,
            "_get_current_weather",
            new=AsyncMock(return_value=None),
        ),
    ):
        result = await weather_service.get_weather_data("Paris")
        assert result is None


@pytest.mark.asyncio
async def test_get_weather_data_service_exception(weather_service):
    """Test get_weather_data when service raises exception."""
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            weather_service,
            "get_lat_lon_for_city",
            new=AsyncMock(side_effect=Exception("Service error")),
        ),
    ):
        result = await weather_service.get_weather_data("Paris")
        assert result is None


@pytest.mark.asyncio
async def test__get_current_weather_api_error(weather_service):
    """Test _get_current_weather when API raises an error."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(side_effect=Exception("API error")),
    ):
        result = await weather_service._get_current_weather(48.8566, 2.3522)
        assert result is None


@pytest.mark.asyncio
async def test__get_current_weather_missing_visibility(weather_service):
    """Test _get_current_weather when visibility is missing from response."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "coord": {"lon": 2.3522, "lat": 48.8566},
        "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
        "base": "stations",
        "main": {
            "temp": 20,
            "feels_like": 19,
            "temp_min": 18,
            "temp_max": 22,
            "pressure": 1000,
            "humidity": 50,
            "sea_level": 1000,
            "grnd_level": 990,
        },
        # visibility is missing
        "wind": {"speed": 5, "deg": 180},
        "clouds": {"all": 20},
        "dt": 1753246845,
        "sys": {
            "type": 2,
            "id": 2027281,
            "country": "FR",
            "sunrise": 1753189040,
            "sunset": 1753239672,
        },
        "timezone": 3600,
        "id": 2988507,
        "name": "Paris",
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await weather_service._get_current_weather(48.8566, 2.3522)
        assert result is not None
        assert result["visibility"] == 10000  # Should default to 10000 when missing


@pytest.mark.asyncio
async def test_get_weather_data_with_state_country(weather_service):
    """Test get_weather_data with state and country parameters."""
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_weather_cache",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            weather_service,
            "get_lat_lon_for_city",
            new=AsyncMock(return_value=(40.7128, -74.0060)),
        ),
        patch.object(
            weather_service,
            "_get_current_weather",
            new=AsyncMock(
                return_value={
                    "coord": {"lon": -74.0060, "lat": 40.7128},
                    "weather": [
                        {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
                    ],
                    "base": "stations",
                    "main": {
                        "temp": 20,
                        "feels_like": 19,
                        "temp_min": 18,
                        "temp_max": 22,
                        "pressure": 1000,
                        "humidity": 50,
                        "sea_level": 1000,
                        "grnd_level": 990,
                    },
                    "visibility": 10000,
                    "wind": {"speed": 5, "deg": 180},
                    "clouds": {"all": 20},
                    "dt": 1753246845,
                    "sys": {
                        "type": 2,
                        "id": 2027281,
                        "country": "US",
                        "sunrise": 1753189040,
                        "sunset": 1753239672,
                    },
                    "timezone": -18000,
                    "id": 5128581,
                    "name": "New York",
                }
            ),
        ),
        patch.object(
            weather_service,
            "_get_forecast",
            new=AsyncMock(
                return_value={
                    "daily_forecasts": [],
                    "temp_range": {"min": 15, "max": 25},
                    "precipitation_chance": 0,
                }
            ),
        ),
        patch("app.services.supabase_cache.supabase_cache.set_weather_cache", new=AsyncMock()),
    ):
        result = await weather_service.get_weather_data("New York", state="NY", country="US")
        assert result is not None
        assert result["destination"] == "New York"
