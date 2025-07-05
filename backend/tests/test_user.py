"""
Tests for user API endpoints.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status

class TestUserEndpoints:
    """Test cases for user endpoints."""

    def test_get_current_user_profile_success(self, client, mock_auth_headers):
        """Test successful user profile retrieval."""
        with patch('app.api.v1.user.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            response = client.get(
                "/api/v1/users/me",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "id" in data
            assert "email" in data
            assert "is_active" in data
            assert data["id"] == "test-user-123"
            assert data["email"] == "test@example.com"

    def test_get_current_user_profile_error(self, client, mock_auth_headers):
        """Test user profile retrieval when it fails."""
        with patch('app.api.v1.user.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            # Mock the function to raise an exception
            with patch('app.api.v1.user.get_user_profile') as mock_get_profile:
                mock_get_profile.side_effect = Exception("Database error")
                
                response = client.get(
                    "/api/v1/users/me",
                    headers=mock_auth_headers
                )
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert "Failed to retrieve user profile" in response.json()["detail"]

    def test_get_user_preferences_success(self, client, mock_auth_headers):
        """Test successful user preferences retrieval."""
        with patch('app.api.v1.user.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            response = client.get(
                "/api/v1/users/preferences",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "style_preferences" in data
            assert "travel_patterns" in data
            assert "size_info" in data

    def test_get_user_preferences_error(self, client, mock_auth_headers):
        """Test user preferences retrieval when it fails."""
        with patch('app.api.v1.user.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            # Mock the function to raise an exception
            with patch('app.api.v1.user.get_user_preferences') as mock_get_prefs:
                mock_get_prefs.side_effect = Exception("Database error")
                
                response = client.get(
                    "/api/v1/users/preferences",
                    headers=mock_auth_headers
                )
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert "Failed to retrieve user preferences" in response.json()["detail"]

    def test_update_user_preferences_success(self, client, mock_auth_headers):
        """Test successful user preferences update."""
        with patch('app.api.v1.user.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
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
            
            response = client.put(
                "/api/v1/users/preferences",
                json=preferences_data,
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
            assert "user_id" in data
            assert data["message"] == "Preferences updated successfully"
            assert data["user_id"] == "test-user-123"

    def test_update_user_preferences_error(self, client, mock_auth_headers):
        """Test user preferences update when it fails."""
        with patch('app.api.v1.user.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            preferences_data = {
                "style_preferences": {
                    "preferred_colors": ["blue", "black"]
                }
            }
            
            # Mock the function to raise an exception
            with patch('app.api.v1.user.update_user_preferences') as mock_update_prefs:
                mock_update_prefs.side_effect = Exception("Database error")
                
                response = client.put(
                    "/api/v1/users/preferences",
                    json=preferences_data,
                    headers=mock_auth_headers
                )
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert "Failed to update user preferences" in response.json()["detail"]

    def test_user_endpoints_no_auth(self, client):
        """Test user endpoints without authentication."""
        # Test get current user profile
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test get user preferences
        response = client.get("/api/v1/users/preferences")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test update user preferences
        response = client.put("/api/v1/users/preferences", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_preferences_invalid_data(self, client, mock_auth_headers):
        """Test user preferences update with invalid data."""
        with patch('app.api.v1.user.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            # Test with invalid JSON structure
            response = client.put(
                "/api/v1/users/preferences",
                json={"invalid": "data"},
                headers=mock_auth_headers
            )
            
            # Should still work since the endpoint accepts any Dict[str, Any]
            assert response.status_code == status.HTTP_200_OK 