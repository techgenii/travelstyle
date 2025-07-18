from unittest.mock import Mock, patch

import pytest
from app.api.v1.user import get_current_user_profile, get_user_preferences, update_user_preferences
from fastapi import HTTPException


@pytest.fixture
def mock_current_user():
    return {"id": "user-123", "email": "test@example.com", "is_active": True}


@pytest.fixture
def mock_current_user_inactive():
    return {"id": "user-123", "email": "test@example.com", "is_active": False}


@pytest.fixture
def mock_current_user_minimal():
    return {
        "id": "user-123"
        # Missing email and is_active
    }


@pytest.mark.asyncio
async def test_get_current_user_profile_success(mock_current_user):
    result = await get_current_user_profile(mock_current_user)
    assert result["id"] == "user-123"
    assert result["email"] == "test@example.com"
    assert result["is_active"] is True


@pytest.mark.asyncio
async def test_get_current_user_profile_inactive(mock_current_user_inactive):
    result = await get_current_user_profile(mock_current_user_inactive)
    assert result["id"] == "user-123"
    assert result["email"] == "test@example.com"
    assert result["is_active"] is False


@pytest.mark.asyncio
async def test_get_current_user_profile_minimal(mock_current_user_minimal):
    result = await get_current_user_profile(mock_current_user_minimal)
    assert result["id"] == "user-123"
    assert result["email"] is None
    assert result["is_active"] is True  # Default value


@pytest.mark.asyncio
async def test_get_current_user_profile_exception():
    with patch("app.api.v1.user.logger") as mock_logger:
        # Create a user object that will cause an exception when accessed
        problematic_user = Mock()
        problematic_user.__getitem__ = Mock(side_effect=Exception("Database error"))

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_profile(problematic_user)

        assert exc_info.value.status_code == 500
        assert "Failed to retrieve user profile" in exc_info.value.detail
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_preferences_success():
    result = await get_user_preferences({"id": "user-123"})
    assert "style_preferences" in result
    assert "travel_patterns" in result
    assert "size_info" in result
    assert result["style_preferences"] == {}
    assert result["travel_patterns"] == {}
    assert result["size_info"] == {}


@pytest.mark.asyncio
async def test_update_user_preferences_success(mock_current_user):
    preferences_data = {
        "style_preferences": {"color": "blue"},
        "travel_patterns": {"frequent_destinations": ["Europe"]},
        "size_info": {"height": "5'8\""},
    }

    result = await update_user_preferences(preferences_data, mock_current_user)
    assert result["message"] == "Preferences updated successfully"
    assert result["user_id"] == "user-123"


@pytest.mark.asyncio
async def test_update_user_preferences_empty_preferences(mock_current_user):
    preferences_data = {}

    result = await update_user_preferences(preferences_data, mock_current_user)
    assert result["message"] == "Preferences updated successfully"
    assert result["user_id"] == "user-123"


@pytest.mark.asyncio
async def test_update_user_preferences_missing_user_id():
    preferences_data = {"style_preferences": {"color": "blue"}}
    user_without_id = {"email": "test@example.com"}  # Missing id

    with patch("app.api.v1.user.logger") as mock_logger:
        with pytest.raises(HTTPException) as exc_info:
            await update_user_preferences(preferences_data, user_without_id)

        assert exc_info.value.status_code == 500
        assert "Failed to update user preferences" in exc_info.value.detail
        mock_logger.error.assert_called_once()
