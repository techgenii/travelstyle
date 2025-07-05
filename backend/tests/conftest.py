"""
Pytest configuration and fixtures for TravelStyle AI backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.core.config import settings

@pytest.fixture
def client():
    """Test client for FastAPI application."""
    return TestClient(app)

@pytest.fixture
def mock_user():
    """Mock user data for testing."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "is_active": True,
        "aud": "authenticated",
        "exp": 1234567890,
        "iat": 1234567890
    }

@pytest.fixture
def mock_auth_headers(mock_user):
    """Mock authentication headers."""
    return {"Authorization": "Bearer mock-jwt-token"}

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
            "trip_purpose": "leisure"
        }
    }

@pytest.fixture
def mock_recommendation_response():
    """Mock recommendation response data."""
    return {
        "message": "Here are your packing recommendations for Paris...",
        "quick_replies": [
            {"text": "Show me cultural insights", "action": "cultural"},
            {"text": "What's the weather like?", "action": "weather"}
        ],
        "suggestions": ["Pack layers", "Include comfortable walking shoes"],
        "confidence_score": 0.85,
        "timestamp": "2024-01-01T12:00:00Z"
    } 