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

"""Supabase cache service for TravelStyle AI:
Handles caching of weather, cultural, and currency data.
This service provides caching functionality for external
API responses to improve performance.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from supabase import Client, create_client

logger = logging.getLogger(__name__)


class SupabaseCacheService:
    """Service for caching data in Supabase tables for weather,
    cultural insights, and currency rates. Provides methods to store
    and retrieve cached data with TTL support.
    """

    def __init__(self):
        """Initialize the SupabaseCacheService with client connection."""
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    async def get_weather_cache(self, destination: str) -> dict[str, Any] | None:
        """Get cached weather data for destination.
        Args:
            destination: The destination location.
        Returns:
            Cached weather data or None if not found/expired.
        """
        try:
            response = (
                self.client.table("weather_cache")
                .select("*")
                .eq("destination", destination)
                .limit(1)
                .execute()
            )
            # response.data is a list of rows
            if response.data and len(response.data) > 0:
                cache_entry = response.data[0]
                expires_at = cache_entry.get("expires_at")
                if expires_at and not self._is_expired(expires_at):
                    return cache_entry.get("weather_data")
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Weather cache get error: %s", type(e).__name__)
            return None

    async def set_weather_cache(
        self, destination: str, data: dict[str, Any], ttl_hours: int = 1
    ) -> bool:
        """Cache weather data for destination.
        Args:
            destination: The destination location.
            data: Weather data to cache.
            ttl_hours: Time to live in hours (default: 1).
        Returns:
            True if successful, False otherwise.
        """
        try:
            expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)
            cache_data = {
                "destination": destination,
                "destination_normalized": destination.lower(),
                "weather_data": data,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(UTC).isoformat(),
            }
            self.client.table("weather_cache").upsert(cache_data).execute()
            return True
        except Exception as e:
            logger.error("Weather cache set error: %s", type(e).__name__)
            return False

    async def get_cultural_cache(
        self, destination: str, context: str = "leisure"
    ) -> dict[str, Any] | None:
        """Get cached cultural insights for destination.
        Args:
            destination: The destination location.
            context: The travel context (default: leisure).
        Returns:
            Cached cultural data or None if not found/expired.
        """
        try:
            response = (
                self.client.table("cultural_insights_cache")
                .select("*")
                .eq("destination", destination)
                .limit(1)
                .execute()
            )
            # response.data is a list of rows
            if response.data and len(response.data) > 0:
                cache_entry = response.data[0]
                expires_at = cache_entry.get("expires_at")
                if expires_at and not self._is_expired(expires_at):
                    # Return both cultural_data and style_data
                    return {
                        "cultural_data": cache_entry.get("cultural_data"),
                        "style_data": cache_entry.get("style_data"),
                    }
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Cultural cache get error: %s", type(e).__name__)
            return None

    async def set_cultural_cache(
        self, destination: str, context: str, data: dict[str, Any], ttl_hours: int = 24
    ) -> bool:
        """Cache cultural insights for destination.
        Args:
            destination: The destination location.
            context: The travel context.
            data: Cultural data to cache.
            ttl_hours: Time to live in hours (default: 24).
        Returns:
            True if successful, False otherwise.
        """
        try:
            expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)
            cache_data = {
                "destination": destination,
                "destination_normalized": destination.lower(),
                "cultural_data": data.get("cultural_data", {}),
                "style_data": data.get("style_data", {}),
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(UTC).isoformat(),
            }
            self.client.table("cultural_insights_cache").upsert(cache_data).execute()
            return True
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Cultural cache set error: %s", type(e).__name__)
            return False

    async def get_currency_cache(self, base_currency: str) -> dict[str, Any] | None:
        """Get cached currency rates.
        Args:
            base_currency: The base currency code.
        Returns:
            Cached currency data or None if not found/expired.
        """
        try:
            response = (
                self.client.table("currency_rates_cache")
                .select("*")
                .eq("base_currency", base_currency)
                .execute()
            )
            # response.data is a list of rows
            if response.data and len(response.data) > 0:
                cache_entry = response.data[0]
                expires_at = cache_entry.get("expires_at")

                # Check if cache is expired
                if expires_at and self._is_expired(expires_at):
                    return None

                # Return the rates_data field from the first row
                return cache_entry["rates_data"]
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Currency cache get error: %s - %s", type(e).__name__, str(e))
            return None

    async def set_currency_cache(
        self, base_currency: str, data: dict[str, Any], ttl_hours: int = 1
    ) -> bool:
        """Cache currency rates.
        Args:
            base_currency: The base currency code.
            data: Currency data to cache.
            ttl_hours: Time to live in hours (default: 1).
        Returns:
            True if successful, False otherwise.
        """
        try:
            expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)
            cache_data = {
                "base_currency": base_currency,
                "rates_data": data,  # Use correct column name
                "expires_at": expires_at.isoformat(),
                "api_source": "exchangerate-api",
                # created_at and updated_at are auto-set by the DB
            }
            self.client.table("currency_rates_cache").upsert(cache_data).execute()
            return True
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Currency cache set error: %s - %s", type(e).__name__, str(e))
            return False

    def _is_expired(self, expires_at: str) -> bool:
        """Check if cache entry is expired.
        Args:
            expires_at: ISO format timestamp string.
        Returns:
            True if expired, False otherwise.
        """
        try:
            expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            return datetime.now(UTC) > expiry
        except Exception:  # pylint: disable=broad-except
            return True


# Singleton instance
supabase_cache = SupabaseCacheService()
