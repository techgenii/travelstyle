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
                    "temperature": 15,
                    "feels_like": 14,
                    "humidity": 60,
                    "description": "clear sky",
                    "wind_speed": 5,
                    "visibility": 10,
                    "pressure": 1012,
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
        assert result["current"]["temperature"] == 15
        assert result["destination"] == "Paris"
        assert "clothing_recommendations" in result
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
        "main": {"temp": 20, "feels_like": 19, "humidity": 50, "pressure": 1000},
        "weather": [{"description": "light rain"}],
        "wind": {"speed": 7},
        "visibility": 5000,
    }
    mock_response.raise_for_status = MagicMock()
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await weather_service._get_current_weather(51.5074, -0.1278)  # London lat/lon
        assert result["temperature"] == 20
        assert result["description"] == "light rain"
        assert result["wind_speed"] == 7
        assert result["visibility"] == 5
        assert result["pressure"] == 1000


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
                        {"dt": day1, "main": {"temp": 15}, "weather": [{"main": "Clear"}]},
                        {"dt": day2, "main": {"temp": 20}, "weather": [{"main": "Sunny"}]},
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


def test__calculate_precipitation_chance():
    ws = WeatherService()
    assert ws._calculate_precipitation_chance(["Rain", "Rain"]) == 100
    assert ws._calculate_precipitation_chance(["Rain", "Clear"]) == 50
    assert ws._calculate_precipitation_chance(["Clear", "Clouds"]) == 0
    assert ws._calculate_precipitation_chance([]) == 0


def test__generate_clothing_recommendations_temp_ranges():
    ws = WeatherService()
    # <0C
    rec = ws._generate_clothing_recommendations(
        {"temperature": -5, "description": "clear sky"}, None
    )
    assert "Heavy winter coat" in rec["layers"]
    # 0-10C
    rec = ws._generate_clothing_recommendations(
        {"temperature": 5, "description": "clear sky"}, None
    )
    assert "Warm jacket" in rec["layers"]
    # 10-20C
    rec = ws._generate_clothing_recommendations(
        {"temperature": 15, "description": "clear sky"}, None
    )
    assert "Light jacket or cardigan" in rec["layers"]
    # 20-30C
    rec = ws._generate_clothing_recommendations(
        {"temperature": 25, "description": "clear sky"}, None
    )
    assert "Light clothing" in rec["layers"]
    # >30C
    rec = ws._generate_clothing_recommendations(
        {"temperature": 35, "description": "clear sky"}, None
    )
    assert "Very light clothing" in rec["layers"]


def test__generate_clothing_recommendations_rain():
    ws = WeatherService()
    rec = ws._generate_clothing_recommendations(
        {"temperature": 15, "description": "rain showers"}, None
    )
    assert "Rain jacket" in rec["accessories"]
    assert "Waterproof shoes" in rec["footwear"]
    assert "Water-resistant fabrics" in rec["materials"]


def test__generate_clothing_recommendations_forecast_precip():
    ws = WeatherService()
    rec = ws._generate_clothing_recommendations(
        {"temperature": 15, "description": "clear sky"}, {"precipitation_chance": 80}
    )
    assert "Pack rain gear" in rec["accessories"]
    assert "High chance of rain during trip" in rec["special_considerations"]


def test__generate_clothing_recommendations_wind_humidity():
    ws = WeatherService()
    rec = ws._generate_clothing_recommendations(
        {"temperature": 15, "description": "clear sky", "wind_speed": 12, "humidity": 85}, None
    )
    assert "Windbreaker" in rec["accessories"]
    assert "Windy conditions expected" in rec["special_considerations"]
    assert "Breathable fabrics" in rec["materials"]
    assert "High humidity - choose breathable clothing" in rec["special_considerations"]


def test__generate_clothing_recommendations_no_current():
    ws = WeatherService()
    rec = ws._generate_clothing_recommendations(None, None)
    assert rec == {
        "layers": [],
        "footwear": [],
        "accessories": [],
        "materials": [],
        "special_considerations": [],
    }


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
        "main": {"temp": 20, "feels_like": 19, "humidity": 50, "pressure": 1000},
        "weather": [{"description": "clear sky"}],
        "wind": {"speed": 5},
        # visibility is missing
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await weather_service._get_current_weather(48.8566, 2.3522)
        assert result is not None
        assert result["visibility"] == 0  # Should default to 0 when missing


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
                    "temperature": 20,
                    "feels_like": 19,
                    "humidity": 50,
                    "description": "clear sky",
                    "wind_speed": 5,
                    "visibility": 10,
                    "pressure": 1000,
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
        assert "clothing_recommendations" in result
