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
from app.services.currency_conversion_service import currency_conversion_service
from app.services.currency_service import currency_service
from app.services.openai_service import openai_service
from app.services.orchestrator import TravelOrchestratorService, orchestrator_service
from app.services.qloo_service import qloo_service
from app.services.weather_service import weather_service


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
            currency_service, "get_exchange_rates", new=AsyncMock(return_value={"USD": 1.0})
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
            currency_service, "get_exchange_rates", new=AsyncMock(return_value={"USD": 1.0})
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
    context = ConversationContext(
        user_id="user-1",
        destination="Paris",
        travel_dates=["2024-06-01"],
        trip_purpose="leisure",
    )
    trip = orchestrator._parse_trip_context("I'm going to Paris for business", context)
    assert trip["destination"] == "Paris"
    assert trip["context"] == "business"
    assert trip["occasion"] == "business"

    trip2 = orchestrator._parse_trip_context("Let's go hiking in Denver", context)
    assert trip2["context"] == "active"
    assert trip2["occasion"] == "active"


def test_enhance_response():
    """Test response enhancement."""
    orchestrator = TravelOrchestratorService()
    ai_response = ChatResponse(
        message="Here are your travel recommendations",
        confidence_score=0.9,
        quick_replies=[],
        suggestions=[],
    )
    context = {
        "weather_conditions": {"temperature": 25},
        "cultural_intelligence": {"customs": "data"},
        "currency_info": {"rates": "data"},
        "trip_context": {"destination": "Paris"},
    }
    result = orchestrator._enhance_response(ai_response, context)
    assert len(result.quick_replies) == 3
    assert len(result.suggestions) == 3


@pytest.mark.asyncio
async def test_generate_travel_recommendations_orchestration_error():
    """Test orchestration error handling."""
    with patch.object(
        orchestrator_service, "_parse_trip_context", side_effect=Exception("Parse error")
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
        assert result.confidence_score == 0.0
        assert "I apologize, but I'm having trouble processing your request" in result.message


@pytest.mark.asyncio
async def test_safe_api_call_exception():
    """Test safe API call with exception."""
    orchestrator_service = TravelOrchestratorService()

    async def failing_api():
        raise Exception("API error")

    result = await orchestrator_service._safe_api_call(failing_api)
    assert result is None


@pytest.mark.asyncio
async def test_parse_trip_context_destination_extraction():
    """Test destination extraction from message."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1",
        destination=None,
        travel_dates=["2024-06-01"],
        trip_purpose="leisure",
    )
    result = orchestrator_service._parse_trip_context("I want to go to Tokyo", context)
    assert result["destination"] == "Tokyo"


@pytest.mark.asyncio
async def test_parse_trip_context_destination_extraction_visiting():
    """Test destination extraction with 'visiting' keyword."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1",
        destination=None,
        travel_dates=["2024-06-01"],
        trip_purpose="leisure",
    )
    result = orchestrator_service._parse_trip_context("I'm visiting London next week", context)
    assert result["destination"] == "London"


@pytest.mark.asyncio
async def test_parse_trip_context_destination_extraction_in():
    """Test destination extraction with 'in' keyword."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1",
        destination=None,
        travel_dates=["2024-06-01"],
        trip_purpose="leisure",
    )
    result = orchestrator_service._parse_trip_context("I'll be in New York", context)
    assert result["destination"] == "New York"


@pytest.mark.asyncio
async def test_parse_trip_context_business_context():
    """Test business context detection."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1",
        destination="Paris",
        travel_dates=["2024-06-01"],
        trip_purpose="leisure",
    )
    result = orchestrator_service._parse_trip_context("I have a business meeting in Paris", context)
    assert result["context"] == "business"
    assert result["occasion"] == "business"


@pytest.mark.asyncio
async def test_parse_trip_context_formal_context():
    """Test formal context detection."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1",
        destination="Paris",
        travel_dates=["2024-06-01"],
        trip_purpose="leisure",
    )
    result = orchestrator_service._parse_trip_context(
        "I'm attending a formal dinner in Paris", context
    )
    assert result["context"] == "formal"
    assert result["occasion"] == "formal"


@pytest.mark.asyncio
async def test_parse_trip_context_active_context():
    """Test active context detection."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1",
        destination="Switzerland",
        travel_dates=["2024-06-01"],
        trip_purpose="leisure",
    )
    result = orchestrator_service._parse_trip_context("I'm going hiking in Switzerland", context)
    assert result["context"] == "active"
    assert result["occasion"] == "active"


@pytest.mark.asyncio
async def test_enhance_response_with_all_context():
    """Test _enhance_response when all context is available."""
    orchestrator_service = TravelOrchestratorService()
    ai_response = ChatResponse(
        message="Here are your travel recommendations",
        confidence_score=0.9,
        quick_replies=[],
        suggestions=[],
    )

    context = {
        "weather_conditions": {"temperature": 25},
        "cultural_intelligence": {"customs": "data"},
        "currency_info": {"rates": "data"},
        "trip_context": {"destination": "Paris"},
    }

    result = orchestrator_service._enhance_response(ai_response, context)

    # Check that quick replies were added
    quick_reply_texts = [qr.text for qr in result.quick_replies]
    assert "More weather details" in quick_reply_texts
    assert "Cultural tips" in quick_reply_texts
    assert "Currency help" in quick_reply_texts

    # Check that suggestions were added
    assert len(result.suggestions) == 3
    assert "Get packing checklist" in result.suggestions
    assert "Local shopping tips" in result.suggestions
    assert "Emergency contact info" in result.suggestions


@pytest.mark.asyncio
async def test_enhance_response_with_partial_context():
    """Test _enhance_response when only partial context is available."""
    orchestrator_service = TravelOrchestratorService()
    ai_response = ChatResponse(
        message="Here are your travel recommendations",
        confidence_score=0.9,
        quick_replies=[],
        suggestions=[],
    )

    context = {
        "weather_conditions": {"temperature": 25},
        "cultural_intelligence": None,
        "currency_info": {"rates": "data"},
        "trip_context": {"destination": "Paris"},
    }

    result = orchestrator_service._enhance_response(ai_response, context)

    # Check that only available quick replies were added
    quick_reply_texts = [qr.text for qr in result.quick_replies]
    assert "More weather details" in quick_reply_texts
    assert "Cultural tips" not in quick_reply_texts
    assert "Currency help" in quick_reply_texts

    # Check that suggestions were added
    assert len(result.suggestions) == 3


@pytest.mark.asyncio
async def test_enhance_response_with_no_destination():
    """Test _enhance_response when no destination is specified."""
    orchestrator_service = TravelOrchestratorService()
    ai_response = ChatResponse(
        message="Here are your travel recommendations",
        confidence_score=0.9,
        quick_replies=[],
        suggestions=[],
    )

    context = {
        "weather_conditions": {"temperature": 25},
        "cultural_intelligence": {"customs": "data"},
        "currency_info": {"rates": "data"},
        "trip_context": {"destination": None},
    }

    result = orchestrator_service._enhance_response(ai_response, context)

    # Check that quick replies were added
    quick_reply_texts = [qr.text for qr in result.quick_replies]
    assert "More weather details" in quick_reply_texts
    assert "Cultural tips" in quick_reply_texts
    assert "Currency help" in quick_reply_texts

    # Check that no suggestions were added (no destination)
    assert len(result.suggestions) == 0


@pytest.mark.asyncio
async def test_generate_travel_recommendations_no_destination():
    """Test generate_travel_recommendations when no destination is specified."""
    with (
        patch.object(qloo_service, "get_cultural_insights", new=AsyncMock(return_value=None)),
        patch.object(weather_service, "get_weather_data", new=AsyncMock(return_value=None)),
        patch.object(qloo_service, "get_style_recommendations", new=AsyncMock(return_value=None)),
        patch.object(
            currency_service, "get_exchange_rates", new=AsyncMock(return_value={"USD": 1.0})
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
            "I need travel advice",
            ConversationContext(
                user_id="user-1",
                destination=None,
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            {"id": "user-1", "home_currency": "USD"},
        )
        assert result.confidence_score == 0.8
        assert "Here are your recommendations" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_no_user_profile():
    """Test generate_travel_recommendations when no user profile is provided."""
    with (
        patch.object(
            qloo_service, "get_cultural_insights", new=AsyncMock(return_value={"insights": "data"})
        ),
        patch.object(
            weather_service, "get_weather_data", new=AsyncMock(return_value={"weather": "data"})
        ),
        patch.object(
            currency_service, "get_exchange_rates", new=AsyncMock(return_value={"USD": 1.0})
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
    """Test generate_travel_recommendations when it's a currency request with amount > 0."""
    with (
        patch.object(currency_conversion_service, "is_currency_request", return_value=True),
        patch.object(
            currency_conversion_service,
            "handle_currency_request",
            return_value={
                "type": "currency_rate",
                "message": "1 USD = 0.85 EUR",
                "amount": 100.0,
            },
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "Convert 100 USD to EUR",
            ConversationContext(
                user_id="user-1",
                destination="Paris",
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            {"id": "user-1", "home_currency": "USD"},
        )

        assert result.confidence_score == 0.9
        assert "1 USD = 0.85 EUR" in result.message
        assert len(result.quick_replies) == 3

        # Check that the "Show rate only" quick reply was added first (amount > 0)
        assert result.quick_replies[0].text == "Show rate only"
        assert result.quick_replies[0].action == "currency_rate_only"
        assert result.quick_replies[1].text == "Convert different amount"
        assert result.quick_replies[2].text == "Other currencies"


@pytest.mark.asyncio
async def test_generate_travel_recommendations_currency_request_without_amount():
    """Test generate_travel_recommendations when it's a currency request with amount = 0."""
    with (
        patch.object(currency_conversion_service, "is_currency_request", return_value=True),
        patch.object(
            currency_conversion_service,
            "handle_currency_request",
            return_value={
                "type": "currency_rate",
                "message": "1 USD = 0.85 EUR",
                "amount": 0.0,
            },
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "What's the USD to EUR rate?",
            ConversationContext(
                user_id="user-1",
                destination="Paris",
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            {"id": "user-1", "home_currency": "USD"},
        )

        assert result.confidence_score == 0.9
        assert "1 USD = 0.85 EUR" in result.message
        assert len(result.quick_replies) == 2

        # Check that the "Show rate only" quick reply was NOT added (amount = 0)
        quick_reply_texts = [qr.text for qr in result.quick_replies]
        assert "Show rate only" not in quick_reply_texts
        assert "Convert different amount" in quick_reply_texts
        assert "Other currencies" in quick_reply_texts


@pytest.mark.asyncio
async def test_generate_travel_recommendations_currency_request_non_rate_type():
    """Test generate_travel_recommendations when it's a currency request but not rate type."""
    with (
        patch.object(currency_conversion_service, "is_currency_request", return_value=True),
        patch.object(
            currency_conversion_service,
            "handle_currency_request",
            return_value={
                "type": "currency_list",
                "message": "Here are available currencies",
            },
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "Show me available currencies",
            ConversationContext(
                user_id="user-1",
                destination="Paris",
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            {"id": "user-1", "home_currency": "USD"},
        )

        assert result.confidence_score == 0.0
        assert "Here are available currencies" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_exception_handling():
    """Test generate_travel_recommendations when an exception occurs."""
    with (
        patch.object(currency_conversion_service, "is_currency_request", return_value=False),
        patch.object(
            orchestrator_service, "_parse_trip_context", side_effect=Exception("Parse error")
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

        assert result.confidence_score == 0.0
        assert "I apologize, but I'm having trouble processing your request" in result.message
        assert "Please try again or be more specific about your travel plans" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_exception_handling_alternative():
    """Test generate_travel_recommendations when an exception occurs in a different way."""
    with (
        patch.object(currency_conversion_service, "is_currency_request", return_value=False),
        patch.object(openai_service, "generate_response", side_effect=Exception("OpenAI error")),
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

        assert result.confidence_score == 0.0
        assert "I apologize, but I'm having trouble processing your request" in result.message
        assert "Please try again or be more specific about your travel plans" in result.message


@pytest.mark.asyncio
async def test_return_none_helper():
    """Test the _return_none helper method."""
    result = await orchestrator_service._return_none()
    assert result is None
