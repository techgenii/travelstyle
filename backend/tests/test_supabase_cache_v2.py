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

"""Tests for Enhanced Supabase Cache Service (v2)."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from app.services.supabase import EnhancedSupabaseCacheService
from app.services.supabase.supabase_cache_v2 import (
    CacheEntry,
    CulturalCacheService,
    CurrencyCacheService,
    WeatherCacheService,
    enhanced_supabase_cache,
)


class TestCacheEntry:
    """Test CacheEntry class."""

    def test_cache_entry_creation(self):
        """Test CacheEntry creation."""
        data = {"temperature": 20, "description": "sunny"}
        expires_at = datetime.now(UTC) + timedelta(hours=1)
        created_at = datetime.now(UTC)

        entry = CacheEntry(data, expires_at, created_at)

        assert entry.data == data
        assert entry.expires_at == expires_at
        assert entry.created_at == created_at

    def test_cache_entry_from_dict(self):
        """Test CacheEntry.from_dict method."""
        record = {
            "data": {"temperature": 20, "description": "sunny"},
            "expires_at": "2025-01-01T12:00:00+00:00",
            "created_at": "2025-01-01T11:00:00+00:00",
        }

        entry = CacheEntry.from_dict(record)

        assert entry.data == {"temperature": 20, "description": "sunny"}
        assert entry.expires_at == datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert entry.created_at == datetime(2025, 1, 1, 11, 0, 0, tzinfo=UTC)

    def test_cache_entry_from_dict_with_z_suffix(self):
        """Test CacheEntry.from_dict with Z suffix."""
        record = {
            "data": {"temperature": 20, "description": "sunny"},
            "expires_at": "2025-01-01T12:00:00Z",
            "created_at": "2025-01-01T11:00:00Z",
        }

        entry = CacheEntry.from_dict(record)

        assert entry.data == {"temperature": 20, "description": "sunny"}
        assert entry.expires_at == datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert entry.created_at == datetime(2025, 1, 1, 11, 0, 0, tzinfo=UTC)

    def test_cache_entry_is_expired_future(self):
        """Test is_expired with future date."""
        data = {"temperature": 20}
        expires_at = datetime.now(UTC) + timedelta(hours=1)
        created_at = datetime.now(UTC)

        entry = CacheEntry(data, expires_at, created_at)

        assert entry.is_expired() is False

    def test_cache_entry_is_expired_past(self):
        """Test is_expired with past date."""
        data = {"temperature": 20}
        expires_at = datetime.now(UTC) - timedelta(hours=1)
        created_at = datetime.now(UTC)

        entry = CacheEntry(data, expires_at, created_at)

        assert entry.is_expired() is True

    def test_cache_entry_is_expired_now(self):
        """Test is_expired with current time."""
        data = {"temperature": 20}
        expires_at = datetime.now(UTC)
        created_at = datetime.now(UTC)

        entry = CacheEntry(data, expires_at, created_at)

        assert entry.is_expired() is True


class TestEnhancedSupabaseCacheService:
    """Test EnhancedSupabaseCacheService class."""

    def test_enhanced_supabase_cache_service_init(self):
        """Test EnhancedSupabaseCacheService initialization."""
        service = EnhancedSupabaseCacheService()

        assert service.weather_service is not None
        assert service.cultural_service is not None
        assert service.currency_service is not None

    @pytest.mark.asyncio
    async def test_get_weather_cache_delegation(self):
        """Test get_weather_cache delegates to weather service."""
        with patch.object(enhanced_supabase_cache.weather_service, "get_cache") as mock_get:
            mock_get.return_value = {"temperature": 20}

            result = await enhanced_supabase_cache.get_weather_cache("Paris")

            assert result == {"temperature": 20}
            mock_get.assert_called_once_with("Paris")

    @pytest.mark.asyncio
    async def test_set_weather_cache_delegation(self):
        """Test set_weather_cache delegates to weather service."""
        with patch.object(enhanced_supabase_cache.weather_service, "set_cache") as mock_set:
            mock_set.return_value = True

            result = await enhanced_supabase_cache.set_weather_cache("Paris", {"temp": 20}, 1)

            assert result is True
            mock_set.assert_called_once_with("Paris", {"temp": 20}, 1)

    @pytest.mark.asyncio
    async def test_get_cultural_cache_delegation(self):
        """Test get_cultural_cache delegates to cultural service."""
        with patch.object(enhanced_supabase_cache.cultural_service, "get_cache") as mock_get:
            mock_get.return_value = {"cultural_data": {"customs": "formal"}}

            result = await enhanced_supabase_cache.get_cultural_cache("Paris", "business")

            assert result == {"cultural_data": {"customs": "formal"}}
            mock_get.assert_called_once_with("Paris", "business")

    @pytest.mark.asyncio
    async def test_set_cultural_cache_delegation(self):
        """Test set_cultural_cache delegates to cultural service."""
        with patch.object(enhanced_supabase_cache.cultural_service, "set_cache") as mock_set:
            mock_set.return_value = True

            result = await enhanced_supabase_cache.set_cultural_cache(
                "Paris", "business", {"customs": "formal"}, 24
            )

            assert result is True
            mock_set.assert_called_once_with("Paris", {"customs": "formal"}, 24, "business")

    @pytest.mark.asyncio
    async def test_get_currency_cache_delegation(self):
        """Test get_currency_cache delegates to currency service."""
        with patch.object(enhanced_supabase_cache.currency_service, "get_cache") as mock_get:
            mock_get.return_value = {"USD": 1.0, "EUR": 0.85}

            result = await enhanced_supabase_cache.get_currency_cache("USD")

            assert result == {"USD": 1.0, "EUR": 0.85}
            mock_get.assert_called_once_with("USD")

    @pytest.mark.asyncio
    async def test_set_currency_cache_delegation(self):
        """Test set_currency_cache delegates to currency service."""
        with patch.object(enhanced_supabase_cache.currency_service, "set_cache") as mock_set:
            mock_set.return_value = True

            result = await enhanced_supabase_cache.set_currency_cache("USD", {"EUR": 0.85}, 1)

            assert result is True
            mock_set.assert_called_once_with("USD", {"EUR": 0.85}, 1)


class TestWeatherCacheServiceImplementation:
    """Test WeatherCacheService implementation details."""

    @pytest.fixture
    def weather_service(self):
        """Create a WeatherCacheService instance."""
        return WeatherCacheService()

    def test_weather_service_init(self, weather_service):
        """Test WeatherCacheService initialization."""
        assert weather_service.table_name == "weather_cache"

    def test_weather_service_parse_record(self, weather_service):
        """Test WeatherCacheService._parse_record method."""
        record = {
            "weather_data": {"temperature": 20, "description": "sunny"},
            "expires_at": "2025-01-01T12:00:00+00:00",
            "created_at": "2025-01-01T11:00:00+00:00",
        }

        result = weather_service._parse_record(record)

        assert isinstance(result, CacheEntry)
        assert result.data == {"temperature": 20, "description": "sunny"}
        assert result.expires_at == datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert result.created_at == datetime(2025, 1, 1, 11, 0, 0, tzinfo=UTC)


class TestCulturalCacheServiceImplementation:
    """Test CulturalCacheService implementation details."""

    @pytest.fixture
    def cultural_service(self):
        """Create a CulturalCacheService instance."""
        return CulturalCacheService()

    def test_cultural_service_init(self, cultural_service):
        """Test CulturalCacheService initialization."""
        assert cultural_service.table_name == "cultural_insights_cache"

    def test_cultural_service_parse_record(self, cultural_service):
        """Test CulturalCacheService._parse_record method."""
        record = {
            "cultural_data": {"customs": "formal", "dress_code": "business"},
            "style_data": {"recommendations": "business casual"},
            "expires_at": "2025-01-01T12:00:00+00:00",
            "created_at": "2025-01-01T11:00:00+00:00",
        }

        result = cultural_service._parse_record(record)

        assert isinstance(result, CacheEntry)
        assert result.data == {
            "cultural_data": {"customs": "formal", "dress_code": "business"},
            "style_data": {"recommendations": "business casual"},
        }
        assert result.expires_at == datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert result.created_at == datetime(2025, 1, 1, 11, 0, 0, tzinfo=UTC)


class TestCurrencyCacheServiceImplementation:
    """Test CurrencyCacheService implementation details."""

    @pytest.fixture
    def currency_service(self):
        """Create a CurrencyCacheService instance."""
        return CurrencyCacheService()

    def test_currency_service_init(self, currency_service):
        """Test CurrencyCacheService initialization."""
        assert currency_service.table_name == "currency_rates_cache"

    def test_currency_service_parse_record(self, currency_service):
        """Test CurrencyCacheService._parse_record method."""
        record = {
            "rates_data": {"USD": 1.0, "EUR": 0.85},
            "expires_at": "2025-01-01T12:00:00+00:00",
            "created_at": "2025-01-01T11:00:00+00:00",
        }

        result = currency_service._parse_record(record)

        assert isinstance(result, CacheEntry)
        assert result.data == {"USD": 1.0, "EUR": 0.85}
        assert result.expires_at == datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert result.created_at == datetime(2025, 1, 1, 11, 0, 0, tzinfo=UTC)


class TestRateLimitingIntegration:
    """Test rate limiting integration."""

    @pytest.mark.asyncio
    async def test_rate_limiting_blocks_weather_cache_get(self):
        """Test rate limiting blocks weather cache get."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await enhanced_supabase_cache.get_weather_cache("Paris")

            assert result is None
            mock_acquire.assert_called_once_with("cache")

    @pytest.mark.asyncio
    async def test_rate_limiting_blocks_weather_cache_set(self):
        """Test rate limiting blocks weather cache set."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await enhanced_supabase_cache.set_weather_cache("Paris", {"temp": 20}, 1)

            assert result is False
            mock_acquire.assert_called_once_with("cache")

    @pytest.mark.asyncio
    async def test_rate_limiting_blocks_cultural_cache_get(self):
        """Test rate limiting blocks cultural cache get."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await enhanced_supabase_cache.get_cultural_cache("Paris", "business")

            assert result is None
            mock_acquire.assert_called_once_with("cache")

    @pytest.mark.asyncio
    async def test_rate_limiting_blocks_cultural_cache_set(self):
        """Test rate limiting blocks cultural cache set."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await enhanced_supabase_cache.set_cultural_cache(
                "Paris", "business", {"customs": "formal"}, 24
            )

            assert result is False
            mock_acquire.assert_called_once_with("cache")

    @pytest.mark.asyncio
    async def test_rate_limiting_blocks_currency_cache_get(self):
        """Test rate limiting blocks currency cache get."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await enhanced_supabase_cache.get_currency_cache("USD")

            assert result is None
            mock_acquire.assert_called_once_with("cache")

    @pytest.mark.asyncio
    async def test_rate_limiting_blocks_currency_cache_set(self):
        """Test rate limiting blocks currency cache set."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await enhanced_supabase_cache.set_currency_cache("USD", {"EUR": 0.85}, 1)

            assert result is False
            mock_acquire.assert_called_once_with("cache")


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_weather_service_get_cache_exception_handling(self):
        """Test weather service get_cache exception handling."""
        weather_service = WeatherCacheService()

        with patch.object(weather_service, "get_by_field") as mock_get_by_field:
            mock_get_by_field.side_effect = Exception("Database error")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await weather_service.get_cache("Paris")

                assert result is None

    @pytest.mark.asyncio
    async def test_weather_service_set_cache_exception_handling(self):
        """Test weather service set_cache exception handling."""
        weather_service = WeatherCacheService()

        with patch.object(weather_service, "upsert") as mock_upsert:
            mock_upsert.side_effect = Exception("Database error")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await weather_service.set_cache("Paris", {"temp": 20}, 1)

                assert result is False

    @pytest.mark.asyncio
    async def test_cultural_service_get_cache_exception_handling(self):
        """Test cultural service get_cache exception handling."""
        cultural_service = CulturalCacheService()

        with patch.object(cultural_service, "get_by_field") as mock_get_by_field:
            mock_get_by_field.side_effect = Exception("Database error")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await cultural_service.get_cache("Paris", "business")

                assert result is None

    @pytest.mark.asyncio
    async def test_cultural_service_set_cache_exception_handling(self):
        """Test cultural service set_cache exception handling."""
        cultural_service = CulturalCacheService()

        with patch.object(cultural_service, "upsert") as mock_upsert:
            mock_upsert.side_effect = Exception("Database error")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await cultural_service.set_cache(
                    "Paris", {"customs": "formal"}, 24, "business"
                )

                assert result is False

    @pytest.mark.asyncio
    async def test_currency_service_get_cache_exception_handling(self):
        """Test currency service get_cache exception handling."""
        currency_service = CurrencyCacheService()

        with patch.object(currency_service, "get_by_field") as mock_get_by_field:
            mock_get_by_field.side_effect = Exception("Database error")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await currency_service.get_cache("USD")

                assert result is None

    @pytest.mark.asyncio
    async def test_currency_service_set_cache_exception_handling(self):
        """Test currency service set_cache exception handling."""
        currency_service = CurrencyCacheService()

        with patch.object(currency_service, "upsert") as mock_upsert:
            mock_upsert.side_effect = Exception("Database error")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await currency_service.set_cache("USD", {"EUR": 0.85}, 1)

                assert result is False


class TestServiceMethods:
    """Test individual service methods."""

    @pytest.mark.asyncio
    async def test_weather_service_get_cache_success(self):
        """Test WeatherCacheService.get_cache success."""
        weather_service = WeatherCacheService()

        with patch.object(weather_service, "get_by_field") as mock_get_by_field:
            mock_entry = MagicMock()
            mock_entry.is_expired.return_value = False
            mock_entry.data = {"temperature": 20, "description": "sunny"}
            mock_get_by_field.return_value = [mock_entry]

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await weather_service.get_cache("Paris")

                assert result == {"temperature": 20, "description": "sunny"}
                mock_get_by_field.assert_called_once_with("destination", "Paris")

    @pytest.mark.asyncio
    async def test_weather_service_get_cache_expired(self):
        """Test WeatherCacheService.get_cache with expired entry."""
        weather_service = WeatherCacheService()

        with patch.object(weather_service, "get_by_field") as mock_get_by_field:
            mock_entry = MagicMock()
            mock_entry.is_expired.return_value = True
            mock_get_by_field.return_value = [mock_entry]

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await weather_service.get_cache("Paris")

                assert result is None

    @pytest.mark.asyncio
    async def test_weather_service_get_cache_no_results(self):
        """Test WeatherCacheService.get_cache with no results."""
        weather_service = WeatherCacheService()

        with patch.object(weather_service, "get_by_field") as mock_get_by_field:
            mock_get_by_field.return_value = []

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await weather_service.get_cache("Paris")

                assert result is None

    @pytest.mark.asyncio
    async def test_weather_service_set_cache_success(self):
        """Test WeatherCacheService.set_cache success."""
        weather_service = WeatherCacheService()

        with patch.object(weather_service, "upsert") as mock_upsert:
            mock_upsert.return_value = MagicMock()

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await weather_service.set_cache("Paris", {"temp": 20}, 1)

                assert result is True
                mock_upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_weather_service_set_cache_failure(self):
        """Test WeatherCacheService.set_cache failure."""
        weather_service = WeatherCacheService()

        with patch.object(weather_service, "upsert") as mock_upsert:
            mock_upsert.return_value = None

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await weather_service.set_cache("Paris", {"temp": 20}, 1)

                assert result is False

    @pytest.mark.asyncio
    async def test_cultural_service_get_cache_success(self):
        """Test CulturalCacheService.get_cache success."""
        cultural_service = CulturalCacheService()

        with patch.object(cultural_service, "get_by_field") as mock_get_by_field:
            mock_entry = MagicMock()
            mock_entry.is_expired.return_value = False
            mock_entry.data = {
                "cultural_data": {"customs": "formal", "dress_code": "business"},
                "style_data": {"recommendations": "business casual"},
            }
            mock_get_by_field.return_value = [mock_entry]

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await cultural_service.get_cache("Paris", "business")

                assert result == {
                    "cultural_data": {"customs": "formal", "dress_code": "business"},
                    "style_data": {"recommendations": "business casual"},
                }
                mock_get_by_field.assert_called_once_with("destination", "Paris")

    @pytest.mark.asyncio
    async def test_cultural_service_set_cache_success(self):
        """Test CulturalCacheService.set_cache success."""
        cultural_service = CulturalCacheService()

        with patch.object(cultural_service, "upsert") as mock_upsert:
            mock_upsert.return_value = MagicMock()

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await cultural_service.set_cache(
                    "Paris", {"customs": "formal"}, 24, "business"
                )

                assert result is True
                mock_upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_currency_service_get_cache_success(self):
        """Test CurrencyCacheService.get_cache success."""
        currency_service = CurrencyCacheService()

        with patch.object(currency_service, "get_by_field") as mock_get_by_field:
            mock_entry = MagicMock()
            mock_entry.is_expired.return_value = False
            mock_entry.data = {"USD": 1.0, "EUR": 0.85}
            mock_get_by_field.return_value = [mock_entry]

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await currency_service.get_cache("USD")

                assert result == {"USD": 1.0, "EUR": 0.85}
                mock_get_by_field.assert_called_once_with("base_currency", "USD")

    @pytest.mark.asyncio
    async def test_currency_service_set_cache_success(self):
        """Test CurrencyCacheService.set_cache success."""
        currency_service = CurrencyCacheService()

        with patch.object(currency_service, "upsert") as mock_upsert:
            mock_upsert.return_value = MagicMock()

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await currency_service.set_cache("USD", {"EUR": 0.85}, 1)

                assert result is True
                mock_upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_weather_service_rate_limiting_warning(self):
        """Test weather service rate limiting warning."""
        weather_service = WeatherCacheService()

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await weather_service.get_cache("Paris")

            assert result is None
            mock_acquire.assert_called_once_with("cache")

    @pytest.mark.asyncio
    async def test_cultural_service_rate_limiting_warning(self):
        """Test cultural service rate limiting warning."""
        cultural_service = CulturalCacheService()

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await cultural_service.get_cache("Paris", "business")

            assert result is None
            mock_acquire.assert_called_once_with("cache")

    @pytest.mark.asyncio
    async def test_currency_service_rate_limiting_warning(self):
        """Test currency service rate limiting warning."""
        currency_service = CurrencyCacheService()

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
            mock_acquire.return_value = False

            result = await currency_service.get_cache("USD")

            assert result is None
            mock_acquire.assert_called_once_with("cache")

    @pytest.mark.asyncio
    async def test_weather_service_logger_error(self):
        """Test weather service logger error statement."""
        weather_service = WeatherCacheService()

        with patch.object(weather_service, "get_by_field") as mock_get_by_field:
            mock_get_by_field.side_effect = Exception("Database connection failed")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await weather_service.get_cache("Paris")

                assert result is None

    @pytest.mark.asyncio
    async def test_cultural_service_logger_error(self):
        """Test cultural service logger error statement."""
        cultural_service = CulturalCacheService()

        with patch.object(cultural_service, "get_by_field") as mock_get_by_field:
            mock_get_by_field.side_effect = Exception("Database connection failed")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await cultural_service.get_cache("Paris", "business")

                assert result is None

    @pytest.mark.asyncio
    async def test_currency_service_logger_error(self):
        """Test currency service logger error statement."""
        currency_service = CurrencyCacheService()

        with patch.object(currency_service, "get_by_field") as mock_get_by_field:
            mock_get_by_field.side_effect = Exception("Database connection failed")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await currency_service.get_cache("USD")

                assert result is None

    @pytest.mark.asyncio
    async def test_weather_service_set_cache_logger_error(self):
        """Test weather service set_cache logger error statement."""
        weather_service = WeatherCacheService()

        with patch.object(weather_service, "upsert") as mock_upsert:
            mock_upsert.side_effect = Exception("Database connection failed")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await weather_service.set_cache("Paris", {"temp": 20}, 1)

                assert result is False

    @pytest.mark.asyncio
    async def test_cultural_service_set_cache_logger_error(self):
        """Test cultural service set_cache logger error statement."""
        cultural_service = CulturalCacheService()

        with patch.object(cultural_service, "upsert") as mock_upsert:
            mock_upsert.side_effect = Exception("Database connection failed")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await cultural_service.set_cache(
                    "Paris", {"customs": "formal"}, 24, "business"
                )

                assert result is False

    @pytest.mark.asyncio
    async def test_currency_service_set_cache_logger_error(self):
        """Test currency service set_cache logger error statement."""
        currency_service = CurrencyCacheService()

        with patch.object(currency_service, "upsert") as mock_upsert:
            mock_upsert.side_effect = Exception("Database connection failed")

            with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_acquire:
                mock_acquire.return_value = True

                result = await currency_service.set_cache("USD", {"EUR": 0.85}, 1)

                assert result is False
