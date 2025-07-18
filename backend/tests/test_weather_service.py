from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.weather_service import WeatherService


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
        result = await weather_service._get_current_weather("London")
        assert result["temperature"] == 20
        assert result["description"] == "light rain"
        assert result["wind_speed"] == 7
        assert result["visibility"] == 5
        assert result["pressure"] == 1000


@pytest.mark.asyncio
async def test__get_current_weather_error(weather_service):
    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=Exception("fail"))):
        result = await weather_service._get_current_weather("London")
        assert result is None


@pytest.mark.asyncio
async def test__get_forecast_success(weather_service):
    # Simulate OpenWeather forecast API response
    from datetime import datetime as dt

    now = dt.now()
    timestamp = int(now.timestamp())
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "list": [
            {"dt": timestamp, "main": {"temp": 10}, "weather": [{"main": "Rain"}]},
            {"dt": timestamp + 3600, "main": {"temp": 12}, "weather": [{"main": "Clear"}]},
            {"dt": timestamp + 7200, "main": {"temp": 8}, "weather": [{"main": "Rain"}]},
        ]
    }
    mock_response.raise_for_status = MagicMock()
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await weather_service._get_forecast("London")
        assert "daily_forecasts" in result
        assert "temp_range" in result
        assert "precipitation_chance" in result


@pytest.mark.asyncio
async def test__get_forecast_error(weather_service):
    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=Exception("fail"))):
        result = await weather_service._get_forecast("London")
        assert result is None


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
