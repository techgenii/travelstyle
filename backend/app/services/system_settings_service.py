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
import json
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
        limits_settings = {"free": {}, "paid": {}, "premium": {}}

        # Get the unified tier definitions
        free_tier = await self.get_setting("subscription_tier_free")
        premium_tier = await self.get_setting("subscription_tier_premium")
        enterprise_tier = (
            await self.get_setting("subscription_tier_enterprise") if include_enterprise else None
        )

        # Process free tier limits
        if free_tier:
            if isinstance(free_tier, str):
                try:
                    free_tier = json.loads(free_tier)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse subscription_tier_free JSON")
                    free_tier = {}

            if isinstance(free_tier, dict) and "limits" in free_tier:
                limits = free_tier["limits"]
                # Convert keys to match the expected format
                for key, value in limits.items():
                    if key == "style_preferences":
                        limits_settings["free"]["max_style_preferences_per_user"] = value
                    elif key == "conversations":
                        limits_settings["free"]["max_conversations_per_user"] = value
                    elif key == "bookmarks":
                        limits_settings["free"]["max_bookmarks_per_user"] = value
                    elif key == "api_rate_limit_per_hour":
                        limits_settings["free"]["api_rate_limit_per_user_per_hour"] = value

        # Process premium tier limits (paid tier)
        if premium_tier:
            if isinstance(premium_tier, str):
                try:
                    premium_tier = json.loads(premium_tier)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse subscription_tier_premium JSON")
                    premium_tier = {}

            if isinstance(premium_tier, dict) and "limits" in premium_tier:
                limits = premium_tier["limits"]
                # Convert keys to match the expected format
                for key, value in limits.items():
                    if key == "style_preferences":
                        limits_settings["paid"]["max_style_preferences_per_user"] = value
                        limits_settings["premium"]["max_style_preferences_per_user"] = value
                    elif key == "conversations":
                        limits_settings["paid"]["max_conversations_per_user"] = value
                        limits_settings["premium"]["max_conversations_per_user"] = value
                    elif key == "bookmarks":
                        limits_settings["paid"]["max_bookmarks_per_user"] = value
                        limits_settings["premium"]["max_bookmarks_per_user"] = value
                    elif key == "api_rate_limit_per_hour":
                        limits_settings["paid"]["api_rate_limit_per_user_per_hour"] = value
                        limits_settings["premium"]["api_rate_limit_per_user_per_hour"] = value

        if include_enterprise:
            limits_settings["enterprise"] = {}

            # Process enterprise tier limits
            if enterprise_tier:
                if isinstance(enterprise_tier, str):
                    try:
                        enterprise_tier = json.loads(enterprise_tier)
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse subscription_tier_enterprise JSON")
                        enterprise_tier = {}

                if isinstance(enterprise_tier, dict) and "limits" in enterprise_tier:
                    limits = enterprise_tier["limits"]
                    # Convert keys to match the expected format
                    for key, value in limits.items():
                        if key == "style_preferences":
                            limits_settings["enterprise"]["max_style_preferences_per_user"] = value
                        elif key == "conversations":
                            limits_settings["enterprise"]["max_conversations_per_user"] = value
                        elif key == "bookmarks":
                            limits_settings["enterprise"]["max_bookmarks_per_user"] = value
                        elif key == "api_rate_limit_per_hour":
                            limits_settings["enterprise"]["api_rate_limit_per_user_per_hour"] = (
                                value
                            )

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
            Dictionary with subscription tier information
        """
        subscription_settings = {}

        # Get subscription tier constants
        subscription_tiers = await self.get_setting("subscription_tiers")
        subscription_tier_order = await self.get_setting("subscription_tier_order")

        # Get the unified tier definitions
        free_tier = await self.get_setting("subscription_tier_free")
        premium_tier = await self.get_setting("subscription_tier_premium")
        enterprise_tier = await self.get_setting("subscription_tier_enterprise")

        # Process tier definitions
        tiers = {}
        for tier_key, tier_data in [
            ("free", free_tier),
            ("premium", premium_tier),
            ("enterprise", enterprise_tier),
        ]:
            if tier_data:
                if isinstance(tier_data, str):
                    try:
                        tier_data = json.loads(tier_data)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse subscription_tier_{tier_key} JSON")
                        continue

                if isinstance(tier_data, dict):
                    tiers[tier_key] = tier_data

        subscription_settings["tiers"] = tiers
        subscription_settings["tier_list"] = subscription_tiers
        subscription_settings["tier_order"] = subscription_tier_order

        return subscription_settings


# Create a singleton instance
system_settings_service = SystemSettingsService()
