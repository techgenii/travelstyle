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
Tests for chat API endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from app.models.responses import ChatResponse
from app.services.openai_service import OpenAIService
from fastapi import status


class TestChatEndpoints:
    """Test cases for chat endpoints."""

    def test_chat_endpoint_success(
        self, authenticated_client, mock_chat_request, mock_recommendation_response
    ):
        """Test successful chat request."""
        with patch(
            "app.services.orchestrator.orchestrator_service.generate_travel_recommendations"
        ) as mock_generate:
            # Mock the orchestrator response with a proper ChatResponse object
            mock_generate.return_value = ChatResponse(
                message=mock_recommendation_response["message"],
                quick_replies=mock_recommendation_response["quick_replies"],
                suggestions=mock_recommendation_response["suggestions"],
                confidence_score=mock_recommendation_response["confidence_score"],
            )
            response = authenticated_client.post("/api/v1/chat/", json=mock_chat_request)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
            assert "quick_replies" in data
            assert "confidence_score" in data

    def test_chat_endpoint_no_auth(self, client, mock_chat_request):
        """Test chat request without authentication."""
        response = client.post("/api/v1/chat/", json=mock_chat_request)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_chat_endpoint_invalid_request(self, authenticated_client):
        """Test chat request with invalid data."""
        response = authenticated_client.post("/api/v1/chat/", json={"invalid": "data"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_chat_endpoint_orchestrator_error(self, authenticated_client, mock_chat_request):
        """Test chat request when orchestrator fails."""
        with patch(
            "app.services.orchestrator.orchestrator_service.generate_travel_recommendations"
        ) as mock_generate:
            # Mock orchestrator to raise an exception
            mock_generate.side_effect = Exception("Orchestrator error")
            response = authenticated_client.post("/api/v1/chat/", json=mock_chat_request)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to process chat request" in response.json()["detail"]

    def test_get_conversation_history_success(self, authenticated_client):
        """Test successful conversation history retrieval."""
        response = authenticated_client.get("/api/v1/chat/dialog/test-conversation-123/history")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "conversation_id" in data
        assert "history" in data
        assert len(data["history"]) == 0  # Empty list as per implementation

    def test_get_conversation_history_no_auth(self, client):
        """Test conversation history without authentication."""
        response = client.get("/api/v1/chat/dialog/test-conversation-123/history")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_conversation_history_error(self, authenticated_client):
        """Test conversation history when database fails."""
        with patch("app.api.v1.chat.db_helpers.get_conversation_history") as mock_get_history:
            # Mock the function to raise an exception
            mock_get_history.side_effect = Exception("Database connection failed")

            response = authenticated_client.get("/api/v1/chat/dialog/test-conversation-123/history")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve dialog" in response.json()["detail"]

    def test_chat_endpoint_database_error(self, authenticated_client, mock_chat_request):
        """Test chat request when database operations fail."""
        with patch("app.api.v1.chat.db_helpers.get_conversation_history") as mock_get_history:
            # Mock database function to raise an exception
            mock_get_history.side_effect = Exception("Database connection failed")

            response = authenticated_client.post("/api/v1/chat/", json=mock_chat_request)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to process chat request" in response.json()["detail"]

    def test_chat_endpoint_user_profile_error(self, authenticated_client, mock_chat_request):
        """Test chat request when user profile retrieval fails."""
        with patch("app.api.v1.chat.db_helpers.get_user_profile") as mock_get_profile:
            # Mock user profile function to raise an exception
            mock_get_profile.side_effect = Exception("User profile not found")

            response = authenticated_client.post("/api/v1/chat/", json=mock_chat_request)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to process chat request" in response.json()["detail"]

    # Additional tests for missing endpoints
    def test_get_user_conversations_success(self, authenticated_client):
        """Test successful user conversations retrieval."""
        response = authenticated_client.get("/api/v1/chat/dialog")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "conversations" in data

    def test_get_user_conversations_no_auth(self, client):
        """Test user conversations without authentication."""
        response = client.get("/api/v1/chat/dialog")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_conversations_error(self, authenticated_client):
        """Test user conversations when database fails."""
        with patch("app.api.v1.chat.db_helpers.get_user_conversations") as mock_get_conversations:
            # Mock the function to raise an exception
            mock_get_conversations.side_effect = Exception("Database connection failed")

            response = authenticated_client.get("/api/v1/chat/dialog")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve conversations" in response.json()["detail"]

    def test_delete_conversation_success(self, authenticated_client):
        """Test successful conversation deletion."""
        with patch("app.api.v1.chat.db_helpers.delete_conversation") as mock_delete:
            mock_delete.return_value = True
            response = authenticated_client.delete("/api/v1/chat/dialog/test-conversation-123")
            assert response.status_code == status.HTTP_200_OK
            assert "Conversation deleted successfully" in response.json()["message"]

    def test_delete_conversation_no_auth(self, client):
        """Test conversation deletion without authentication."""
        response = client.delete("/api/v1/chat/dialog/test-conversation-123")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_conversation_failure(self, authenticated_client):
        """Test conversation deletion when database fails."""
        with patch("app.api.v1.chat.db_helpers.delete_conversation") as mock_delete:
            mock_delete.return_value = False
            response = authenticated_client.delete("/api/v1/chat/dialog/test-conversation-123")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to delete conversation" in response.json()["detail"]

    def test_delete_conversation_error(self, authenticated_client):
        """Test conversation deletion when exception occurs."""
        with patch("app.api.v1.chat.db_helpers.delete_conversation") as mock_delete:
            mock_delete.side_effect = Exception("Database error")
            response = authenticated_client.delete("/api/v1/chat/dialog/test-conversation-123")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to delete conversation" in response.json()["detail"]

    def test_archive_conversation_success(self, authenticated_client):
        """Test successful conversation archiving."""
        with patch("app.api.v1.chat.db_helpers.archive_conversation") as mock_archive:
            mock_archive.return_value = True
            response = authenticated_client.put("/api/v1/chat/dialog/test-conversation-123/archive")
            assert response.status_code == status.HTTP_200_OK
            assert "Conversation archived successfully" in response.json()["message"]

    def test_archive_conversation_no_auth(self, client):
        """Test conversation archiving without authentication."""
        response = client.put("/api/v1/chat/dialog/test-conversation-123/archive")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_archive_conversation_failure(self, authenticated_client):
        """Test conversation archiving when database fails."""
        with patch("app.api.v1.chat.db_helpers.archive_conversation") as mock_archive:
            mock_archive.return_value = False
            response = authenticated_client.put("/api/v1/chat/dialog/test-conversation-123/archive")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to archive conversation" in response.json()["detail"]

    def test_archive_conversation_error(self, authenticated_client):
        """Test conversation archiving when exception occurs."""
        with patch("app.api.v1.chat.db_helpers.archive_conversation") as mock_archive:
            mock_archive.side_effect = Exception("Database error")
            response = authenticated_client.put("/api/v1/chat/dialog/test-conversation-123/archive")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to archive conversation" in response.json()["detail"]

    def test_start_conversation_success(self, authenticated_client):
        """Test successful conversation start."""
        with patch("app.api.v1.chat.db_helpers.create_chat_session") as mock_create:
            mock_create.return_value = {"id": "test-session", "conversation_id": "test-conv-123"}
            response = authenticated_client.post(
                "/api/v1/chat/start", json={"destination": "Paris"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "conversation_id" in data
            assert "conversation" in data
            assert "message" in data

    def test_start_conversation_no_data(self, authenticated_client):
        """Test conversation start with no data (None)."""
        with patch("app.api.v1.chat.db_helpers.create_chat_session") as mock_create:
            mock_create.return_value = {"id": "test-session", "conversation_id": "test-conv-123"}
            response = authenticated_client.post("/api/v1/chat/start", json=None)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "conversation_id" in data
            assert "conversation" in data
            assert "message" in data

    def test_start_conversation_no_auth(self, client):
        """Test conversation start without authentication."""
        response = client.post("/api/v1/chat/start", json={"destination": "Paris"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_start_conversation_with_conversation_id(self, authenticated_client):
        """Test conversation start with provided conversation_id."""
        with patch("app.api.v1.chat.db_helpers.create_chat_session") as mock_create:
            mock_create.return_value = {"id": "test-session", "conversation_id": "custom-conv-123"}
            response = authenticated_client.post(
                "/api/v1/chat/start",
                json={"conversation_id": "custom-conv-123", "destination": "Paris"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["conversation_id"] == "custom-conv-123"

    def test_start_conversation_error(self, authenticated_client):
        """Test conversation start when exception occurs."""
        with patch("app.api.v1.chat.db_helpers.create_chat_session") as mock_create:
            mock_create.side_effect = Exception("Database error")
            response = authenticated_client.post(
                "/api/v1/chat/start", json={"destination": "Paris"}
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to start conversation" in response.json()["detail"]

    def test_save_feedback_success(self, authenticated_client):
        """Test successful feedback saving."""
        with patch("app.api.v1.chat.db_helpers.save_recommendation_feedback") as mock_save:
            mock_save.return_value = True
            feedback_data = {
                "conversation_id": "test-conv-123",
                "message_id": "test-msg-123",
                "feedback_type": "positive",
                "feedback_text": "Great recommendation!",
                "ai_response_content": "Here's your recommendation",
            }
            response = authenticated_client.post("/api/v1/chat/feedback", json=feedback_data)
            assert response.status_code == status.HTTP_200_OK
            assert "Feedback saved successfully" in response.json()["message"]

    def test_save_feedback_no_auth(self, client):
        """Test feedback saving without authentication."""
        feedback_data = {
            "conversation_id": "test-conv-123",
            "message_id": "test-msg-123",
            "feedback_type": "positive",
        }
        response = client.post("/api/v1/chat/feedback", json=feedback_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_save_feedback_missing_fields(self, authenticated_client):
        """Test feedback saving with missing required fields."""
        # Missing conversation_id
        feedback_data = {"message_id": "test-msg-123", "feedback_type": "positive"}
        response = authenticated_client.post("/api/v1/chat/feedback", json=feedback_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Missing required fields" in response.json()["detail"]

        # Missing message_id
        feedback_data = {"conversation_id": "test-conv-123", "feedback_type": "positive"}
        response = authenticated_client.post("/api/v1/chat/feedback", json=feedback_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Missing required fields" in response.json()["detail"]

        # Missing feedback_type
        feedback_data = {"conversation_id": "test-conv-123", "message_id": "test-msg-123"}
        response = authenticated_client.post("/api/v1/chat/feedback", json=feedback_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Missing required fields" in response.json()["detail"]

    def test_save_feedback_failure(self, authenticated_client):
        """Test feedback saving when database fails."""
        with patch("app.api.v1.chat.db_helpers.save_recommendation_feedback") as mock_save:
            mock_save.return_value = False
            feedback_data = {
                "conversation_id": "test-conv-123",
                "message_id": "test-msg-123",
                "feedback_type": "positive",
            }
            response = authenticated_client.post("/api/v1/chat/feedback", json=feedback_data)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to save feedback" in response.json()["detail"]

    def test_save_feedback_error(self, authenticated_client):
        """Test feedback saving when exception occurs."""
        with patch("app.api.v1.chat.db_helpers.save_recommendation_feedback") as mock_save:
            mock_save.side_effect = Exception("Database error")
            feedback_data = {
                "conversation_id": "test-conv-123",
                "message_id": "test-msg-123",
                "feedback_type": "positive",
            }
            response = authenticated_client.post("/api/v1/chat/feedback", json=feedback_data)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to save feedback" in response.json()["detail"]

    def test_start_conversation_http_exception(self, authenticated_client):
        """Test start conversation when HTTPException is raised."""
        with patch("app.api.v1.chat.db_helpers.create_chat_session") as mock_create:
            # Mock the function to raise an HTTPException
            from fastapi import HTTPException

            mock_create.side_effect = HTTPException(status_code=400, detail="Bad request")

            response = authenticated_client.post(
                "/api/v1/chat/start", json={"destination": "Paris"}
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Bad request" in response.json()["detail"]

    def test_start_conversation_http_exception_from_within(self, authenticated_client):
        """Test start conversation when HTTPException is raised from within the function."""
        # This test specifically targets line 155 by mocking the function to raise an HTTPException
        with patch("app.api.v1.chat.db_helpers.create_chat_session") as mock_create:
            from fastapi import HTTPException

            # Mock to raise HTTPException which should be re-raised by the except block
            mock_create.side_effect = HTTPException(status_code=422, detail="Validation error")

            response = authenticated_client.post(
                "/api/v1/chat/start", json={"destination": "Paris"}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "Validation error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_response_success():
    service = OpenAIService()
    mock_ai_message = 'Hello! [QUICK: "Show accessories"]'
    mock_response = AsyncMock()
    mock_response.choices = [
        type("obj", (object,), {"message": type("obj", (object,), {"content": mock_ai_message})()})
    ]
    with patch.object(
        service.client.chat.completions, "create", new=AsyncMock(return_value=mock_response)
    ):
        result = await service.generate_response(
            user_message="Hi!",
            conversation_history=[],
            cultural_context=None,
            weather_context=None,
            user_profile=None,
        )
        assert isinstance(result, ChatResponse)
        assert "Hello!" in result.message
        assert any(qr.text == "Show accessories" for qr in result.quick_replies)


@pytest.mark.asyncio
async def test_generate_response_error():
    service = OpenAIService()
    with patch.object(
        service.client.chat.completions, "create", new=AsyncMock(side_effect=Exception("fail"))
    ):
        result = await service.generate_response(
            user_message="Hi!",
            conversation_history=[],
            cultural_context=None,
            weather_context=None,
            user_profile=None,
        )
        assert isinstance(result, ChatResponse)
        assert "trouble processing your request" in result.message
        assert result.confidence_score == 0.0


def test_build_system_prompt():
    service = OpenAIService()
    prompt = service._build_system_prompt()
    assert "TravelStyle AI" in prompt
    assert "CAPABILITIES" in prompt


def test_build_context_prompt():
    service = OpenAIService()
    context = service._build_context_prompt(
        cultural_context={"culture": "test"},
        weather_context={"weather": "test"},
        user_profile={"user": "test"},
    )
    assert "Cultural Insights" in context
    assert "Weather Summary" in context
    assert "User Preferences" in context


def test_process_response():
    service = OpenAIService()
    ai_message = (
        'Here is your answer. [QUICK: "Show accessories"] Would you like more?'
        " Also consider other options."
    )
    result = service._process_response(ai_message)
    assert "Here is your answer." in result.message
    assert any(qr.text == "Show accessories" for qr in result.quick_replies)
    assert "Get more details" in result.suggestions
    assert "Show alternatives" in result.suggestions
