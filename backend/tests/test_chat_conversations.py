"""
Tests for chat session management endpoints.
"""

from unittest.mock import patch

from fastapi import status


def test_create_session_success(authenticated_client):
    """Test successful session creation."""
    with patch("app.api.v1.chat.db_helpers.create_chat_session") as mock_create:
        mock_create.return_value = {"session_id": "sess-1"}
        response = authenticated_client.post(
            "/api/v1/chat/sessions/create",
            json={"conversation_id": "conv-1", "destination": "Paris"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "session" in response.json()


def test_create_session_no_auth(client):
    """Test session creation without authentication."""
    response = client.post("/api/v1/chat/sessions/create", json={})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_session_error(authenticated_client):
    """Test session creation when it fails."""
    with patch("app.api.v1.chat.db_helpers.create_chat_session", side_effect=Exception("fail")):
        response = authenticated_client.post(
            "/api/v1/chat/sessions/create",
            json={"conversation_id": "conv-1", "destination": "Paris"},
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_session_invalid(authenticated_client):
    """Test session creation with invalid data."""
    response = authenticated_client.post("/api/v1/chat/sessions/create", json={})
    assert response.status_code in (400, 422)
