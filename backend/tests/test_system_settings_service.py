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
Tests for the system settings service.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.system_settings_service import SystemSettingsService


class TestSystemSettingsService:
    """Test cases for SystemSettingsService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SystemSettingsService()
        self.mock_client = MagicMock()
        self.service.client = self.mock_client

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_get_all_settings_success(self, mock_rate_limiter):
        """Test successful retrieval of all settings."""
        # Mock rate limiter
        mock_rate_limiter.acquire = AsyncMock(return_value=True)

        # Mock database response
        mock_response = MagicMock()
        mock_response.data = [
            {
                "setting_key": "clothing_categories",
                "setting_value": ["aesthetic", "cultural_etiquette", "functional"],
                "is_public": True,
            },
            {"setting_key": "style_importance_levels", "setting_value": 5, "is_public": True},
        ]

        # Mock the query chain
        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.execute.return_value = mock_response
        self.mock_client.table.return_value = mock_query

        result = await self.service.get_all_settings()

        assert result == {
            "clothing_categories": ["aesthetic", "cultural_etiquette", "functional"],
            "style_importance_levels": 5,
        }

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_get_all_settings_public_only(self, mock_rate_limiter):
        """Test retrieval of public settings only."""
        # Mock rate limiter
        mock_rate_limiter.acquire = AsyncMock(return_value=True)

        # Mock database response
        mock_response = MagicMock()
        mock_response.data = [
            {
                "setting_key": "clothing_categories",
                "setting_value": ["aesthetic", "cultural_etiquette", "functional"],
                "is_public": True,
            },
            {
                "setting_key": "max_style_preferences_per_user",
                "setting_value": 50,
                "is_public": False,
            },
        ]

        # Mock the query chain
        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        self.mock_client.table.return_value = mock_query

        result = await self.service.get_all_settings(public_only=True)

        # Should only return the public setting
        assert result == {"clothing_categories": ["aesthetic", "cultural_etiquette", "functional"]}

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_get_setting_success(self, mock_rate_limiter):
        """Test successful retrieval of a specific setting."""
        # Mock rate limiter
        mock_rate_limiter.acquire = AsyncMock(return_value=True)

        # Mock database response
        mock_response = MagicMock()
        mock_response.data = [{"setting_value": ["aesthetic", "cultural_etiquette", "functional"]}]

        # Mock the query chain
        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        self.mock_client.table.return_value = mock_query

        result = await self.service.get_setting("clothing_categories")

        assert result == ["aesthetic", "cultural_etiquette", "functional"]

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_get_setting_not_found(self, mock_rate_limiter):
        """Test retrieval of a setting that doesn't exist."""
        # Mock rate limiter
        mock_rate_limiter.acquire = AsyncMock(return_value=True)

        # Mock database response with no data
        mock_response = MagicMock()
        mock_response.data = []

        # Mock the query chain
        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        self.mock_client.table.return_value = mock_query

        result = await self.service.get_setting("nonexistent_setting")

        assert result is None

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_get_profile_settings(self, mock_rate_limiter):
        """Test retrieval of profile-related settings."""
        # Mock rate limiter
        mock_rate_limiter.acquire.return_value = True

        # Mock the get_setting method
        with patch.object(self.service, "get_setting") as mock_get_setting:
            mock_get_setting.side_effect = lambda key: {
                "clothing_categories": ["aesthetic", "cultural_etiquette", "functional"],
                "style_importance_levels": 5,
                "supported_currencies": ["USD", "EUR", "GBP"],
                "default_packing_methods": [{"name": "5-4-3-2-1 Method"}],
            }.get(key)

            result = await self.service.get_profile_settings()

            assert result == {
                "clothing_categories": ["aesthetic", "cultural_etiquette", "functional"],
                "style_importance_levels": 5,
                "supported_currencies": ["USD", "EUR", "GBP"],
                "default_packing_methods": [{"name": "5-4-3-2-1 Method"}],
            }

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_get_limits_settings(self, mock_rate_limiter):
        """Test retrieval of limit settings."""
        # Mock rate limiter
        mock_rate_limiter.acquire.return_value = True

        # Mock the get_setting method
        with patch.object(self.service, "get_setting") as mock_get_setting:
            mock_get_setting.side_effect = lambda key: {
                "max_style_preferences_per_user_free": 10,
                "max_conversations_per_user_free": 20,
                "max_bookmarks_per_user_free": 10,
                "api_rate_limit_per_user_per_hour_free": 50,
                "max_style_preferences_per_user_paid": 50,
                "max_conversations_per_user_paid": 100,
                "max_bookmarks_per_user_paid": 50,
                "api_rate_limit_per_user_per_hour_paid": 100,
            }.get(key)

            result = await self.service.get_limits_settings()

            assert result == {
                "free": {
                    "max_style_preferences_per_user": 10,
                    "max_conversations_per_user": 20,
                    "max_bookmarks_per_user": 10,
                    "api_rate_limit_per_user_per_hour": 50,
                },
                "paid": {
                    "max_style_preferences_per_user": 50,
                    "max_conversations_per_user": 100,
                    "max_bookmarks_per_user": 50,
                    "api_rate_limit_per_user_per_hour": 100,
                },
            }

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_get_feature_flags(self, mock_rate_limiter):
        """Test retrieval of feature flag settings."""
        # Mock rate limiter
        mock_rate_limiter.acquire.return_value = True

        # Mock the get_setting method
        with patch.object(self.service, "get_setting") as mock_get_setting:
            mock_get_setting.side_effect = lambda key: {
                "style_recommendation_enabled": True,
                "feedback_collection_enabled": True,
                "analytics_collection_enabled": True,
            }.get(key)

            result = await self.service.get_feature_flags()

            assert result == {
                "style_recommendation_enabled": True,
                "feedback_collection_enabled": True,
                "analytics_collection_enabled": True,
            }

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_rate_limited(self, mock_rate_limiter):
        """Test behavior when rate limited."""
        # Mock rate limiter to return False (rate limited)
        mock_rate_limiter.acquire = AsyncMock(return_value=False)

        result = await self.service.get_all_settings()

        assert result == {}

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_get_subscription_settings(self, mock_rate_limiter):
        """Test retrieval of subscription settings."""
        # Mock rate limiter
        mock_rate_limiter.acquire.return_value = True

        # Mock the get_setting method
        with patch.object(self.service, "get_setting") as mock_get_setting:
            mock_get_setting.side_effect = lambda key: {
                "subscription_tiers": ["free", "premium", "enterprise"],
                "subscription_features": {
                    "free": {"style_preferences": True, "conversations": True},
                    "premium": {
                        "style_preferences": True,
                        "conversations": True,
                        "priority_support": True,
                    },
                    "enterprise": {
                        "style_preferences": True,
                        "conversations": True,
                        "api_access": True,
                    },
                },
            }.get(key)

            result = await self.service.get_subscription_settings()

            assert result == {
                "subscription_tiers": ["free", "premium", "enterprise"],
                "subscription_features": {
                    "free": {"style_preferences": True, "conversations": True},
                    "premium": {
                        "style_preferences": True,
                        "conversations": True,
                        "priority_support": True,
                    },
                    "enterprise": {
                        "style_preferences": True,
                        "conversations": True,
                        "api_access": True,
                    },
                },
            }

    @patch("app.services.system_settings_service.db_rate_limiter")
    @pytest.mark.asyncio
    async def test_database_error(self, mock_rate_limiter):
        """Test behavior when database error occurs."""
        # Mock rate limiter
        mock_rate_limiter.acquire = AsyncMock(return_value=True)

        # Mock database to raise an exception
        self.mock_client.table.side_effect = Exception("Database error")

        result = await self.service.get_all_settings()

        assert result == {}
