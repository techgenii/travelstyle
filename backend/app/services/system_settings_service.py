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
System settings service for TravelStyle AI application.
Handles access to system configuration settings stored in the database.
"""

import asyncio
import logging
from typing import Any

from app.services.database.constants import DatabaseTables
from app.services.database_helpers import db_helpers
from app.services.rate_limiter import db_rate_limiter

logger = logging.getLogger(__name__)


class SystemSettingsService:
    """Service for managing system settings."""

    def __init__(self):
        """Initialize the system settings service."""
        self.client = db_helpers.client

    async def get_all_settings(self, public_only: bool = False) -> dict[str, Any]:
        """
        Get all system settings.

        Args:
            public_only: If True, only return public settings

        Returns:
            Dictionary of setting_key -> setting_value pairs
        """
        if not await db_rate_limiter.acquire("read"):
            logger.warning("Rate limited: get_all_settings")
            return {}

        try:
            query = self.client.table(DatabaseTables.SYSTEM_SETTINGS).select("*")

            response = await asyncio.to_thread(lambda: query.execute())

            if not response.data:
                return {}

            # Convert to key-value pairs
            settings = {}
            for setting in response.data:
                if public_only and not setting.get("is_public", False):
                    continue
                settings[setting["setting_key"]] = setting["setting_value"]

            return settings

        except Exception as e:
            logger.error(f"Error retrieving system settings: {e}")
            return {}

    async def get_setting(self, setting_key: str) -> Any | None:
        """
        Get a specific system setting by key.

        Args:
            setting_key: The setting key to retrieve

        Returns:
            The setting value or None if not found
        """
        if not await db_rate_limiter.acquire("read"):
            logger.warning("Rate limited: get_setting")
            return None

        try:
            response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.SYSTEM_SETTINGS)
                    .select("setting_value")
                    .eq("setting_key", setting_key)
                    .execute()
                )
            )

            if response.data and len(response.data) > 0:
                return response.data[0]["setting_value"]

            return None

        except Exception as e:
            logger.error(f"Error retrieving setting {setting_key}: {e}")
            return None

    async def get_public_settings(self) -> dict[str, Any]:
        """
        Get all public system settings.

        Returns:
            Dictionary of public setting_key -> setting_value pairs
        """
        return await self.get_all_settings(public_only=True)

    async def get_profile_settings(self) -> dict[str, Any]:
        """
        Get settings relevant for user profile functionality.

        Returns:
            Dictionary of profile-related settings
        """
        profile_settings = {}

        # Get specific settings that are relevant for profiles
        profile_setting_keys = [
            "clothing_categories",
            "style_importance_levels",
            "supported_currencies",
            "default_packing_methods",
        ]

        for key in profile_setting_keys:
            value = await self.get_setting(key)
            if value is not None:
                profile_settings[key] = value

        return profile_settings

    async def get_limits_settings(self, include_enterprise: bool = False) -> dict[str, Any]:
        """
        Get user limit settings for free and paid tiers. Optionally include enterprise.

        Returns:
            Dictionary with free and paid limit settings. If include_enterprise is True,
            the returned dict also contains an "enterprise" key.
        """
        limits_settings = {"free": {}, "paid": {}}

        # Free tier limit settings
        free_limit_keys = [
            "max_style_preferences_per_user_free",
            "max_conversations_per_user_free",
            "max_bookmarks_per_user_free",
            "api_rate_limit_per_user_per_hour_free",
        ]

        # Paid tier limit settings
        paid_limit_keys = [
            "max_style_preferences_per_user_paid",
            "max_conversations_per_user_paid",
            "max_bookmarks_per_user_paid",
            "api_rate_limit_per_user_per_hour_paid",
        ]

        # Enterprise tier limit settings (explicit). If not present, will be derived from paid.
        enterprise_limit_keys = [
            "max_style_preferences_per_user_enterprise",
            "max_conversations_per_user_enterprise",
            "max_bookmarks_per_user_enterprise",
            "api_rate_limit_per_user_per_hour_enterprise",
        ]

        # Get free limits
        for key in free_limit_keys:
            value = await self.get_setting(key)
            if value is not None:
                # Convert key from "max_style_preferences_per_user_free" to "max_style_preferences_per_user"
                clean_key = key.replace("_free", "")
                limits_settings["free"][clean_key] = value

        # Get paid limits
        for key in paid_limit_keys:
            value = await self.get_setting(key)
            if value is not None:
                # Convert key from "max_style_preferences_per_user_paid" to "max_style_preferences_per_user"
                clean_key = key.replace("_paid", "")
                limits_settings["paid"][clean_key] = value

        if include_enterprise:
            limits_settings["enterprise"] = {}
            # Get enterprise limits (explicit values first)
            for key in enterprise_limit_keys:
                value = await self.get_setting(key)
                if value is not None:
                    clean_key = key.replace("_enterprise", "")
                    limits_settings["enterprise"][clean_key] = value

            # Derive missing enterprise values as 3x paid
            for clean_key, paid_value in limits_settings["paid"].items():
                if clean_key not in limits_settings["enterprise"]:
                    try:
                        # Support numeric JSON and strings
                        numeric_value = (
                            int(paid_value) if isinstance(paid_value, str) else int(paid_value)
                        )
                        limits_settings["enterprise"][clean_key] = numeric_value * 3
                    except (ValueError, TypeError):
                        # If non-numeric, fall back to paid value
                        limits_settings["enterprise"][clean_key] = paid_value

        return limits_settings

    async def get_feature_flags(self) -> dict[str, Any]:
        """
        Get feature flag settings.

        Returns:
            Dictionary of feature flag settings
        """
        feature_settings = {}

        # Get specific feature flag settings
        feature_setting_keys = [
            "style_recommendation_enabled",
            "feedback_collection_enabled",
            "analytics_collection_enabled",
        ]

        for key in feature_setting_keys:
            value = await self.get_setting(key)
            if value is not None:
                feature_settings[key] = value

        return feature_settings

    async def get_cache_settings(self) -> dict[str, Any]:
        """
        Get cache duration settings.

        Returns:
            Dictionary of cache duration settings
        """
        cache_settings = {}

        # Get specific cache settings
        cache_setting_keys = [
            "weather_cache_duration_hours",
            "currency_cache_duration_hours",
            "cultural_cache_duration_hours",
            "chat_session_timeout_hours",
        ]

        for key in cache_setting_keys:
            value = await self.get_setting(key)
            if value is not None:
                cache_settings[key] = value

        return cache_settings

    async def get_subscription_settings(self) -> dict[str, Any]:
        """
        Get subscription tier settings and features.

        Returns:
            Dictionary with subscription tiers and features
        """
        subscription_settings = {}

        # Get subscription tier settings
        subscription_setting_keys = ["subscription_tiers", "subscription_features"]

        for key in subscription_setting_keys:
            value = await self.get_setting(key)
            if value is not None:
                subscription_settings[key] = value

        return subscription_settings


# Create a singleton instance
system_settings_service = SystemSettingsService()
