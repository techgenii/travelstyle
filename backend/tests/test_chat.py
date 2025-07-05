"""
Tests for chat API endpoints.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status

class TestChatEndpoints:
    """Test cases for chat endpoints."""

    def test_chat_endpoint_success(self, client, mock_auth_headers, mock_chat_request, mock_recommendation_response):
        """Test successful chat request."""
        with patch('app.api.v1.chat.get_current_user') as mock_get_user, \
             patch('app.api.v1.chat.orchestrator_service.generate_travel_recommendations') as mock_generate:
            
            # Mock the current user
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            # Mock the orchestrator response
            mock_generate.return_value = mock_recommendation_response
            
            response = client.post(
                "/api/v1/chat/",
                json=mock_chat_request,
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
            assert "quick_replies" in data
            assert "confidence_score" in data

    def test_chat_endpoint_no_auth(self, client, mock_chat_request):
        """Test chat request without authentication."""
        response = client.post(
            "/api/v1/chat/",
            json=mock_chat_request
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_chat_endpoint_invalid_request(self, client, mock_auth_headers):
        """Test chat request with invalid data."""
        with patch('app.api.v1.chat.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            response = client.post(
                "/api/v1/chat/",
                json={"invalid": "data"},
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_chat_endpoint_orchestrator_error(self, client, mock_auth_headers, mock_chat_request):
        """Test chat request when orchestrator fails."""
        with patch('app.api.v1.chat.get_current_user') as mock_get_user, \
             patch('app.api.v1.chat.orchestrator_service.generate_travel_recommendations') as mock_generate:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            # Mock orchestrator to raise an exception
            mock_generate.side_effect = Exception("Orchestrator error")
            
            response = client.post(
                "/api/v1/chat/",
                json=mock_chat_request,
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to process chat request" in response.json()["detail"]

    def test_get_conversation_history_success(self, client, mock_auth_headers):
        """Test successful conversation history retrieval."""
        with patch('app.api.v1.chat.get_current_user') as mock_get_user, \
             patch('app.api.v1.chat.get_conversation_history') as mock_get_history:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            mock_get_history.return_value = [
                {"message": "Hello", "timestamp": "2024-01-01T12:00:00Z"},
                {"message": "Hi there!", "timestamp": "2024-01-01T12:01:00Z"}
            ]
            
            response = client.get(
                "/api/v1/chat/conversations/test-conversation-123/history",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "conversation_id" in data
            assert "history" in data
            assert len(data["history"]) == 2

    def test_get_conversation_history_no_auth(self, client):
        """Test conversation history without authentication."""
        response = client.get("/api/v1/chat/conversations/test-conversation-123/history")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_conversation_history_error(self, client, mock_auth_headers):
        """Test conversation history when database fails."""
        with patch('app.api.v1.chat.get_current_user') as mock_get_user, \
             patch('app.api.v1.chat.get_conversation_history') as mock_get_history:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            # Mock database to raise an exception
            mock_get_history.side_effect = Exception("Database error")
            
            response = client.get(
                "/api/v1/chat/conversations/test-conversation-123/history",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve conversation" in response.json()["detail"] 