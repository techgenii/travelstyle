"""
Tests for chat conversation management endpoints.
"""

from unittest.mock import patch

from fastapi import status


def test_get_user_conversations_success(authenticated_client):
    """Test successful retrieval of user conversations."""
    with patch("app.api.v1.chat.db_helpers.get_user_conversations") as mock_get:
        mock_get.return_value = [{"id": "conv-1", "title": "Test"}]
        response = authenticated_client.get("/api/v1/chat/conversations")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "conversations" in data
        assert isinstance(data["conversations"], list)


def test_get_user_conversations_no_auth(client):
    """Test conversation retrieval without authentication."""
    response = client.get("/api/v1/chat/conversations")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_conversations_error(authenticated_client):
    """Test conversation retrieval when it fails."""
    with patch("app.api.v1.chat.db_helpers.get_user_conversations", side_effect=Exception("fail")):
        response = authenticated_client.get("/api/v1/chat/conversations")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_delete_conversation_success(authenticated_client):
    """Test successful conversation deletion."""
    with patch("app.api.v1.chat.db_helpers.delete_conversation") as mock_delete:
        mock_delete.return_value = True
        response = authenticated_client.delete("/api/v1/chat/conversations/conv-1")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


def test_delete_conversation_no_auth(client):
    """Test conversation deletion without authentication."""
    response = client.delete("/api/v1/chat/conversations/conv-1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_conversation_error(authenticated_client):
    """Test conversation deletion when it fails."""
    with patch("app.api.v1.chat.db_helpers.delete_conversation", side_effect=Exception("fail")):
        response = authenticated_client.delete("/api/v1/chat/conversations/conv-1")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_archive_conversation_success(authenticated_client):
    """Test successful conversation archiving."""
    with patch("app.api.v1.chat.db_helpers.archive_conversation") as mock_archive:
        mock_archive.return_value = True
        response = authenticated_client.put("/api/v1/chat/conversations/conv-1/archive")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


def test_archive_conversation_no_auth(client):
    """Test conversation archiving without authentication."""
    response = client.put("/api/v1/chat/conversations/conv-1/archive")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_archive_conversation_error(authenticated_client):
    """Test conversation archiving when it fails."""
    with patch("app.api.v1.chat.db_helpers.archive_conversation", side_effect=Exception("fail")):
        response = authenticated_client.put("/api/v1/chat/conversations/conv-1/archive")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
