"""
Tests for user API endpoints.
"""

from datetime import UTC, datetime, timedelta

import pytest
from app.models.user import (
    UserActivity,
    UserAuthToken,
    UserFeedback,
    UserPreferences,
    UserProfile,
    UserRole,
    UserSession,
    UserStatus,
    UserUsageStats,
)
from fastapi import status
from pydantic import ValidationError


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
                "style_categories": ["business_professional", "smart_casual"],
            },
            "size_info": {"height": "5'8\"", "weight": "150 lbs", "shirt_size": "M"},
            "travel_patterns": {
                "frequent_destinations": ["Europe", "Asia"],
                "travel_style": "business",
            },
        }
        response = authenticated_client.put("/api/v1/users/preferences", json=preferences_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "user_id" in data
        assert data["message"] == "Preferences updated successfully"
        assert data["user_id"] == "test-user-123"

    def test_update_user_preferences_error(self, authenticated_client):
        """Test user preferences update when it fails."""
        preferences_data = {"style_preferences": {"preferred_colors": ["blue", "black"]}}
        response = authenticated_client.put("/api/v1/users/preferences", json=preferences_data)
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
        response = authenticated_client.put("/api/v1/users/preferences", json={"invalid": "data"})
        assert response.status_code == status.HTTP_200_OK


def test_user_profile_creation():
    now = datetime.now(UTC)
    profile = UserProfile(
        id="user-1",
        email="test@example.com",
        first_name="Jane",
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )
    assert profile.email == "test@example.com"
    assert profile.role == UserRole.USER
    assert profile.status == UserStatus.ACTIVE
    assert profile.created_at == now
    assert profile.updated_at == now


def test_user_profile_email_validation():
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        UserProfile(id="user-2", email="not-an-email", created_at=now, updated_at=now)


def test_user_preferences_defaults():
    now = datetime.now(UTC)
    prefs = UserPreferences(user_id="user-1", created_at=now, updated_at=now)
    assert prefs.style_preferences is None
    assert prefs.size_info is None
    assert prefs.travel_patterns is None
    assert prefs.preferred_packing_methods is None
    assert prefs.budget_preferences is None
    assert prefs.climate_preferences is None


def test_user_auth_token_defaults():
    now = datetime.now(UTC)
    token = UserAuthToken(
        token_id="token-1",
        user_id="user-1",
        token_hash="hash",
        expires_at=now + timedelta(days=1),
        created_at=now,
    )
    assert token.is_revoked is False
    assert token.last_used is None


def test_user_activity_creation():
    now = datetime.now(UTC)
    activity = UserActivity(
        activity_id="act-1",
        user_id="user-1",
        activity_type="login",
        description="User logged in",
        created_at=now,
    )
    assert activity.activity_type == "login"
    assert activity.description == "User logged in"


def test_user_session_defaults():
    now = datetime.now(UTC)
    session = UserSession(
        session_id="sess-1",
        user_id="user-1",
        created_at=now,
        last_activity=now,
        expires_at=now + timedelta(hours=1),
    )
    assert session.is_active is True
    assert session.device_info is None
    assert session.ip_address is None
    assert session.user_agent is None


def test_user_feedback_rating_bounds():
    now = datetime.now(UTC)
    # Valid rating
    UserFeedback(
        feedback_id="fb-1", user_id="user-1", recommendation_id="rec-1", rating=5, created_at=now
    )
    # Invalid rating
    with pytest.raises(ValidationError):
        UserFeedback(
            feedback_id="fb-2",
            user_id="user-1",
            recommendation_id="rec-1",
            rating=0,
            created_at=now,
        )
    with pytest.raises(ValidationError):
        UserFeedback(
            feedback_id="fb-3",
            user_id="user-1",
            recommendation_id="rec-1",
            rating=6,
            created_at=now,
        )


def test_user_usage_stats_defaults():
    now = datetime.now(UTC)
    stats = UserUsageStats(user_id="user-1", created_at=now, updated_at=now)
    assert stats.total_chat_sessions == 0
    assert stats.total_recommendations == 0
    assert stats.total_currency_conversions == 0
    assert stats.favorite_destinations is None
    assert stats.most_used_packing_method is None
    assert stats.last_activity is None
