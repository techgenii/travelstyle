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

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.supabase import supabase_cache
from app.services.supabase.supabase_cache import (
    CulturalCacheHandler,
    CurrencyCacheHandler,
    SupabaseCacheService,
    WeatherCacheHandler,
)


class TestCacheHandler:
    """Test CacheHandler abstract base class."""

    def test_cache_handler_init(self):
        """Test CacheHandler initialization."""
        mock_client = MagicMock()
        handler = WeatherCacheHandler(mock_client)

        assert handler.client == mock_client

    def test_is_expired_future(self):
        """Test is_expired with future date returns False."""
        mock_client = MagicMock()
        handler = WeatherCacheHandler(mock_client)

        future_time = datetime.now(UTC) + timedelta(hours=1)
        result = handler._is_expired(future_time.isoformat())

        assert result is False

    def test_is_expired_past(self):
        """Test is_expired with past date returns True."""
        mock_client = MagicMock()
        handler = WeatherCacheHandler(mock_client)

        past_time = datetime.now(UTC) - timedelta(hours=1)
        result = handler._is_expired(past_time.isoformat())

        assert result is True

    def test_is_expired_invalid_format(self):
        """Test is_expired with invalid format returns True."""
        mock_client = MagicMock()
        handler = WeatherCacheHandler(mock_client)

        result = handler._is_expired("invalid-date")

        assert result is True

    def test_is_expired_with_z_suffix(self):
        """Test is_expired with Z suffix works correctly."""
        mock_client = MagicMock()
        handler = WeatherCacheHandler(mock_client)

        future_time = datetime.now(UTC) + timedelta(hours=1)
        z_format = future_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        result = handler._is_expired(z_format)

        assert result is False

    @pytest.mark.asyncio
    async def test_apply_rate_limiting_success(self):
        """Test _apply_rate_limiting when rate limiter allows."""
        mock_client = MagicMock()
        handler = WeatherCacheHandler(mock_client)

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = True

            result = await handler._apply_rate_limiting("test_operation")

            assert result is True
            mock_acquire.assert_called_once_with("cache")

    @pytest.mark.asyncio
    async def test_apply_rate_limiting_blocked(self):
        """Test _apply_rate_limiting when rate limiter blocks."""
        mock_client = MagicMock()
        handler = WeatherCacheHandler(mock_client)

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await handler._apply_rate_limiting("test_operation")

            assert result is False
            mock_acquire.assert_called_once_with("cache")


class TestWeatherCacheHandler:
    """Test WeatherCacheHandler class."""

    @pytest.fixture
    def weather_handler(self):
        """Create a WeatherCacheHandler instance."""
        mock_client = MagicMock()
        return WeatherCacheHandler(mock_client)

    @pytest.mark.asyncio
    async def test_get_cache_success(self, weather_handler):
        """Test successful weather cache retrieval."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "destination": "Paris",
                "weather_data": {"temperature": 20, "description": "sunny"},
                "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
            }
        ]

        with patch.object(weather_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await weather_handler.get_cache("Paris")

                assert result == {"temperature": 20, "description": "sunny"}

    @pytest.mark.asyncio
    async def test_get_cache_expired(self, weather_handler):
        """Test weather cache retrieval with expired data."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "destination": "Paris",
                "weather_data": {"temperature": 20, "description": "sunny"},
                "expires_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
            }
        ]

        with patch.object(weather_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await weather_handler.get_cache("Paris")

                assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_no_data(self, weather_handler):
        """Test weather cache retrieval with no data."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch.object(weather_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await weather_handler.get_cache("Paris")

                assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_rate_limited(self, weather_handler):
        """Test weather cache retrieval when rate limited."""
        with patch.object(weather_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await weather_handler.get_cache("Paris")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_exception(self, weather_handler):
        """Test weather cache retrieval with exception."""
        with patch.object(weather_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await weather_handler.get_cache("Paris")

                assert result is None

    @pytest.mark.asyncio
    async def test_set_cache_success(self, weather_handler):
        """Test successful weather cache setting."""
        with patch.object(weather_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = None

                result = await weather_handler.set_cache("Paris", {"temp": 20}, 1)

                assert result is True

    @pytest.mark.asyncio
    async def test_set_cache_rate_limited(self, weather_handler):
        """Test weather cache setting when rate limited."""
        with patch.object(weather_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await weather_handler.set_cache("Paris", {"temp": 20}, 1)

            assert result is False

    @pytest.mark.asyncio
    async def test_set_cache_exception(self, weather_handler):
        """Test weather cache setting with exception."""
        with patch.object(weather_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await weather_handler.set_cache("Paris", {"temp": 20}, 1)

                assert result is False


class TestCulturalCacheHandler:
    """Test CulturalCacheHandler class."""

    @pytest.fixture
    def cultural_handler(self):
        """Create a CulturalCacheHandler instance."""
        mock_client = MagicMock()
        return CulturalCacheHandler(mock_client)

    @pytest.mark.asyncio
    async def test_get_cache_success(self, cultural_handler):
        """Test successful cultural cache retrieval."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "destination": "Paris",
                "cultural_data": {"customs": "formal", "dress_code": "business"},
                "style_data": {"recommendations": "business casual"},
                "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
            }
        ]

        with patch.object(cultural_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await cultural_handler.get_cache("Paris", "business")

                assert result == {
                    "cultural_data": {"customs": "formal", "dress_code": "business"},
                    "style_data": {"recommendations": "business casual"},
                }

    @pytest.mark.asyncio
    async def test_get_cache_expired(self, cultural_handler):
        """Test cultural cache retrieval with expired data."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "destination": "Paris",
                "cultural_data": {"customs": "formal"},
                "style_data": {"recommendations": "business casual"},
                "expires_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
            }
        ]

        with patch.object(cultural_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await cultural_handler.get_cache("Paris", "business")

                assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_no_data(self, cultural_handler):
        """Test cultural cache retrieval with no data."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch.object(cultural_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await cultural_handler.get_cache("Paris", "business")

                assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_rate_limited(self, cultural_handler):
        """Test cultural cache retrieval when rate limited."""
        with patch.object(cultural_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await cultural_handler.get_cache("Paris", "business")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_exception(self, cultural_handler):
        """Test cultural cache retrieval with exception."""
        with patch.object(cultural_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await cultural_handler.get_cache("Paris", "business")

                assert result is None

    @pytest.mark.asyncio
    async def test_set_cache_success(self, cultural_handler):
        """Test successful cultural cache setting."""
        with patch.object(cultural_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = None

                result = await cultural_handler.set_cache(
                    "Paris", {"customs": "formal"}, 24, "business"
                )

                assert result is True

    @pytest.mark.asyncio
    async def test_set_cache_rate_limited(self, cultural_handler):
        """Test cultural cache setting when rate limited."""
        with patch.object(cultural_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await cultural_handler.set_cache(
                "Paris", {"customs": "formal"}, 24, "business"
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_set_cache_exception(self, cultural_handler):
        """Test cultural cache setting with exception."""
        with patch.object(cultural_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await cultural_handler.set_cache(
                    "Paris", {"customs": "formal"}, 24, "business"
                )

                assert result is False


class TestCurrencyCacheHandler:
    """Test CurrencyCacheHandler class."""

    @pytest.fixture
    def currency_handler(self):
        """Create a CurrencyCacheHandler instance."""
        mock_client = MagicMock()
        return CurrencyCacheHandler(mock_client)

    @pytest.mark.asyncio
    async def test_get_cache_success(self, currency_handler):
        """Test successful currency cache retrieval."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "base_currency": "USD",
                "rates_data": {"USD": 1.0, "EUR": 0.85},
                "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
            }
        ]

        with patch.object(currency_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await currency_handler.get_cache("USD")

                assert result == {"USD": 1.0, "EUR": 0.85}

    @pytest.mark.asyncio
    async def test_get_cache_expired(self, currency_handler):
        """Test currency cache retrieval with expired data."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "base_currency": "USD",
                "rates_data": {"USD": 1.0, "EUR": 0.85},
                "expires_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
            }
        ]

        with patch.object(currency_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await currency_handler.get_cache("USD")

                assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_no_data(self, currency_handler):
        """Test currency cache retrieval with no data."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch.object(currency_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await currency_handler.get_cache("USD")

                assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_rate_limited(self, currency_handler):
        """Test currency cache retrieval when rate limited."""
        with patch.object(currency_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await currency_handler.get_cache("USD")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_exception(self, currency_handler):
        """Test currency cache retrieval with exception."""
        with patch.object(currency_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await currency_handler.get_cache("USD")

                assert result is None

    @pytest.mark.asyncio
    async def test_set_cache_success(self, currency_handler):
        """Test successful currency cache setting."""
        with patch.object(currency_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = None

                result = await currency_handler.set_cache("USD", {"EUR": 0.85}, 1)

                assert result is True

    @pytest.mark.asyncio
    async def test_set_cache_rate_limited(self, currency_handler):
        """Test currency cache setting when rate limited."""
        with patch.object(currency_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await currency_handler.set_cache("USD", {"EUR": 0.85}, 1)

            assert result is False

    @pytest.mark.asyncio
    async def test_set_cache_exception(self, currency_handler):
        """Test currency cache setting with exception."""
        with patch.object(currency_handler, "_apply_rate_limiting") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await currency_handler.set_cache("USD", {"EUR": 0.85}, 1)

                assert result is False


class TestSupabaseCacheService:
    """Test SupabaseCacheService class."""

    def test_supabase_cache_service_init(self):
        """Test SupabaseCacheService initialization."""
        with patch("app.services.supabase.supabase_cache.get_supabase_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            service = SupabaseCacheService()

            assert service.weather_handler is not None
            assert service.cultural_handler is not None
            assert service.currency_handler is not None
            assert service.weather_handler.client == mock_client
            assert service.cultural_handler.client == mock_client
            assert service.currency_handler.client == mock_client


@pytest.fixture
def mock_weather_handler():
    """Mock the weather handler."""
    mock_handler = MagicMock()
    mock_handler.get_cache = AsyncMock()
    mock_handler.set_cache = AsyncMock()
    with patch.object(supabase_cache, "weather_handler", mock_handler):
        yield mock_handler


@pytest.fixture
def mock_cultural_handler():
    """Mock the cultural handler."""
    mock_handler = MagicMock()
    mock_handler.get_cache = AsyncMock()
    mock_handler.set_cache = AsyncMock()
    with patch.object(supabase_cache, "cultural_handler", mock_handler):
        yield mock_handler


@pytest.fixture
def mock_currency_handler():
    """Mock the currency handler."""
    mock_handler = MagicMock()
    mock_handler.get_cache = AsyncMock()
    mock_handler.set_cache = AsyncMock()
    with patch.object(supabase_cache, "currency_handler", mock_handler):
        yield mock_handler


@pytest.mark.asyncio
async def test_get_weather_cache_success(mock_weather_handler):
    """Test successful weather cache retrieval."""
    expected_data = {"temperature": 20, "description": "sunny"}
    mock_weather_handler.get_cache.return_value = expected_data

    result = await supabase_cache.get_weather_cache("Paris")

    assert result == expected_data
    mock_weather_handler.get_cache.assert_called_once_with("Paris")


@pytest.mark.asyncio
async def test_get_weather_cache_expired(mock_weather_handler):
    """Test expired weather cache returns None."""
    mock_weather_handler.get_cache.return_value = None

    result = await supabase_cache.get_weather_cache("Paris")

    assert result is None
    mock_weather_handler.get_cache.assert_called_once_with("Paris")


@pytest.mark.asyncio
async def test_get_weather_cache_not_found(mock_weather_handler):
    """Test weather cache not found returns None."""
    mock_weather_handler.get_cache.return_value = None

    result = await supabase_cache.get_weather_cache("Paris")

    assert result is None
    mock_weather_handler.get_cache.assert_called_once_with("Paris")


@pytest.mark.asyncio
async def test_set_weather_cache_success(mock_weather_handler):
    """Test successful weather cache setting."""
    mock_weather_handler.set_cache.return_value = True
    weather_data = {"temperature": 20, "description": "sunny"}

    result = await supabase_cache.set_weather_cache("Paris", weather_data, ttl_hours=1)

    assert result is True
    mock_weather_handler.set_cache.assert_called_once_with("Paris", weather_data, 1)


@pytest.mark.asyncio
async def test_set_weather_cache_error(mock_weather_handler):
    """Test weather cache setting error."""
    mock_weather_handler.set_cache.return_value = False
    weather_data = {"temperature": 20, "description": "sunny"}

    result = await supabase_cache.set_weather_cache("Paris", weather_data, ttl_hours=1)

    assert result is False
    mock_weather_handler.set_cache.assert_called_once_with("Paris", weather_data, 1)


@pytest.mark.asyncio
async def test_get_cultural_cache_success(mock_cultural_handler):
    """Test successful cultural cache retrieval."""
    expected_data = {
        "cultural_data": {"customs": "formal", "dress_code": "business"},
        "style_data": {"recommendations": "business casual"},
    }
    mock_cultural_handler.get_cache.return_value = expected_data

    result = await supabase_cache.get_cultural_cache("Paris", "business")

    assert result == expected_data
    mock_cultural_handler.get_cache.assert_called_once_with("Paris", "business")


@pytest.mark.asyncio
async def test_get_cultural_cache_expired(mock_cultural_handler):
    """Test expired cultural cache returns None."""
    mock_cultural_handler.get_cache.return_value = None

    result = await supabase_cache.get_cultural_cache("Paris", "business")

    assert result is None
    mock_cultural_handler.get_cache.assert_called_once_with("Paris", "business")


@pytest.mark.asyncio
async def test_set_cultural_cache_success(mock_cultural_handler):
    """Test successful cultural cache setting."""
    mock_cultural_handler.set_cache.return_value = True
    cultural_data = {"customs": "formal", "dress_code": "business"}

    result = await supabase_cache.set_cultural_cache(
        "Paris", "business", cultural_data, ttl_hours=24
    )

    assert result is True
    mock_cultural_handler.set_cache.assert_called_once_with("Paris", cultural_data, 24, "business")


@pytest.mark.asyncio
async def test_get_currency_cache_success(mock_currency_handler):
    """Test successful currency cache retrieval."""
    expected_data = {"USD": 1.0, "EUR": 0.85}
    mock_currency_handler.get_cache.return_value = expected_data

    result = await supabase_cache.get_currency_cache("USD")

    assert result == expected_data
    mock_currency_handler.get_cache.assert_called_once_with("USD")


@pytest.mark.asyncio
async def test_get_currency_cache_empty(mock_currency_handler):
    """Test empty currency cache returns None."""
    mock_currency_handler.get_cache.return_value = None

    result = await supabase_cache.get_currency_cache("USD")

    assert result is None
    mock_currency_handler.get_cache.assert_called_once_with("USD")


@pytest.mark.asyncio
async def test_set_currency_cache_success(mock_currency_handler):
    """Test successful currency cache setting."""
    mock_currency_handler.set_cache.return_value = True
    currency_data = {"USD": 1.0, "EUR": 0.85}

    result = await supabase_cache.set_currency_cache("USD", currency_data, ttl_hours=1)

    assert result is True
    mock_currency_handler.set_cache.assert_called_once_with("USD", currency_data, 1)


def test_is_expired_future():
    """Test is_expired with future date returns False."""
    mock_client = MagicMock()
    handler = WeatherCacheHandler(mock_client)
    future_time = datetime.now(UTC) + timedelta(hours=1)
    result = handler._is_expired(future_time.isoformat())
    assert result is False


def test_is_expired_past():
    """Test is_expired with past date returns True."""
    mock_client = MagicMock()
    handler = WeatherCacheHandler(mock_client)
    past_time = datetime.now(UTC) - timedelta(hours=1)
    result = handler._is_expired(past_time.isoformat())
    assert result is True


def test_is_expired_invalid_format():
    """Test is_expired with invalid format returns True."""
    mock_client = MagicMock()
    handler = WeatherCacheHandler(mock_client)
    result = handler._is_expired("invalid-date")
    assert result is True


def test_is_expired_with_z_suffix():
    """Test is_expired with Z suffix works correctly."""
    mock_client = MagicMock()
    handler = WeatherCacheHandler(mock_client)
    future_time = datetime.now(UTC) + timedelta(hours=1)
    z_format = future_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    result = handler._is_expired(z_format)
    assert result is False


@pytest.mark.asyncio
async def test_get_weather_cache_no_expires_at(mock_weather_handler):
    """Test weather cache retrieval with no expires_at field."""
    mock_weather_handler.get_cache.return_value = None

    result = await supabase_cache.get_weather_cache("Paris")

    assert result is None
    mock_weather_handler.get_cache.assert_called_once_with("Paris")


@pytest.mark.asyncio
async def test_get_cultural_cache_error(mock_cultural_handler):
    """Test cultural cache retrieval error."""
    mock_cultural_handler.get_cache.return_value = None

    result = await supabase_cache.get_cultural_cache("Paris", "business")

    assert result is None
    mock_cultural_handler.get_cache.assert_called_once_with("Paris", "business")


@pytest.mark.asyncio
async def test_set_cultural_cache_error(mock_cultural_handler):
    """Test cultural cache setting error."""
    mock_cultural_handler.set_cache.return_value = False
    cultural_data = {"customs": "formal", "dress_code": "business"}

    result = await supabase_cache.set_cultural_cache(
        "Paris", "business", cultural_data, ttl_hours=24
    )

    assert result is False
    mock_cultural_handler.set_cache.assert_called_once_with("Paris", cultural_data, 24, "business")


@pytest.mark.asyncio
async def test_get_currency_cache_error(mock_currency_handler):
    """Test currency cache retrieval error."""
    mock_currency_handler.get_cache.return_value = None

    result = await supabase_cache.get_currency_cache("USD")

    assert result is None
    mock_currency_handler.get_cache.assert_called_once_with("USD")


@pytest.mark.asyncio
async def test_set_currency_cache_error(mock_currency_handler):
    """Test currency cache setting error."""
    mock_currency_handler.set_cache.return_value = False
    currency_data = {"USD": 1.0, "EUR": 0.85}

    result = await supabase_cache.set_currency_cache("USD", currency_data, ttl_hours=1)

    assert result is False
    mock_currency_handler.set_cache.assert_called_once_with("USD", currency_data, 1)
