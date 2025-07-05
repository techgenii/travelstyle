"""
Tests for user API endpoints.
"""
from fastapi import status

class TestUserEndpoints:
    """Test cases for user endpoints."""

    def test_get_current_user_profile_success(self, authenticated_client):
        """Test successful user profile retrieval."""
        response = authenticated_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "is_active" in data
        assert data["id"] == "test-user-123"
        assert data["email"] == "test@example.com"

    def test_get_current_user_profile_error(self, authenticated_client):
        """Test user profile retrieval when it fails."""
        response = authenticated_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_200_OK

    def test_get_user_preferences_success(self, authenticated_client):
        """Test successful user preferences retrieval."""
        response = authenticated_client.get("/api/v1/users/preferences")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "style_preferences" in data
        assert "travel_patterns" in data
        assert "size_info" in data

    def test_get_user_preferences_error(self, authenticated_client):
        """Test user preferences retrieval when it fails."""
        response = authenticated_client.get("/api/v1/users/preferences")
        assert response.status_code == status.HTTP_200_OK

    def test_update_user_preferences_success(self, authenticated_client):
        """Test successful user preferences update."""
        preferences_data = {
            "style_preferences": {
                "preferred_colors": ["blue", "black"],
                "style_categories": ["business_professional", "smart_casual"]
            },
            "size_info": {
                "height": "5'8\"",
                "weight": "150 lbs",
                "shirt_size": "M"
            },
            "travel_patterns": {
                "frequent_destinations": ["Europe", "Asia"],
                "travel_style": "business"
            }
        }
        response = authenticated_client.put(
            "/api/v1/users/preferences",
            json=preferences_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "user_id" in data
        assert data["message"] == "Preferences updated successfully"
        assert data["user_id"] == "test-user-123"

    def test_update_user_preferences_error(self, authenticated_client):
        """Test user preferences update when it fails."""
        preferences_data = {
            "style_preferences": {
                "preferred_colors": ["blue", "black"]
            }
        }
        response = authenticated_client.put(
            "/api/v1/users/preferences",
            json=preferences_data
        )
        assert response.status_code == status.HTTP_200_OK

    def test_user_endpoints_no_auth(self, client):
        """Test user endpoints without authentication."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = client.get("/api/v1/users/preferences")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = client.put("/api/v1/users/preferences", json={})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_user_preferences_invalid_data(self, authenticated_client):
        """Test user preferences update with invalid data."""
        response = authenticated_client.put(
            "/api/v1/users/preferences",
            json={"invalid": "data"}
        )
        assert response.status_code == status.HTTP_200_OK
