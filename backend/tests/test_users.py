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
Tests for UserOperations class.
"""

from unittest.mock import MagicMock, patch

import pytest
from app.services.database.users import UserOperations


class TestUserOperations:
    """Test UserOperations class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Supabase client."""
        return MagicMock()

    @pytest.fixture
    def user_operations(self, mock_client):
        """Create a UserOperations instance with mock client."""
        return UserOperations(mock_client)

    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, user_operations, mock_client):
        """Test successful user profile retrieval."""
        mock_response = MagicMock()
        mock_response.data = [{"user_id": "test-user", "name": "Test User"}]

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await user_operations.get_user_profile("test-user")

                assert result == {"user_id": "test-user", "name": "Test User"}

    @pytest.mark.asyncio
    async def test_get_user_profile_invalid_user_id(self, user_operations):
        """Test get_user_profile with invalid user ID."""
        result = await user_operations.get_user_profile("invalid-id")
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_user_profile_rate_limited(self, user_operations):
        """Test get_user_profile when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await user_operations.get_user_profile("test-user")
            assert result == {}

    @pytest.mark.asyncio
    async def test_get_user_profile_no_data(self, user_operations, mock_client):
        """Test get_user_profile when no data is returned."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await user_operations.get_user_profile("test-user")
                assert result == {}

    @pytest.mark.asyncio
    async def test_get_user_profile_exception(self, user_operations, mock_client):
        """Test get_user_profile when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await user_operations.get_user_profile("test-user")
                assert result == {}

    @pytest.mark.asyncio
    async def test_save_user_profile_success(self, user_operations, mock_client):
        """Test save_user_profile success."""
        # Mock the table operations
        table_mock = MagicMock()

        # Mock users table check - user exists
        users_response = MagicMock()
        users_response.data = [{"id": "test-user"}]

        # Mock profiles table update
        profiles_response = MagicMock()
        profiles_response.data = [{"id": "test-user"}]

        # Mock user_preferences table operations
        prefs_select_response = MagicMock()
        prefs_select_response.data = []  # No existing preferences

        prefs_insert_response = MagicMock()
        prefs_insert_response.data = [{"user_id": "test-user"}]

        # Mock user_profile_view final query
        profile_view_response = MagicMock()
        profile_view_response.data = [{"id": "test-user", "name": "Updated User"}]

        # Configure table mock to return different responses based on table name
        def table_side_effect(table_name):
            if table_name == "users":
                return table_mock
            elif table_name == "profiles":
                return table_mock
            elif table_name == "user_preferences":
                return table_mock
            elif table_name == "user_profile_view":
                return table_mock
            else:
                return table_mock

        mock_client.table.side_effect = table_side_effect

        # Configure the table mock methods
        table_mock.select.return_value.eq.return_value.execute.return_value = users_response
        table_mock.update.return_value.eq.return_value.execute.return_value = profiles_response
        table_mock.insert.return_value.execute.return_value = prefs_insert_response

        # For the final profile view query
        table_mock.select.return_value.eq.return_value.execute.return_value = profile_view_response

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            result = await user_operations.save_user_profile("test-user", {"name": "Updated User"})

            assert result == {"id": "test-user", "name": "Updated User"}

    @pytest.mark.asyncio
    async def test_save_user_profile_invalid_user_id(self, user_operations):
        """Test save_user_profile with invalid user ID."""
        result = await user_operations.save_user_profile("invalid-id", {"name": "User"})
        assert result is None

    @pytest.mark.asyncio
    async def test_save_user_profile_invalid_profile_data(self, user_operations):
        """Test save_user_profile with invalid profile data."""
        result = await user_operations.save_user_profile("test-user", "not a dict")
        assert result is None

    @pytest.mark.asyncio
    async def test_save_user_profile_rate_limited(self, user_operations):
        """Test save_user_profile when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await user_operations.save_user_profile("test-user", {"name": "User"})
            assert result is None

    @pytest.mark.asyncio
    async def test_save_user_profile_user_not_found(self, user_operations, mock_client):
        """Test save_user_profile when user doesn't exist."""
        user_response = MagicMock()
        user_response.data = []

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = user_response

                result = await user_operations.save_user_profile("test-user", {"name": "User"})
                assert result is None

    @pytest.mark.asyncio
    async def test_save_user_profile_create_preferences(self, user_operations, mock_client):
        """Test save_user_profile when creating new preferences via view."""
        # Mock the table operations
        table_mock = MagicMock()

        # Mock users table check - user exists
        users_response = MagicMock()
        users_response.data = [{"id": "test-user"}]

        # Mock profiles table update
        profiles_response = MagicMock()
        profiles_response.data = [{"id": "test-user"}]

        # Mock user_preferences table operations (no existing preferences, so insert)
        prefs_select_response = MagicMock()
        prefs_select_response.data = []  # No existing preferences

        prefs_insert_response = MagicMock()
        prefs_insert_response.data = [{"user_id": "test-user"}]

        # Mock user_profile_view final query
        profile_view_response = MagicMock()
        profile_view_response.data = [{"id": "test-user", "name": "Updated User"}]

        # Configure table mock to return different responses based on table name
        def table_side_effect(table_name):
            if table_name == "users":
                return table_mock
            elif table_name == "profiles":
                return table_mock
            elif table_name == "user_preferences":
                return table_mock
            elif table_name == "user_profile_view":
                return table_mock
            else:
                return table_mock

        mock_client.table.side_effect = table_side_effect

        # Configure the table mock methods
        table_mock.select.return_value.eq.return_value.execute.return_value = users_response
        table_mock.update.return_value.eq.return_value.execute.return_value = profiles_response
        table_mock.insert.return_value.execute.return_value = prefs_insert_response

        # For the final profile view query
        table_mock.select.return_value.eq.return_value.execute.return_value = profile_view_response

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            result = await user_operations.save_user_profile("test-user", {"name": "Updated User"})

            assert result == {"id": "test-user", "name": "Updated User"}

    @pytest.mark.asyncio
    async def test_save_user_profile_update_failed(self, user_operations, mock_client):
        """Test save_user_profile when update fails."""
        user_response = MagicMock()
        user_response.data = [{"id": "test-user"}]

        update_response = MagicMock()
        update_response.data = []

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = [user_response, update_response]

                result = await user_operations.save_user_profile(
                    "test-user", {"name": "Updated User"}
                )
                assert result is None

    @pytest.mark.asyncio
    async def test_save_user_profile_exception(self, user_operations, mock_client):
        """Test save_user_profile when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await user_operations.save_user_profile("test-user", {"name": "User"})
                assert result is None

    @pytest.mark.asyncio
    async def test_update_user_preferences_success_existing(self, user_operations, mock_client):
        """Test successful user preferences update with existing preferences."""
        existing_response = MagicMock()
        existing_response.data = [{"id": "pref-1"}]

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = [existing_response, None]

                result = await user_operations.update_user_preferences(
                    "test-user", {"theme": "dark"}
                )
                assert result is True

    @pytest.mark.asyncio
    async def test_update_user_preferences_success_new(self, user_operations, mock_client):
        """Test successful user preferences update with new preferences."""
        existing_response = MagicMock()
        existing_response.data = []

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = [existing_response, None]

                result = await user_operations.update_user_preferences(
                    "test-user", {"theme": "dark"}
                )
                assert result is True

    @pytest.mark.asyncio
    async def test_update_user_preferences_invalid_user_id(self, user_operations):
        """Test update_user_preferences with invalid user ID."""
        result = await user_operations.update_user_preferences("invalid-id", {"theme": "dark"})
        assert result is False

    @pytest.mark.asyncio
    async def test_update_user_preferences_rate_limited(self, user_operations):
        """Test update_user_preferences when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await user_operations.update_user_preferences("test-user", {"theme": "dark"})
            assert result is False

    @pytest.mark.asyncio
    async def test_update_user_preferences_exception(self, user_operations, mock_client):
        """Test update_user_preferences when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await user_operations.update_user_preferences(
                    "test-user", {"theme": "dark"}
                )
                assert result is False

    @pytest.mark.asyncio
    async def test_save_recommendation_feedback_success(self, user_operations, mock_client):
        """Test successful recommendation feedback save."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = None

                result = await user_operations.save_recommendation_feedback(
                    "test-user", "conv-1", "msg-1", "positive", "Great!", "AI response"
                )
                assert result is True

    @pytest.mark.asyncio
    async def test_save_recommendation_feedback_invalid_user_id(self, user_operations):
        """Test save_recommendation_feedback with invalid user ID."""
        result = await user_operations.save_recommendation_feedback(
            "invalid-id", "conv-1", "msg-1", "positive"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_save_recommendation_feedback_rate_limited(self, user_operations):
        """Test save_recommendation_feedback when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await user_operations.save_recommendation_feedback(
                "test-user", "conv-1", "msg-1", "positive"
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_save_recommendation_feedback_exception(self, user_operations, mock_client):
        """Test save_recommendation_feedback when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await user_operations.save_recommendation_feedback(
                    "test-user", "conv-1", "msg-1", "positive"
                )
                assert result is False

    @pytest.mark.asyncio
    async def test_save_destination_success_new(self, user_operations, mock_client):
        """Test successful destination save for new destination."""
        existing_response = MagicMock()
        existing_response.data = []

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = [existing_response, None]

                result = await user_operations.save_destination(
                    "test-user", "Paris", {"country": "France"}
                )
                assert result is True

    @pytest.mark.asyncio
    async def test_save_destination_success_existing(self, user_operations, mock_client):
        """Test successful destination save for existing destination."""
        existing_response = MagicMock()
        existing_response.data = [{"id": "dest-1"}]

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = [existing_response, None]

                result = await user_operations.save_destination(
                    "test-user", "Paris", {"country": "France"}
                )
                assert result is True

    @pytest.mark.asyncio
    async def test_save_destination_invalid_user_id(self, user_operations):
        """Test save_destination with invalid user ID."""
        result = await user_operations.save_destination(
            "invalid-id", "Paris", {"country": "France"}
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_save_destination_rate_limited(self, user_operations):
        """Test save_destination when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await user_operations.save_destination(
                "test-user", "Paris", {"country": "France"}
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_save_destination_exception(self, user_operations, mock_client):
        """Test save_destination when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await user_operations.save_destination(
                    "test-user", "Paris", {"country": "France"}
                )
                assert result is False

    @pytest.mark.asyncio
    async def test_update_user_profile_picture_url_success(self, user_operations, mock_client):
        """Test successful profile picture URL update."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = None

                result = await user_operations.update_user_profile_picture_url(
                    "test-user", "https://example.com/photo.jpg"
                )
                assert result is True

    @pytest.mark.asyncio
    async def test_update_user_profile_picture_url_invalid_user_id(self, user_operations):
        """Test update_user_profile_picture_url with invalid user ID."""
        result = await user_operations.update_user_profile_picture_url(
            "invalid-id", "https://example.com/photo.jpg"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_update_user_profile_picture_url_rate_limited(self, user_operations):
        """Test update_user_profile_picture_url when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await user_operations.update_user_profile_picture_url(
                "test-user", "https://example.com/photo.jpg"
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_update_user_profile_picture_url_exception(self, user_operations, mock_client):
        """Test update_user_profile_picture_url when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await user_operations.update_user_profile_picture_url(
                    "test-user", "https://example.com/photo.jpg"
                )
                assert result is False

    def test_user_operations_init(self, mock_client):
        """Test UserOperations initialization."""
        user_ops = UserOperations(mock_client)
        assert user_ops.client == mock_client
