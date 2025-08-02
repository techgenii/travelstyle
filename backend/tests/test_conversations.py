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
Tests for ConversationOperations class.
"""

from unittest.mock import MagicMock, patch

import pytest
from app.services.database.conversations import ConversationOperations


class TestConversationOperations:
    """Test ConversationOperations class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Supabase client."""
        return MagicMock()

    @pytest.fixture
    def conversation_operations(self, mock_client):
        """Create a ConversationOperations instance with mock client."""
        return ConversationOperations(mock_client)

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_conversation_id_success(
        self, conversation_operations, mock_client
    ):
        """Test successful conversation history retrieval with conversation_id."""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "msg-1", "content": "Hello", "role": "user"},
            {"id": "msg-2", "content": "Hi there!", "role": "assistant"},
        ]

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await conversation_operations.get_conversation_history(
                    "test-user", "conv-1"
                )

                assert result == [
                    {"id": "msg-1", "content": "Hello", "role": "user"},
                    {"id": "msg-2", "content": "Hi there!", "role": "assistant"},
                ]

    @pytest.mark.asyncio
    async def test_get_conversation_history_without_conversation_id_success(
        self, conversation_operations, mock_client
    ):
        """Test successful conversation history retrieval without conversation_id."""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "conv-1", "title": "First conversation", "messages": 5},
            {"id": "conv-2", "title": "Second conversation", "messages": 3},
        ]

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await conversation_operations.get_conversation_history("test-user", None)

                assert result == [
                    {"id": "conv-1", "title": "First conversation", "messages": 5},
                    {"id": "conv-2", "title": "Second conversation", "messages": 3},
                ]

    @pytest.mark.asyncio
    async def test_get_conversation_history_invalid_user_id(self, conversation_operations):
        """Test get_conversation_history with invalid user ID."""
        result = await conversation_operations.get_conversation_history("invalid-id", "conv-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_conversation_history_invalid_conversation_id(self, conversation_operations):
        """Test get_conversation_history with invalid conversation ID."""
        result = await conversation_operations.get_conversation_history("test-user", "invalid-conv")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_conversation_history_rate_limited(self, conversation_operations):
        """Test get_conversation_history when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await conversation_operations.get_conversation_history("test-user", "conv-1")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_conversation_history_no_data(self, conversation_operations, mock_client):
        """Test get_conversation_history when no data is returned."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await conversation_operations.get_conversation_history(
                    "test-user", "conv-1"
                )
                assert result == []

    @pytest.mark.asyncio
    async def test_get_conversation_history_exception(self, conversation_operations, mock_client):
        """Test get_conversation_history when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await conversation_operations.get_conversation_history(
                    "test-user", "conv-1"
                )
                assert result == []

    @pytest.mark.asyncio
    async def test_save_conversation_message_new_conversation_success(
        self, conversation_operations, mock_client
    ):
        """Test successful conversation message save with new conversation."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = None

                result = await conversation_operations.save_conversation_message(
                    "test-user", None, "Hello", "Hi there!", "mixed", {"key": "value"}
                )

                assert result is not None
                assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_save_conversation_message_existing_conversation_success(
        self, conversation_operations, mock_client
    ):
        """Test successful conversation message save with existing conversation."""
        current_response = MagicMock()
        current_response.data = [{"messages": 5}]

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                # Mock the three database operations: get current count, update conversation, insert user message, insert ai message
                mock_to_thread.side_effect = [current_response, None, None, None]

                result = await conversation_operations.save_conversation_message(
                    "test-user", "conv-1", "Hello", "Hi there!"
                )

                assert result == "conv-1"

    @pytest.mark.asyncio
    async def test_save_conversation_message_invalid_user_id(self, conversation_operations):
        """Test save_conversation_message with invalid user ID."""
        result = await conversation_operations.save_conversation_message(
            "invalid-id", "conv-1", "Hello", "Hi there!"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_save_conversation_message_invalid_conversation_id(self, conversation_operations):
        """Test save_conversation_message with invalid conversation ID."""
        result = await conversation_operations.save_conversation_message(
            "test-user", "invalid-conv", "Hello", "Hi there!"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_save_conversation_message_invalid_user_message(self, conversation_operations):
        """Test save_conversation_message with invalid user message."""
        result = await conversation_operations.save_conversation_message(
            "test-user", "conv-1", "", "Hi there!"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_save_conversation_message_invalid_ai_response(self, conversation_operations):
        """Test save_conversation_message with invalid AI response."""
        result = await conversation_operations.save_conversation_message(
            "test-user", "conv-1", "Hello", ""
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_save_conversation_message_rate_limited(self, conversation_operations):
        """Test save_conversation_message when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await conversation_operations.save_conversation_message(
                "test-user", "conv-1", "Hello", "Hi there!"
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_save_conversation_message_exception(self, conversation_operations, mock_client):
        """Test save_conversation_message when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await conversation_operations.save_conversation_message(
                    "test-user", "conv-1", "Hello", "Hi there!"
                )
                assert result is None

    @pytest.mark.asyncio
    async def test_get_user_conversations_success(self, conversation_operations, mock_client):
        """Test successful user conversations retrieval."""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "conv-1", "title": "First conversation", "messages": 5},
            {"id": "conv-2", "title": "Second conversation", "messages": 3},
        ]

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await conversation_operations.get_user_conversations("test-user", 10)

                assert result == [
                    {"id": "conv-1", "title": "First conversation", "messages": 5},
                    {"id": "conv-2", "title": "Second conversation", "messages": 3},
                ]

    @pytest.mark.asyncio
    async def test_get_user_conversations_invalid_user_id(self, conversation_operations):
        """Test get_user_conversations with invalid user ID."""
        result = await conversation_operations.get_user_conversations("invalid-id")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_conversations_rate_limited(self, conversation_operations):
        """Test get_user_conversations when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await conversation_operations.get_user_conversations("test-user")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_user_conversations_no_data(self, conversation_operations, mock_client):
        """Test get_user_conversations when no data is returned."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = mock_response

                result = await conversation_operations.get_user_conversations("test-user")
                assert result == []

    @pytest.mark.asyncio
    async def test_get_user_conversations_exception(self, conversation_operations, mock_client):
        """Test get_user_conversations when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await conversation_operations.get_user_conversations("test-user")
                assert result == []

    @pytest.mark.asyncio
    async def test_archive_conversation_success(self, conversation_operations, mock_client):
        """Test successful conversation archive."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = None

                result = await conversation_operations.archive_conversation("test-user", "conv-1")
                assert result is True

    @pytest.mark.asyncio
    async def test_archive_conversation_invalid_user_id(self, conversation_operations):
        """Test archive_conversation with invalid user ID."""
        result = await conversation_operations.archive_conversation("invalid-id", "conv-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_archive_conversation_invalid_conversation_id(self, conversation_operations):
        """Test archive_conversation with invalid conversation ID."""
        result = await conversation_operations.archive_conversation("test-user", "invalid-conv")
        assert result is False

    @pytest.mark.asyncio
    async def test_archive_conversation_rate_limited(self, conversation_operations):
        """Test archive_conversation when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await conversation_operations.archive_conversation("test-user", "conv-1")
            assert result is False

    @pytest.mark.asyncio
    async def test_archive_conversation_exception(self, conversation_operations, mock_client):
        """Test archive_conversation when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await conversation_operations.archive_conversation("test-user", "conv-1")
                assert result is False

    @pytest.mark.asyncio
    async def test_delete_conversation_success(self, conversation_operations, mock_client):
        """Test successful conversation deletion."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = None

                result = await conversation_operations.delete_conversation("test-user", "conv-1")
                assert result is True

    @pytest.mark.asyncio
    async def test_delete_conversation_invalid_user_id(self, conversation_operations):
        """Test delete_conversation with invalid user ID."""
        result = await conversation_operations.delete_conversation("invalid-id", "conv-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_conversation_invalid_conversation_id(self, conversation_operations):
        """Test delete_conversation with invalid conversation ID."""
        result = await conversation_operations.delete_conversation("test-user", "invalid-conv")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_conversation_rate_limited(self, conversation_operations):
        """Test delete_conversation when rate limited."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = False

            result = await conversation_operations.delete_conversation("test-user", "conv-1")
            assert result is False

    @pytest.mark.asyncio
    async def test_delete_conversation_exception(self, conversation_operations, mock_client):
        """Test delete_conversation when exception occurs."""
        with patch("app.services.rate_limiter.db_rate_limiter.acquire") as mock_rate_limit:
            mock_rate_limit.return_value = True

            with patch("asyncio.to_thread") as mock_to_thread:
                mock_to_thread.side_effect = Exception("Database error")

                result = await conversation_operations.delete_conversation("test-user", "conv-1")
                assert result is False

    def test_conversation_operations_init(self, mock_client):
        """Test ConversationOperations initialization."""
        conv_ops = ConversationOperations(mock_client)
        assert conv_ops.client == mock_client
