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
Tests for the TravelOrchestratorService.
"""

from unittest.mock import AsyncMock, patch

import pytest
from app.models.responses import ChatResponse, ConversationContext
from app.services.currency import CurrencyService
from app.services.openai.openai_service import openai_service
from app.services.orchestrator import TravelOrchestratorService, orchestrator_service
from app.services.qloo import qloo_service
from app.services.weather import weather_service


@pytest.mark.asyncio
async def test_generate_travel_recommendations_success():
    """Test successful travel recommendations generation."""
    with (
        patch.object(
            qloo_service, "get_cultural_insights", new=AsyncMock(return_value={"insights": "data"})
        ),
        patch.object(
            weather_service, "get_weather_data", new=AsyncMock(return_value={"weather": "data"})
        ),
        patch.object(
            qloo_service, "get_style_recommendations", new=AsyncMock(return_value={"style": "data"})
        ),
        patch.object(
            CurrencyService, "get_exchange_rates", new=AsyncMock(return_value={"USD": 1.0})
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(
                return_value=ChatResponse(
                    message="Here are your recommendations", confidence_score=0.8
                )
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I want to go to Paris",
            ConversationContext(
                user_id="user-1",
                destination="Paris",
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            {"id": "user-1", "home_currency": "USD"},
        )
        assert result.confidence_score == 0.8
        assert "Here are your recommendations" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_error():
    """Test travel recommendations generation with API errors."""
    with (
        patch.object(qloo_service, "get_cultural_insights", new=AsyncMock(return_value=None)),
        patch.object(weather_service, "get_weather_data", new=AsyncMock(return_value=None)),
        patch.object(qloo_service, "get_style_recommendations", new=AsyncMock(return_value=None)),
        patch.object(
            CurrencyService, "get_exchange_rates", new=AsyncMock(return_value={"USD": 1.0})
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(
                return_value=ChatResponse(
                    message="Here are your recommendations", confidence_score=0.8
                )
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I want to go to Paris",
            ConversationContext(
                user_id="user-1",
                destination="Paris",
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            {"id": "user-1", "home_currency": "USD"},
        )
        assert result.confidence_score == 0.8
        assert "Here are your recommendations" in result.message


def test_parse_trip_context():
    """Test trip context parsing."""
    orchestrator = TravelOrchestratorService()

    # Test destination extraction
    context = orchestrator._parse_trip_context(
        "I'm going to Tokyo next week", ConversationContext(user_id="user-1")
    )
    assert context.get("destination") == "Tokyo"

    # Test business context
    context = orchestrator._parse_trip_context(
        "Business trip to London", ConversationContext(user_id="user-1")
    )
    assert context.get("trip_purpose") == "business"


def test_enhance_response():
    """Test response enhancement."""
    orchestrator = TravelOrchestratorService()

    original_response = ChatResponse(message="Test response", confidence_score=0.5)
    context = {"destination": "Paris", "weather": "sunny"}

    enhanced = orchestrator._enhance_response(original_response, context)
    assert enhanced.message == "Test response"
    assert enhanced.confidence_score == 0.5


@pytest.mark.asyncio
async def test_generate_travel_recommendations_orchestration_error():
    """Test orchestration error handling."""
    with (
        patch.object(
            qloo_service, "get_cultural_insights", new=AsyncMock(side_effect=Exception("API Error"))
        ),
        patch.object(weather_service, "get_weather_data", new=AsyncMock(return_value=None)),
        patch.object(qloo_service, "get_style_recommendations", new=AsyncMock(return_value=None)),
        patch.object(CurrencyService, "get_exchange_rates", new=AsyncMock(return_value=None)),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(
                return_value=ChatResponse(
                    message="Here are your recommendations", confidence_score=0.8
                )
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I want to go to Paris",
            ConversationContext(user_id="user-1"),
            [],
            {"id": "user-1"},
        )
        assert result.confidence_score == 0.8


@pytest.mark.asyncio
async def test_safe_api_call_exception():
    """Test safe API call with exception."""
    orchestrator = TravelOrchestratorService()

    async def failing_api():
        raise Exception("API Error")

    result = await orchestrator._safe_api_call(failing_api)
    assert result is None


@pytest.mark.asyncio
async def test_parse_trip_context_destination_extraction():
    """Test destination extraction from various message patterns."""
    orchestrator = TravelOrchestratorService()

    # Test "going to" pattern
    context = orchestrator._parse_trip_context(
        "I'm going to Tokyo next week", ConversationContext(user_id="user-1")
    )
    assert context.get("destination") == "Tokyo"

    # Test "visiting" pattern
    context = orchestrator._parse_trip_context(
        "I'm visiting London for business", ConversationContext(user_id="user-1")
    )
    assert context.get("destination") == "London"

    # Test "in" pattern
    context = orchestrator._parse_trip_context(
        "I'll be in Paris for 5 days", ConversationContext(user_id="user-1")
    )
    assert context.get("destination") == "Paris"


@pytest.mark.asyncio
async def test_parse_trip_context_destination_extraction_visiting():
    """Test destination extraction with 'visiting' keyword."""
    orchestrator = TravelOrchestratorService()

    context = orchestrator._parse_trip_context(
        "I'm visiting New York for vacation", ConversationContext(user_id="user-1")
    )
    assert context.get("destination") == "New York"


@pytest.mark.asyncio
async def test_parse_trip_context_destination_extraction_in():
    """Test destination extraction with 'in' keyword."""
    orchestrator = TravelOrchestratorService()

    context = orchestrator._parse_trip_context(
        "I'll be in Tokyo for 3 days", ConversationContext(user_id="user-1")
    )
    assert context.get("destination") == "Tokyo"


@pytest.mark.asyncio
async def test_parse_trip_context_business_context():
    """Test business context detection."""
    orchestrator = TravelOrchestratorService()

    context = orchestrator._parse_trip_context(
        "Business trip to London", ConversationContext(user_id="user-1")
    )
    assert context.get("trip_purpose") == "business"

    context = orchestrator._parse_trip_context(
        "Work trip to Tokyo", ConversationContext(user_id="user-1")
    )
    assert context.get("trip_purpose") == "business"


@pytest.mark.asyncio
async def test_parse_trip_context_formal_context():
    """Test formal context detection."""
    orchestrator = TravelOrchestratorService()

    context = orchestrator._parse_trip_context(
        "Formal event in Paris", ConversationContext(user_id="user-1")
    )
    assert context.get("trip_purpose") == "formal"

    context = orchestrator._parse_trip_context(
        "Wedding in Rome", ConversationContext(user_id="user-1")
    )
    assert context.get("trip_purpose") == "formal"


@pytest.mark.asyncio
async def test_parse_trip_context_active_context():
    """Test active context detection."""
    orchestrator = TravelOrchestratorService()

    context = orchestrator._parse_trip_context(
        "Hiking trip to Switzerland", ConversationContext(user_id="user-1")
    )
    assert context.get("trip_purpose") == "active"

    context = orchestrator._parse_trip_context(
        "Skiing in Austria", ConversationContext(user_id="user-1")
    )
    assert context.get("trip_purpose") == "active"


@pytest.mark.asyncio
async def test_enhance_response_with_all_context():
    """Test response enhancement with full context."""
    orchestrator = TravelOrchestratorService()

    original_response = ChatResponse(message="Test response", confidence_score=0.5)
    context = {
        "destination": "Paris",
        "weather": "sunny",
        "cultural_insights": {"dress_code": "casual"},
        "user_profile": {"style_preferences": "modern"},
    }

    enhanced = orchestrator._enhance_response(original_response, context)
    assert enhanced.message == "Test response"
    assert enhanced.confidence_score == 0.5


@pytest.mark.asyncio
async def test_enhance_response_with_partial_context():
    """Test response enhancement with partial context."""
    orchestrator = TravelOrchestratorService()

    original_response = ChatResponse(message="Test response", confidence_score=0.5)
    context = {"destination": "Tokyo", "weather": "rainy"}

    enhanced = orchestrator._enhance_response(original_response, context)
    assert enhanced.message == "Test response"
    assert enhanced.confidence_score == 0.5


@pytest.mark.asyncio
async def test_enhance_response_with_no_destination():
    """Test response enhancement without destination."""
    orchestrator = TravelOrchestratorService()

    original_response = ChatResponse(message="Test response", confidence_score=0.5)
    context = {"weather": "sunny", "cultural_insights": {"dress_code": "casual"}}

    enhanced = orchestrator._enhance_response(original_response, context)
    assert enhanced.message == "Test response"
    assert enhanced.confidence_score == 0.5


@pytest.mark.asyncio
async def test_generate_travel_recommendations_no_destination():
    """Test travel recommendations without destination."""
    with (
        patch.object(qloo_service, "get_cultural_insights", new=AsyncMock(return_value=None)),
        patch.object(weather_service, "get_weather_data", new=AsyncMock(return_value=None)),
        patch.object(qloo_service, "get_style_recommendations", new=AsyncMock(return_value=None)),
        patch.object(CurrencyService, "get_exchange_rates", new=AsyncMock(return_value=None)),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(
                return_value=ChatResponse(
                    message="Please specify a destination", confidence_score=0.8
                )
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I need packing advice",
            ConversationContext(user_id="user-1"),
            [],
            {"id": "user-1"},
        )
        assert result.confidence_score == 0.8
        assert "Please specify a destination" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_no_user_profile():
    """Test travel recommendations without user profile."""
    with (
        patch.object(
            qloo_service, "get_cultural_insights", new=AsyncMock(return_value={"insights": "data"})
        ),
        patch.object(
            weather_service, "get_weather_data", new=AsyncMock(return_value={"weather": "data"})
        ),
        patch.object(
            qloo_service, "get_style_recommendations", new=AsyncMock(return_value={"style": "data"})
        ),
        patch.object(
            CurrencyService, "get_exchange_rates", new=AsyncMock(return_value={"USD": 1.0})
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(
                return_value=ChatResponse(
                    message="Here are your recommendations", confidence_score=0.8
                )
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I want to go to Paris",
            ConversationContext(
                user_id="user-1",
                destination="Paris",
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            None,  # No user profile
        )
        assert result.confidence_score == 0.8
        assert "Here are your recommendations" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_currency_request_with_amount():
    """Test currency request handling with amount."""
    with (
        patch.object(CurrencyService, "is_currency_request", return_value=True),
        patch.object(
            CurrencyService,
            "handle_currency_help_request",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            CurrencyService,
            "handle_currency_request",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "request_type": "conversion",
                    "data": {
                        "original": {"amount": 100, "currency": "USD"},
                        "converted": {"amount": 85, "currency": "EUR"},
                        "rate": 0.85,
                    },
                }
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "Convert 100 USD to EUR",
            ConversationContext(user_id="user-1"),
            [],
            {"id": "user-1"},
        )
        assert result.confidence_score == 0.9
        assert "100.00 USD = 85.00 EUR" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_currency_request_without_amount():
    """Test currency request handling without amount."""
    with (
        patch.object(CurrencyService, "is_currency_request", return_value=True),
        patch.object(
            CurrencyService,
            "handle_currency_help_request",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            CurrencyService,
            "handle_currency_request",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "request_type": "rate",
                    "data": {"base_currency": "USD", "target_currency": "EUR", "rate": 0.85},
                }
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "What's the USD to EUR rate?",
            ConversationContext(user_id="user-1"),
            [],
            {"id": "user-1"},
        )
        assert result.confidence_score == 0.9
        assert "Exchange rate: 1 USD = 0.8500 EUR" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_currency_request_non_rate_type():
    """Test currency request handling with non-rate type."""
    with (
        patch.object(CurrencyService, "is_currency_request", return_value=True),
        patch.object(
            CurrencyService,
            "handle_currency_help_request",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            CurrencyService,
            "handle_currency_request",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "request_type": "unknown",
                    "data": {
                        "original": {"amount": 100, "currency": "USD"},
                        "converted": {"amount": 85, "currency": "EUR"},
                        "rate": 0.85,
                    },
                }
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "Convert 100 USD to EUR",
            ConversationContext(user_id="user-1"),
            [],
            {"id": "user-1"},
        )
        assert result.confidence_score == 0.9
        assert "100.00 USD = 85.00 EUR" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_exception_handling():
    """Test exception handling in travel recommendations."""
    with (
        patch.object(
            qloo_service, "get_cultural_insights", new=AsyncMock(side_effect=Exception("API Error"))
        ),
        patch.object(
            weather_service,
            "get_weather_data",
            new=AsyncMock(side_effect=Exception("Weather API Error")),
        ),
        patch.object(
            qloo_service,
            "get_style_recommendations",
            new=AsyncMock(side_effect=Exception("Style API Error")),
        ),
        patch.object(
            CurrencyService,
            "get_exchange_rates",
            new=AsyncMock(side_effect=Exception("Currency API Error")),
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(
                return_value=ChatResponse(
                    message="Here are your recommendations", confidence_score=0.8
                )
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I want to go to Paris",
            ConversationContext(user_id="user-1"),
            [],
            {"id": "user-1"},
        )
        assert result.confidence_score == 0.8
        assert "Here are your recommendations" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_exception_handling_alternative():
    """Test alternative exception handling in travel recommendations."""
    with (
        patch.object(qloo_service, "get_cultural_insights", new=AsyncMock(return_value=None)),
        patch.object(weather_service, "get_weather_data", new=AsyncMock(return_value=None)),
        patch.object(qloo_service, "get_style_recommendations", new=AsyncMock(return_value=None)),
        patch.object(CurrencyService, "get_exchange_rates", new=AsyncMock(return_value=None)),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(side_effect=Exception("OpenAI error")),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I want to go to Paris",
            ConversationContext(user_id="user-1"),
            [],
            {"id": "user-1"},
        )
        # Should return a fallback response
        assert result is not None
        assert hasattr(result, "message")


@pytest.mark.asyncio
async def test_return_none_helper():
    """Test the _return_none helper method."""
    orchestrator = TravelOrchestratorService()
    result = await orchestrator._return_none()
    assert result is None
