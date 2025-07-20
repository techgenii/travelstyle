"""
Tests for user session management endpoints (in chat.py).
"""

from unittest.mock import patch

from fastapi import status


class TestUserSessionManagement:
    """Test cases for session management endpoints."""

    @patch("app.api.v1.chat.db_helpers.create_chat_session")
    def test_create_session_success(self, mock_create, authenticated_client):
        """Test successful session creation."""
        # Mock the database call to return a session
        mock_create.return_value = {"session_id": "sess-1"}

        response = authenticated_client.post(
            "/api/v1/chat/sessions/create",
            json={"conversation_id": "conv-1", "destination": "Paris"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "session" in response.json()

    def test_create_session_no_auth(self, client):
        """Test session creation without authentication."""
        response = client.post("/api/v1/chat/sessions/create", json={})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.v1.chat.db_helpers.create_chat_session")
    def test_create_session_error(self, mock_create, authenticated_client):
        """Test session creation when it fails."""
        # Mock the database call to raise an exception
        mock_create.side_effect = Exception("fail")

        response = authenticated_client.post(
            "/api/v1/chat/sessions/create",
            json={"conversation_id": "conv-1", "destination": "Paris"},
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_create_session_invalid(self, authenticated_client):
        """Test session creation with invalid data."""
        response = authenticated_client.post("/api/v1/chat/sessions/create", json={})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_session_missing_conversation_id(self, authenticated_client):
        """Test session creation with missing conversation_id."""
        response = authenticated_client.post(
            "/api/v1/chat/sessions/create",
            json={"destination": "Paris"},  # Missing conversation_id
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
