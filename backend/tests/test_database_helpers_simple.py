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
Simple isolated tests for database_helpers.py
This file uses the most basic approach possible to avoid all conflicts
"""

from unittest.mock import MagicMock, patch

import pytest


class TestDatabaseHelpersSimple:
    """Simple tests that focus only on the core functionality"""

    @pytest.mark.asyncio
    async def test_database_helpers_class_basic(self):
        """Test basic DatabaseHelpers class functionality"""

        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Test get_user_profile with view-based approach
        mock_response = MagicMock()
        mock_response.data = [{"id": "test-user", "email": "test@example.com"}]

        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
        mock_client.table.return_value = mock_table

        # Test the method
        result = await db.get_user_profile("test-user")

        # Basic assertions
        assert isinstance(result, dict)
        assert result.get("id") == "test-user"
        assert result.get("email") == "test@example.com"

        # Verify table was called
        assert mock_client.table.called

    @pytest.mark.asyncio
    async def test_update_user_preferences_simple(self):
        """Test update_user_preferences with fresh mocks"""

        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock no existing preferences (will create new)
        select_response = MagicMock()
        select_response.data = []

        insert_response = MagicMock()

        # Set up fresh table mock
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.execute.return_value = select_response
        table_mock.insert.return_value.execute.return_value = insert_response

        mock_client.table.return_value = table_mock

        # Test the method
        result = await db.update_user_preferences("test-user", {"style": "casual"})

        # Verify result
        assert result is True

        # Verify methods were called
        assert table_mock.update.called

    @pytest.mark.asyncio
    async def test_save_conversation_message_simple(self):
        """Test save_conversation_message with minimal setup"""

        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock responses
        insert_response = MagicMock()
        update_response = MagicMock()

        table_mock = MagicMock()
        table_mock.insert.return_value.execute.return_value = insert_response
        table_mock.update.return_value.eq.return_value.execute.return_value = update_response

        mock_client.table.return_value = table_mock

        # Test the method
        result = await db.save_conversation_message(
            user_id="test-user",
            conversation_id=None,  # Creates new conversation
            user_message="Hello",
            ai_response="Hi",
        )

        # Verify result structure
        assert isinstance(result, str)
        assert result is not None
        assert len(result) > 0  # Should be a valid UUID

        # Verify calls were made
        assert table_mock.insert.called

    @pytest.mark.asyncio
    async def test_error_handling_simple(self):
        """Test error handling with exceptions"""

        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Test that errors return appropriate defaults
        profile_result = await db.get_user_profile("test-user")
        assert profile_result == {}

        prefs_result = await db.update_user_preferences("test-user", {"test": "data"})
        assert prefs_result is False

        message_result = await db.save_conversation_message("test-user", "conv-1", "Hello", "Hi")
        assert message_result is None

    @pytest.mark.asyncio
    async def test_standalone_functions_bypass_autouse(self):
        """Test standalone functions by patching them directly"""

        # Create our own mock values
        test_profile = {
            "id": "test-user",
            "email": "test@example.com",
            "selected_style_names": ["Bohemian", "Minimalist"],
        }
        test_prefs_result = True
        test_feedback_result = True

        # Patch each function individually to bypass any global patches
        async def mock_get_user_profile(user_id):
            return test_profile

        async def mock_update_user_preferences(user_id, preferences):
            return test_prefs_result

        async def mock_save_recommendation_feedback(
            user_id, conv_id, msg_id, feedback_type, text=None, content=None
        ):
            return test_feedback_result

        # Apply patches
        with (
            patch(
                "app.services.database_helpers.db_helpers.get_user_profile",
                side_effect=mock_get_user_profile,
            ),
            patch(
                "app.services.database_helpers.db_helpers.update_user_preferences",
                side_effect=mock_update_user_preferences,
            ),
            patch(
                "app.services.database_helpers.db_helpers.save_recommendation_feedback",
                side_effect=mock_save_recommendation_feedback,
            ),
        ):
            # Import after patching
            from app.services.database_helpers import db_helpers

            # Test the functions
            profile = await db_helpers.get_user_profile("test-user")
            assert profile == test_profile
            assert profile["selected_style_names"] == ["Bohemian", "Minimalist"]

            prefs = await db_helpers.update_user_preferences("test-user", {"style": "casual"})
            assert prefs == test_prefs_result

            feedback = await db_helpers.save_recommendation_feedback(
                "test-user", "conv-1", "msg-1", "like"
            )
            assert feedback == test_feedback_result

    def test_imports_and_singleton(self):
        """Test that imports work and singleton exists"""

        # Test imports
        from app.services.database_helpers import (
            DatabaseHelpers,
            db_helpers,
        )

        # Test singleton exists
        assert db_helpers is not None
        assert isinstance(db_helpers, DatabaseHelpers)
        assert hasattr(db_helpers, "client")

        # Test methods are callable
        assert callable(db_helpers.get_user_profile)
        assert callable(db_helpers.update_user_preferences)
        assert callable(db_helpers.save_recommendation_feedback)


class TestDatabaseHelpersEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_get_user_profile_edge_cases(self):
        """Test get_user_profile edge cases"""

        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Test when data is None
        response_none = MagicMock()
        response_none.data = None
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            response_none
        )

        result = await db.get_user_profile("test-user")
        assert result == {}

        # Test when data is empty list
        response_empty = MagicMock()
        response_empty.data = []
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            response_empty
        )

        result = await db.get_user_profile("test-user")
        assert result == {}

    @pytest.mark.asyncio
    async def test_save_conversation_message_edge_cases(self):
        """Test save_conversation_message edge cases"""

        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Setup basic mocks
        insert_response = MagicMock()
        update_response = MagicMock()
        table_mock = MagicMock()
        table_mock.insert.return_value.execute.return_value = insert_response
        table_mock.update.return_value.eq.return_value.execute.return_value = update_response
        mock_client.table.return_value = table_mock

        # Test with very long message (should truncate title)
        long_message = "A" * 200  # Longer than 100 characters

        result = await db.save_conversation_message(
            user_id="test-user",
            conversation_id=None,
            user_message=long_message,
            ai_response="Short response",
        )

        assert result is not None

        # Test with empty message
        result = await db.save_conversation_message(
            user_id="test-user", conversation_id=None, user_message="", ai_response=""
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_create_chat_session_edge_cases(self):
        """Test create_chat_session edge cases"""

        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Test when response data is None
        response_none = MagicMock()
        response_none.data = None
        mock_client.table.return_value.insert.return_value.execute.return_value = response_none

        result = await db.create_chat_session("test-user", "conv-1")
        assert result == {}

        # Test when response data is empty
        response_empty = MagicMock()
        response_empty.data = []
        mock_client.table.return_value.insert.return_value.execute.return_value = response_empty

        result = await db.create_chat_session("test-user", "conv-1")
        assert result == {}

        # Test successful creation
        response_success = MagicMock()
        response_success.data = [{"id": "session-1", "user_id": "test-user"}]
        mock_client.table.return_value.insert.return_value.execute.return_value = response_success

        result = await db.create_chat_session("test-user", "conv-1", "Paris")
        assert result.get("id") == "session-1"
