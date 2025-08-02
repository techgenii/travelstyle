"""
Test cache improvements to ensure proper handling of duplicate entries.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from app.services.supabase.supabase_cache_v2 import (
    CacheEntry,
    WeatherCacheService,
    enhanced_supabase_cache,
)


class TestCacheImprovements:
    """Test cache improvements for preventing duplicate entries."""

    def test_cache_entry_expiration(self):
        """Test that cache entries properly handle expiration."""
        # Create a cache entry that expires in 1 hour
        expires_at = datetime.now(UTC) + timedelta(hours=1)
        created_at = datetime.now(UTC)

        entry = CacheEntry(data={"temp": 20}, expires_at=expires_at, created_at=created_at)

        # Should not be expired
        assert not entry.is_expired()

        # Create an expired entry
        expired_at = datetime.now(UTC) - timedelta(hours=1)
        expired_entry = CacheEntry(data={"temp": 20}, expires_at=expired_at, created_at=created_at)

        # Should be expired
        assert expired_entry.is_expired()

    @pytest.mark.asyncio
    async def test_weather_cache_service_get_most_recent_non_expired(self):
        """Test that the cache service returns the most recent non-expired entry."""
        # Mock the base service methods
        with patch.object(WeatherCacheService, "get_by_field") as mock_get_by_field:
            # Create multiple cache entries with different timestamps
            now = datetime.now(UTC)
            entry1 = CacheEntry(
                data={"temp": 20, "source": "old"},
                expires_at=now + timedelta(hours=1),
                created_at=now - timedelta(hours=2),
            )
            entry2 = CacheEntry(
                data={"temp": 25, "source": "new"},
                expires_at=now + timedelta(hours=1),
                created_at=now - timedelta(hours=1),
            )
            entry3 = CacheEntry(
                data={"temp": 30, "source": "expired"},
                expires_at=now - timedelta(hours=1),  # Expired
                created_at=now - timedelta(hours=3),
            )

            # Mock the service to return multiple entries
            mock_get_by_field.return_value = [entry1, entry2, entry3]

            service = WeatherCacheService()
            result = await service.get_cache("Paris")

            # Should return the most recent non-expired entry (entry2)
            assert result == {"temp": 25, "source": "new"}

    @pytest.mark.asyncio
    async def test_weather_cache_service_get_all_expired(self):
        """Test that the cache service returns None when all entries are expired."""
        with patch.object(WeatherCacheService, "get_by_field") as mock_get_by_field:
            # Create expired cache entries
            now = datetime.now(UTC)
            entry1 = CacheEntry(
                data={"temp": 20},
                expires_at=now - timedelta(hours=1),  # Expired
                created_at=now - timedelta(hours=2),
            )
            entry2 = CacheEntry(
                data={"temp": 25},
                expires_at=now - timedelta(hours=30),  # Expired
                created_at=now - timedelta(hours=3),
            )

            mock_get_by_field.return_value = [entry1, entry2]

            service = WeatherCacheService()
            result = await service.get_cache("Paris")

            # Should return None when all entries are expired
            assert result is None

    @pytest.mark.asyncio
    async def test_weather_cache_service_set_with_api_source(self):
        """Test that the cache service includes API source in upsert."""
        with patch.object(WeatherCacheService, "upsert") as mock_upsert:
            mock_upsert.return_value = CacheEntry(
                data={"temp": 20},
                expires_at=datetime.now(UTC) + timedelta(hours=1),
                created_at=datetime.now(UTC),
            )

            service = WeatherCacheService()
            result = await service.set_cache("Paris", {"temp": 20}, 1)

            # Verify that upsert was called with the correct data including API source
            mock_upsert.assert_called_once()
            call_args = mock_upsert.call_args[0][0]  # First argument is the data dict
            assert call_args["destination"] == "Paris"
            assert call_args["api_source"] == "openweathermap"
            assert call_args["weather_data"] == {"temp": 20}
            assert result is True

    @pytest.mark.asyncio
    async def test_enhanced_cache_service_integration(self):
        """Test the enhanced cache service integration."""
        with patch.object(enhanced_supabase_cache.weather_service, "get_cache") as mock_get:
            mock_get.return_value = {"temp": 20}

            result = await enhanced_supabase_cache.get_weather_cache("Paris")
            assert result == {"temp": 20}
            mock_get.assert_called_once_with("Paris")

        with patch.object(enhanced_supabase_cache.weather_service, "set_cache") as mock_set:
            mock_set.return_value = True

            result = await enhanced_supabase_cache.set_weather_cache("Paris", {"temp": 20}, 1)
            assert result is True
            mock_set.assert_called_once_with("Paris", {"temp": 20}, 1)
