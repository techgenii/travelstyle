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
        with patch("app.api.v1.chat.get_conversation_history") as mock_get_history:
            # Mock the function to raise an exception
            mock_get_history.side_effect = Exception("Database connection failed")

            response = authenticated_client.get("/api/v1/chat/dialog/test-conversation-123/history")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve dialog" in response.json()["detail"]

    def test_chat_endpoint_database_error(self, authenticated_client, mock_chat_request):
        """Test chat request when database operations fail."""
        with patch("app.api.v1.chat.get_conversation_history") as mock_get_history:
            # Mock database function to raise an exception
            mock_get_history.side_effect = Exception("Database connection failed")

            response = authenticated_client.post("/api/v1/chat/", json=mock_chat_request)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to process chat request" in response.json()["detail"]

    def test_chat_endpoint_user_profile_error(self, authenticated_client, mock_chat_request):
        """Test chat request when user profile retrieval fails."""
        with patch("app.api.v1.chat.get_user_profile") as mock_get_profile:
            # Mock user profile function to raise an exception
            mock_get_profile.side_effect = Exception("User profile not found")

            response = authenticated_client.post("/api/v1/chat/", json=mock_chat_request)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to process chat request" in response.json()["detail"]


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
