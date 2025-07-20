"""
Tests for user models validation.
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
from pydantic import ValidationError


def test_user_profile_creation():
    """Test user profile creation with valid data."""
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
    """Test user profile email validation."""
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        UserProfile(id="user-2", email="not-an-email", created_at=now, updated_at=now)


def test_user_preferences_defaults():
    """Test user preferences default values."""
    now = datetime.now(UTC)
    prefs = UserPreferences(user_id="user-1", created_at=now, updated_at=now)
    assert prefs.style_preferences is None
    assert prefs.size_info is None
    assert prefs.travel_patterns is None
    assert prefs.preferred_packing_methods is None
    assert prefs.budget_preferences is None
    assert prefs.climate_preferences is None


def test_user_auth_token_defaults():
    """Test user auth token default values."""
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
    """Test user activity creation."""
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
    """Test user session default values."""
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
    """Test user feedback rating validation bounds."""
    now = datetime.now(UTC)
    # Valid rating
    UserFeedback(
        feedback_id="fb-1", user_id="user-1", recommendation_id="rec-1", rating=5, created_at=now
    )
    # Invalid rating - too low
    with pytest.raises(ValidationError):
        UserFeedback(
            feedback_id="fb-2",
            user_id="user-1",
            recommendation_id="rec-1",
            rating=0,
            created_at=now,
        )
    # Invalid rating - too high
    with pytest.raises(ValidationError):
        UserFeedback(
            feedback_id="fb-3",
            user_id="user-1",
            recommendation_id="rec-1",
            rating=6,
            created_at=now,
        )


def test_user_usage_stats_defaults():
    """Test user usage stats default values."""
    now = datetime.now(UTC)
    stats = UserUsageStats(user_id="user-1", created_at=now, updated_at=now)
    assert stats.total_chat_sessions == 0
    assert stats.total_recommendations == 0
    assert stats.total_currency_conversions == 0
    assert stats.favorite_destinations is None
    assert stats.most_used_packing_method is None
    assert stats.last_activity is None
