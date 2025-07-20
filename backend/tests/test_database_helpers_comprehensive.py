"""
Comprehensive tests for database_helpers.py to improve coverage.
Focuses on functions that are currently missing test coverage.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestDatabaseHelpersComprehensive:
    """Comprehensive tests for database_helpers.py"""

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_conversation_id(self):
        """Test get_conversation_history with specific conversation_id"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock response for conversation messages
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "msg-1",
                "conversation_id": "conv-1",
                "role": "user",
                "content": "Hello",
                "created_at": "2023-01-01T00:00:00Z",
            },
            {
                "id": "msg-2",
                "conversation_id": "conv-1",
                "role": "assistant",
                "content": "Hi there!",
                "created_at": "2023-01-01T00:01:00Z",
            },
        ]

        # Setup the mock chain for conversation messages
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )
        mock_client.table.return_value = table_mock

        result = await db.get_conversation_history("test-user", "conv-1")

        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_get_conversation_history_without_conversation_id(self):
        """Test get_conversation_history without conversation_id (gets recent conversations)"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock response for conversations
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "conv-1",
                "title": "Test Conversation",
                "messages": [],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            }
        ]

        # Setup the mock chain for conversations
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        mock_client.table.return_value = table_mock

        result = await db.get_conversation_history("test-user", None)

        assert len(result) == 1
        assert result[0]["id"] == "conv-1"
        assert result[0]["title"] == "Test Conversation"

    @pytest.mark.asyncio
    async def test_get_conversation_history_error_handling(self):
        """Test get_conversation_history error handling"""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        result = await db.get_conversation_history("test-user", "conv-1")
        assert result == []

        result = await db.get_conversation_history("test-user", None)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_profile_with_preferences_and_destinations(self):
        """Test get_user_profile with view-based approach"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock user_profile_view data
        view_response = MagicMock()
        view_response.data = [
            {
                "id": "test-user",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "profile_completed": True,
                "profile_picture_url": "https://example.com/avatar.jpg",
                "last_login": "2023-01-01T00:00:00Z",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "style_preferences": {"colors": ["blue", "black"]},
                "size_info": {"height": "5'8\"", "weight": "150 lbs"},
                "travel_patterns": {"frequent_destinations": ["Europe"]},
                "quick_reply_preferences": {"enabled": True},
                "packing_methods": {"preferred": "rolling"},
                "currency_preferences": {"base_currency": "USD"},
            }
        ]

        # Setup table mock to return view data
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = view_response
        mock_client.table.return_value = mock_table

        result = await db.get_user_profile("test-user")

        assert result["id"] == "test-user"
        assert result["email"] == "test@example.com"
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["profile_completed"] is True
        assert result["profile_picture_url"] == "https://example.com/avatar.jpg"
        assert result["style_preferences"]["colors"] == ["blue", "black"]
        assert result["size_info"]["height"] == "5'8\""
        assert result["travel_patterns"]["frequent_destinations"] == ["Europe"]

    @pytest.mark.asyncio
    async def test_save_conversation_message_with_existing_conversation(self):
        """Test save_conversation_message with existing conversation_id"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Setup mocks
        insert_response = MagicMock()
        update_response = MagicMock()
        table_mock = MagicMock()
        table_mock.insert.return_value.execute.return_value = insert_response
        table_mock.update.return_value.eq.return_value.execute.return_value = update_response
        mock_client.table.return_value = table_mock

        result = await db.save_conversation_message(
            user_id="test-user",
            conversation_id="existing-conv-1",
            user_message="Hello",
            ai_response="Hi there!",
            conversation_type="travel",
            message_metadata={"weather": "sunny"},
        )

        assert result["success"] is True
        assert result["conversation_id"] == "existing-conv-1"
        assert "user_message_id" in result
        assert "ai_message_id" in result

    @pytest.mark.asyncio
    async def test_save_conversation_message_error_handling(self):
        """Test save_conversation_message error handling"""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        result = await db.save_conversation_message(
            user_id="test-user", conversation_id="conv-1", user_message="Hello", ai_response="Hi"
        )

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_update_user_preferences_update_existing(self):
        """Test update_user_preferences when preferences already exist"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock existing preferences
        existing_response = MagicMock()
        existing_response.data = [{"id": "pref-1", "user_id": "test-user"}]

        # Setup mocks
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.execute.return_value = existing_response
        table_mock.update.return_value.eq.return_value.execute.return_value = MagicMock()
        mock_client.table.return_value = table_mock

        result = await db.update_user_preferences(
            "test-user",
            {"style_preferences": {"colors": ["red", "blue"]}, "size_info": {"height": "6'0\""}},
        )

        assert result is True
        assert table_mock.update.called

    @pytest.mark.asyncio
    async def test_save_recommendation_feedback_success(self):
        """Test save_recommendation_feedback success case"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Setup mocks
        insert_response = MagicMock()
        table_mock = MagicMock()
        table_mock.insert.return_value.execute.return_value = insert_response
        mock_client.table.return_value = table_mock

        result = await db.save_recommendation_feedback(
            user_id="test-user",
            conversation_id="conv-1",
            message_id="msg-1",
            feedback_type="like",
            feedback_text="Great recommendation!",
            ai_response_content="Here's what you should pack...",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_save_recommendation_feedback_error(self):
        """Test save_recommendation_feedback error handling"""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        result = await db.save_recommendation_feedback(
            user_id="test-user",
            conversation_id="conv-1",
            message_id="msg-1",
            feedback_type="dislike",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_save_destination_new_destination(self):
        """Test save_destination for new destination"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock no existing destination
        existing_response = MagicMock()
        existing_response.data = []

        # Setup mocks
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            existing_response
        )
        table_mock.insert.return_value.execute.return_value = MagicMock()
        mock_client.table.return_value = table_mock

        result = await db.save_destination(
            user_id="test-user",
            destination_name="Tokyo",
            destination_data={"country": "Japan", "climate": "temperate"},
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_save_destination_existing_destination(self):
        """Test save_destination for existing destination (update visit count)"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock existing destination
        existing_response = MagicMock()
        existing_response.data = [{"id": "dest-1", "visit_count": 2}]

        # Setup mocks
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            existing_response
        )
        table_mock.update.return_value.eq.return_value.execute.return_value = MagicMock()
        mock_client.table.return_value = table_mock

        result = await db.save_destination(
            user_id="test-user", destination_name="Paris", destination_data={"country": "France"}
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_save_destination_error(self):
        """Test save_destination error handling"""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        result = await db.save_destination(user_id="test-user", destination_name="Paris")

        assert result is False

    @pytest.mark.asyncio
    async def test_get_user_conversations_success(self):
        """Test get_user_conversations success case"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock conversations response
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "conv-1",
                "title": "Paris Trip",
                "type": "travel",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "destination": "Paris",
            },
            {
                "id": "conv-2",
                "title": "Tokyo Trip",
                "type": "travel",
                "created_at": "2023-01-02T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
                "destination": "Tokyo",
            },
        ]

        # Setup mocks
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        mock_client.table.return_value = table_mock

        result = await db.get_user_conversations("test-user", limit=10)

        assert len(result) == 2
        assert result[0]["id"] == "conv-1"
        assert result[1]["id"] == "conv-2"

    @pytest.mark.asyncio
    async def test_get_user_conversations_error(self):
        """Test get_user_conversations error handling"""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        result = await db.get_user_conversations("test-user")
        assert result == []

    @pytest.mark.asyncio
    async def test_archive_conversation_success(self):
        """Test archive_conversation success case"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Setup mocks
        update_response = MagicMock()
        table_mock = MagicMock()
        table_mock.update.return_value.eq.return_value.eq.return_value.execute.return_value = (
            update_response
        )
        mock_client.table.return_value = table_mock

        result = await db.archive_conversation("test-user", "conv-1")

        assert result is True

    @pytest.mark.asyncio
    async def test_archive_conversation_error(self):
        """Test archive_conversation error handling"""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        result = await db.archive_conversation("test-user", "conv-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_conversation_success(self):
        """Test delete_conversation success case"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Setup mocks
        delete_response = MagicMock()
        table_mock = MagicMock()
        table_mock.delete.return_value.eq.return_value.execute.return_value = delete_response
        mock_client.table.return_value = table_mock

        result = await db.delete_conversation("test-user", "conv-1")

        assert result is True
        # Verify both delete operations were called
        assert table_mock.delete.call_count == 2

    @pytest.mark.asyncio
    async def test_delete_conversation_error(self):
        """Test delete_conversation error handling"""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        result = await db.delete_conversation("test-user", "conv-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_create_chat_session_success(self):
        """Test create_chat_session success case"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock successful response
        mock_response = MagicMock()
        mock_response.data = [{"id": "session-1", "user_id": "test-user"}]

        # Setup mocks
        table_mock = MagicMock()
        table_mock.insert.return_value.execute.return_value = mock_response
        mock_client.table.return_value = table_mock

        result = await db.create_chat_session("test-user", "conv-1", "Paris")

        assert result["id"] == "session-1"
        assert result["user_id"] == "test-user"

    @pytest.mark.asyncio
    async def test_create_chat_session_error(self):
        """Test create_chat_session error handling"""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        result = await db.create_chat_session("test-user", "conv-1")
        assert result == {}

    @pytest.mark.asyncio
    async def test_create_chat_session_empty_response(self):
        """Test create_chat_session with empty response data"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock empty response
        mock_response = MagicMock()
        mock_response.data = []

        # Setup mocks
        table_mock = MagicMock()
        table_mock.insert.return_value.execute.return_value = mock_response
        mock_client.table.return_value = table_mock

        result = await db.create_chat_session("test-user", "conv-1")
        assert result == {}

    @pytest.mark.asyncio
    async def test_standalone_functions_coverage(self):
        """Test standalone functions to ensure they're covered"""
        from app.services.database_helpers import (
            get_conversation_history,
            get_user_profile,
            save_conversation_message,
            save_recommendation_feedback,
            save_user_profile,
            update_user_preferences,
        )

        # Mock the db_helpers instance methods with AsyncMock
        with patch("app.services.database_helpers.db_helpers") as mock_db_helpers:
            # Setup AsyncMock for each method
            mock_db_helpers.get_conversation_history = AsyncMock(return_value=[{"id": "conv-1"}])
            mock_db_helpers.get_user_profile = AsyncMock(return_value={"id": "test-user"})
            mock_db_helpers.save_conversation_message = AsyncMock(return_value={"success": True})
            mock_db_helpers.update_user_preferences = AsyncMock(return_value=True)
            mock_db_helpers.save_recommendation_feedback = AsyncMock(return_value=True)
            mock_db_helpers.save_user_profile = AsyncMock(
                return_value={"id": "test-user", "first_name": "John"}
            )

            # Test get_conversation_history
            result = await get_conversation_history("test-user", "conv-1")
            assert result == [{"id": "conv-1"}]

            # Test get_user_profile
            result = await get_user_profile("test-user")
            assert result == {"id": "test-user"}

            # Test save_conversation_message
            result = await save_conversation_message("test-user", "conv-1", "Hello", "Hi")
            assert result == {"success": True}

            # Test update_user_preferences
            result = await update_user_preferences("test-user", {"style": "casual"})
            assert result is True

            # Test save_recommendation_feedback
            result = await save_recommendation_feedback("test-user", "conv-1", "msg-1", "like")
            assert result is True

            # Test save_user_profile
            result = await save_user_profile("test-user", {"first_name": "John"})
            assert result == {"id": "test-user", "first_name": "John"}

    @pytest.mark.asyncio
    async def test_save_user_profile_success(self):
        """Test save_user_profile success case"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock successful view update response
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "test-user",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "profile_completed": True,
                "profile_picture_url": "https://example.com/avatar.jpg",
                "style_preferences": {"colors": ["blue", "black"]},
                "size_info": {"height": "5'8\"", "weight": "150 lbs"},
            }
        ]

        # Setup table mock to return view update response
        mock_table = MagicMock()
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_response
        mock_client.table.return_value = mock_table

        profile_data = {
            "first_name": "John",
            "last_name": "Doe",
            "profile_completed": True,
            "style_preferences": {"colors": ["blue", "black"]},
        }

        result = await db.save_user_profile("test-user", profile_data)

        assert result is not None
        assert result["id"] == "test-user"
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["profile_completed"] is True
        assert result["profile_picture_url"] == "https://example.com/avatar.jpg"

    @pytest.mark.asyncio
    async def test_save_user_profile_no_data_returned(self):
        """Test save_user_profile when no data is returned"""
        mock_client = MagicMock()
        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        # Mock empty response
        mock_response = MagicMock()
        mock_response.data = []

        # Setup table mock to return empty response
        mock_table = MagicMock()
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_response
        mock_client.table.return_value = mock_table

        profile_data = {"first_name": "John", "last_name": "Doe"}

        result = await db.save_user_profile("test-user", profile_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_save_user_profile_exception(self):
        """Test save_user_profile error handling"""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        from app.services.database_helpers import DatabaseHelpers

        db = DatabaseHelpers(supabase_client=mock_client)

        profile_data = {"first_name": "John", "last_name": "Doe"}

        result = await db.save_user_profile("test-user", profile_data)

        assert result is None
