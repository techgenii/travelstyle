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

"""
Enhanced Supabase cache service using the base service pattern.
Provides improved caching functionality with better error handling and type safety.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from app.services.rate_limiter import db_rate_limiter

from .supabase_base import SupabaseBaseService

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cache entry with metadata."""

    def __init__(self, data: dict[str, Any], expires_at: datetime, created_at: datetime):
        self.data = data
        self.expires_at = expires_at
        self.created_at = created_at

    @classmethod
    def from_dict(cls, record: dict[str, Any]) -> "CacheEntry":
        """Create a CacheEntry from a database record."""
        expires_at = datetime.fromisoformat(record.get("expires_at", "").replace("Z", "+00:00"))
        created_at = datetime.fromisoformat(record.get("created_at", "").replace("Z", "+00:00"))
        return cls(record.get("data", {}), expires_at, created_at)

    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        return datetime.now(UTC) > self.expires_at


class WeatherCacheService(SupabaseBaseService[CacheEntry]):
    """Service for weather cache operations."""

    def __init__(self):
        super().__init__("weather_cache")

    def _parse_record(self, record: dict[str, Any]) -> CacheEntry:
        """Parse a weather cache record."""
        return CacheEntry.from_dict(
            {
                "data": record.get("weather_data", {}),
                "expires_at": record.get("expires_at"),
                "created_at": record.get("created_at"),
            }
        )

    async def get_cache(self, destination: str) -> dict[str, Any] | None:
        """Get cached weather data for destination."""
        if not await db_rate_limiter.acquire("cache"):
            logger.warning("Rate limited: get_weather_cache")
            return None

        try:
            records = await self.get_by_field("destination", destination)
            if not records:
                return None

            # Find the most recent non-expired record
            for record in sorted(records, key=lambda r: r.created_at, reverse=True):
                if not record.is_expired():
                    return record.data

            return None
        except Exception as e:
            logger.error(f"Weather cache get error: {e}")
            return None

    async def set_cache(self, destination: str, data: dict[str, Any], ttl_hours: int = 1) -> bool:
        """Cache weather data for destination."""
        if not await db_rate_limiter.acquire("cache"):
            logger.warning("Rate limited: set_weather_cache")
            return False

        try:
            expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)
            cache_data = {
                "destination": destination,
                "destination_normalized": destination.lower(),
                "weather_data": data,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(UTC).isoformat(),
                "api_source": "openweathermap",  # Add API source for unique constraint
            }
            result = await self.upsert(cache_data, ["destination", "api_source"])
            return result is not None
        except Exception as e:
            logger.error(f"Weather cache set error: {e}")
            return False


class CulturalCacheService(SupabaseBaseService[CacheEntry]):
    """Service for cultural cache operations."""

    def __init__(self):
        super().__init__("cultural_insights_cache")

    def _parse_record(self, record: dict[str, Any]) -> CacheEntry:
        """Parse a cultural cache record."""
        return CacheEntry.from_dict(
            {
                "data": {
                    "cultural_data": record.get("cultural_data", {}),
                    "style_data": record.get("style_data", {}),
                },
                "expires_at": record.get("expires_at"),
                "created_at": record.get("created_at"),
            }
        )

    async def get_cache(self, destination: str, context: str = "leisure") -> dict[str, Any] | None:
        """Get cached cultural insights for destination."""
        if not await db_rate_limiter.acquire("cache"):
            logger.warning("Rate limited: get_cultural_cache")
            return None

        try:
            records = await self.get_by_field("destination", destination)
            if not records:
                return None

            # Find the most recent non-expired record
            for record in sorted(records, key=lambda r: r.created_at, reverse=True):
                if not record.is_expired():
                    return record.data

            return None
        except Exception as e:
            logger.error(f"Cultural cache get error: {e}")
            return None

    async def set_cache(
        self, destination: str, data: dict[str, Any], ttl_hours: int = 24, context: str = "leisure"
    ) -> bool:
        """Cache cultural insights for destination."""
        if not await db_rate_limiter.acquire("cache"):
            logger.warning("Rate limited: set_cultural_cache")
            return False

        try:
            expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)
            cache_data = {
                "destination": destination,
                "destination_normalized": destination.lower(),
                "cultural_data": data.get("cultural_data", {}),
                "style_data": data.get("style_data", {}),
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(UTC).isoformat(),
                "api_source": "qloo",  # Add API source for unique constraint
            }
            result = await self.upsert(cache_data, ["destination", "api_source"])
            return result is not None
        except Exception as e:
            logger.error(f"Cultural cache set error: {e}")
            return False


class CurrencyCacheService(SupabaseBaseService[CacheEntry]):
    """Service for currency cache operations."""

    def __init__(self):
        super().__init__("currency_rates_cache")

    def _parse_record(self, record: dict[str, Any]) -> CacheEntry:
        """Parse a currency cache record."""
        return CacheEntry.from_dict(
            {
                "data": record.get("rates_data", {}),
                "expires_at": record.get("expires_at"),
                "created_at": record.get("created_at"),
            }
        )

    async def get_cache(self, base_currency: str) -> dict[str, Any] | None:
        """Get cached currency rates."""
        if not await db_rate_limiter.acquire("cache"):
            logger.warning("Rate limited: get_currency_cache")
            return None

        try:
            records = await self.get_by_field("base_currency", base_currency)
            if not records:
                return None

            # Find the most recent non-expired record
            for record in sorted(records, key=lambda r: r.created_at, reverse=True):
                if not record.is_expired():
                    return record.data

            return None
        except Exception as e:
            logger.error(f"Currency cache get error: {e}")
            return None

    async def set_cache(self, base_currency: str, data: dict[str, Any], ttl_hours: int = 1) -> bool:
        """Cache currency rates."""
        if not await db_rate_limiter.acquire("cache"):
            logger.warning("Rate limited: set_currency_cache")
            return False

        try:
            expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)
            cache_data = {
                "base_currency": base_currency,
                "rates_data": data,
                "expires_at": expires_at.isoformat(),
                "api_source": "exchangerate-api",
            }
            result = await self.upsert(cache_data, ["base_currency", "api_source"])
            return result is not None
        except Exception as e:
            logger.error(f"Currency cache set error: {e}")
            return False


class EnhancedSupabaseCacheService:
    """Enhanced cache service using the base service pattern."""

    def __init__(self):
        """Initialize the enhanced cache service."""
        self.weather_service = WeatherCacheService()
        self.cultural_service = CulturalCacheService()
        self.currency_service = CurrencyCacheService()

    async def get_weather_cache(self, destination: str) -> dict[str, Any] | None:
        """Get cached weather data for destination."""
        return await self.weather_service.get_cache(destination)

    async def set_weather_cache(
        self, destination: str, data: dict[str, Any], ttl_hours: int = 1
    ) -> bool:
        """Cache weather data for destination."""
        return await self.weather_service.set_cache(destination, data, ttl_hours)

    async def get_cultural_cache(
        self, destination: str, context: str = "leisure"
    ) -> dict[str, Any] | None:
        """Get cached cultural insights for destination."""
        return await self.cultural_service.get_cache(destination, context)

    async def set_cultural_cache(
        self, destination: str, context: str, data: dict[str, Any], ttl_hours: int = 24
    ) -> bool:
        """Cache cultural insights for destination."""
        return await self.cultural_service.set_cache(destination, data, ttl_hours, context)

    async def get_currency_cache(self, base_currency: str) -> dict[str, Any] | None:
        """Get cached currency rates."""
        return await self.currency_service.get_cache(base_currency)

    async def set_currency_cache(
        self, base_currency: str, data: dict[str, Any], ttl_hours: int = 1
    ) -> bool:
        """Cache currency rates."""
        return await self.currency_service.set_cache(base_currency, data, ttl_hours)


# Singleton instance for the enhanced service
enhanced_supabase_cache = EnhancedSupabaseCacheService()
