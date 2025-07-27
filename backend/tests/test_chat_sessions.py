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
