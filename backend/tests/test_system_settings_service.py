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

"""Tests for SystemSettingsService."""

from unittest.mock import MagicMock, patch

import pytest
from app.services.system_settings_service import SystemSettingsService


@pytest.fixture
def service() -> SystemSettingsService:
    return SystemSettingsService()


def _make_query_response(data):
    resp = MagicMock()
    resp.data = data
    return resp


class TestGetAllSettings:
    @pytest.mark.asyncio
    async def test_rate_limited_returns_empty(self, service):
        with patch(
            "app.services.system_settings_service.db_rate_limiter.acquire", return_value=False
        ):
            result = await service.get_all_settings()
            assert result == {}

    @pytest.mark.asyncio
    async def test_success_full_and_public_filter(self, service):
        client = MagicMock()
        service.client = client
        query = MagicMock()
        client.table.return_value = query
        query.select.return_value = query
        # Two records, one private
        data = [
            {"setting_key": "a", "setting_value": 1, "is_public": True},
            {"setting_key": "b", "setting_value": 2, "is_public": False},
        ]
        with patch("asyncio.to_thread", return_value=_make_query_response(data)):
            # all
            all_settings = await service.get_all_settings(public_only=False)
            assert all_settings == {"a": 1, "b": 2}
            # public only
            public_settings = await service.get_all_settings(public_only=True)
            assert public_settings == {"a": 1}

    @pytest.mark.asyncio
    async def test_no_data_returns_empty(self, service):
        client = MagicMock()
        service.client = client
        query = MagicMock()
        client.table.return_value = query
        query.select.return_value = query
        with patch("asyncio.to_thread", return_value=_make_query_response([])):
            result = await service.get_all_settings()
            assert result == {}

    @pytest.mark.asyncio
    async def test_exception_returns_empty(self, service):
        client = MagicMock()
        service.client = client
        query = MagicMock()
        client.table.return_value = query
        query.select.return_value = query
        with patch("asyncio.to_thread", side_effect=Exception("db error")):
            result = await service.get_all_settings()
            assert result == {}


class TestGetSetting:
    @pytest.mark.asyncio
    async def test_rate_limited_returns_none(self, service):
        with patch(
            "app.services.system_settings_service.db_rate_limiter.acquire", return_value=False
        ):
            result = await service.get_setting("foo")
            assert result is None

    @pytest.mark.asyncio
    async def test_success_found_and_not_found(self, service):
        client = MagicMock()
        service.client = client
        query = MagicMock()
        eq = MagicMock()
        client.table.return_value = query
        query.select.return_value = query
        query.eq.return_value = eq
        eq.execute.return_value = _make_query_response([{"setting_value": "x"}])
        with patch("asyncio.to_thread", side_effect=lambda func: func()):
            assert await service.get_setting("k") == "x"
            # not found
            eq.execute.return_value = _make_query_response([])
            assert await service.get_setting("k") is None

    @pytest.mark.asyncio
    async def test_exception_returns_none(self, service):
        client = MagicMock()
        service.client = client
        query = MagicMock()
        client.table.return_value = query
        query.select.return_value = query
        query.eq.return_value = MagicMock()
        with patch("asyncio.to_thread", side_effect=Exception("db error")):
            assert await service.get_setting("k") is None


class TestGetPublicSettings:
    @pytest.mark.asyncio
    async def test_delegates_to_get_all_settings(self, service):
        with patch.object(service, "get_all_settings", return_value={"k": "v"}) as mock:
            result = await service.get_public_settings()
            assert result == {"k": "v"}
            mock.assert_called_once_with(public_only=True)


class TestGetProfileSettings:
    @pytest.mark.asyncio
    async def test_profile_settings_collects_existing(self, service):
        with patch.object(service, "get_setting") as mock_get:
            mock_get.side_effect = [
                ["tops", "bottoms"],  # clothing_categories
                None,  # style_importance_levels missing
                ["USD", "EUR"],  # supported_currencies
                {"default": "5-4-3-2-1"},  # default_packing_methods
            ]
            result = await service.get_profile_settings()
            assert result == {
                "clothing_categories": ["tops", "bottoms"],
                "supported_currencies": ["USD", "EUR"],
                "default_packing_methods": {"default": "5-4-3-2-1"},
            }


class TestGetLimitsSettings:
    @pytest.mark.asyncio
    async def test_limits_free_paid_and_enterprise_derivation(self, service):
        with patch.object(service, "get_setting") as mock_get:
            # Return strings to test numeric coercion path
            key_to_value = {
                "max_style_preferences_per_user_free": "1",
                "max_conversations_per_user_free": "2",
                "max_bookmarks_per_user_free": "3",
                "api_rate_limit_per_user_per_hour_free": "4",
                "max_style_preferences_per_user_paid": "10",
                "max_conversations_per_user_paid": "20",
                "max_bookmarks_per_user_paid": "30",
                "api_rate_limit_per_user_per_hour_paid": "40",
                # enterprise explicit only for one key
                "max_style_preferences_per_user_enterprise": "100",
            }

            def side_effect(key):
                return key_to_value.get(key)

            mock_get.side_effect = side_effect

            result = await service.get_limits_settings(include_enterprise=True)
            assert result["free"]["max_style_preferences_per_user"] == "1"
            assert result["paid"]["max_style_preferences_per_user"] == "10"
            # Enterprise explicit uses value
            assert result["enterprise"]["max_style_preferences_per_user"] == "100"
            # Derived enterprise = 3x paid (coerced to int)
            assert result["enterprise"]["max_conversations_per_user"] == 60
            assert result["enterprise"]["max_bookmarks_per_user"] == 90
            assert result["enterprise"]["api_rate_limit_per_user_per_hour"] == 120

    @pytest.mark.asyncio
    async def test_limits_without_enterprise(self, service):
        with patch.object(service, "get_setting", return_value=None):
            result = await service.get_limits_settings(include_enterprise=False)
            assert result == {"free": {}, "paid": {}}

    @pytest.mark.asyncio
    async def test_limits_derivation_non_numeric_fallback(self, service):
        with patch.object(service, "get_setting") as mock_get:
            key_to_value = {
                "max_style_preferences_per_user_paid": "not-a-number",
            }

            def side_effect(key):
                return key_to_value.get(key)

            mock_get.side_effect = side_effect

            result = await service.get_limits_settings(include_enterprise=True)
            assert result["enterprise"]["max_style_preferences_per_user"] == "not-a-number"


class TestGetFeatureAndCacheAndSubscriptionSettings:
    @pytest.mark.asyncio
    async def test_get_feature_flags(self, service):
        with patch.object(service, "get_setting") as mock_get:
            key_to_value = {
                "style_recommendation_enabled": True,
                "feedback_collection_enabled": False,
                "analytics_collection_enabled": True,
            }
            mock_get.side_effect = lambda k: key_to_value.get(k)
            result = await service.get_feature_flags()
            assert result == key_to_value

    @pytest.mark.asyncio
    async def test_get_cache_settings(self, service):
        with patch.object(service, "get_setting") as mock_get:
            key_to_value = {
                "weather_cache_duration_hours": 1,
                "currency_cache_duration_hours": 2,
                "cultural_cache_duration_hours": 3,
                "chat_session_timeout_hours": 4,
            }
            mock_get.side_effect = lambda k: key_to_value.get(k)
            result = await service.get_cache_settings()
            assert result == key_to_value

    @pytest.mark.asyncio
    async def test_get_subscription_settings(self, service):
        with patch.object(service, "get_setting") as mock_get:
            key_to_value = {
                "subscription_tiers": ["free", "paid"],
                "subscription_features": {"paid": ["x"]},
            }
            mock_get.side_effect = lambda k: key_to_value.get(k)
            result = await service.get_subscription_settings()
            assert result == key_to_value
