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
Pytest configuration and fixtures for TravelStyle AI backend tests.
"""

import pytest
from app.main import app
from fastapi.testclient import TestClient


# Override the authentication dependency for testing
async def override_get_current_user():
    """Override authentication dependency for testing."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "is_active": True,
        "aud": "authenticated",
        "exp": 1234567890,
        "iat": 1234567890,
    }


# Apply the override to the app
app.dependency_overrides = {}


@pytest.fixture
def client():
    """Test client for FastAPI application."""
    return TestClient(app)


@pytest.fixture
def authenticated_client():
    """Test client with authentication overridden."""
    from app.api.deps import get_current_user  # pylint: disable=import-outside-toplevel

    app.dependency_overrides[get_current_user] = override_get_current_user
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    """Mock user data for testing."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "is_active": True,
        "aud": "authenticated",
        "exp": 1234567890,
        "iat": 1234567890,
    }


@pytest.fixture
def mock_auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer mock-jwt-token"}


@pytest.fixture
def mock_authenticated_user():
    """Mock authenticated user for dependency injection."""

    async def _mock_get_current_user():
        return {"id": "test-user-123", "email": "test@example.com", "is_active": True}

    return _mock_get_current_user


@pytest.fixture
def mock_chat_request():
    """Mock chat request data."""
    return {
        "message": "I'm going to Paris for a week. What should I pack?",
        "conversation_id": "test-conversation-123",
        "context": {
            "user_id": "test-user-123",
            "destination": "Paris",
            "travel_dates": ["2024-06-01", "2024-06-07"],
            "trip_purpose": "leisure",
        },
    }


@pytest.fixture
def mock_recommendation_response():
    """Mock recommendation response data."""
    return {
        "message": "Here are your packing recommendations for Paris...",
        "quick_replies": [
            {"text": "Show me cultural insights", "action": "cultural"},
            {"text": "What's the weather like?", "action": "weather"},
        ],
        "suggestions": ["Pack layers", "Include comfortable walking shoes"],
        "confidence_score": 0.85,
        "timestamp": "2024-01-01T12:00:00Z",
    }
