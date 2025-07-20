from unittest.mock import patch

from fastapi import status


def test_save_feedback_success(authenticated_client):
    with patch("app.api.v1.chat.save_recommendation_feedback") as mock_save:
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
    with patch("app.api.v1.chat.save_recommendation_feedback", side_effect=Exception("fail")):
        response = authenticated_client.post(
            "/api/v1/chat/feedback",
            json={"conversation_id": "conv-1", "message_id": "msg-1", "feedback_type": "like"},
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_save_feedback_invalid(authenticated_client):
    response = authenticated_client.post("/api/v1/chat/feedback", json={})
    assert response.status_code in (400, 422)
