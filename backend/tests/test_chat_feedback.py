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

from unittest.mock import patch

from fastapi import status


def test_save_feedback_success(authenticated_client):
    with patch("app.api.v1.chat.db_helpers.save_recommendation_feedback") as mock_save:
        mock_save.return_value = True
        response = authenticated_client.post(
            "/api/v1/chat/feedback",
            json={"conversation_id": "conv-1", "message_id": "msg-1", "feedback_type": "like"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


def test_save_feedback_no_auth(client):
    response = client.post("/api/v1/chat/feedback", json={})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_save_feedback_error(authenticated_client):
    with patch(
        "app.api.v1.chat.db_helpers.save_recommendation_feedback", side_effect=Exception("fail")
    ):
        response = authenticated_client.post(
            "/api/v1/chat/feedback",
            json={"conversation_id": "conv-1", "message_id": "msg-1", "feedback_type": "like"},
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_save_feedback_invalid(authenticated_client):
    response = authenticated_client.post("/api/v1/chat/feedback", json={})
    assert response.status_code in (400, 422)
