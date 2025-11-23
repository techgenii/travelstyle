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
Additional tests for TravelOrchestratorService handlers, routing, and AI classification functionality.
"""

from unittest.mock import AsyncMock, patch

import pytest
from app.models.responses import ChatResponse, ConversationContext
from app.services.openai.openai_service import openai_service
from app.services.orchestrator import TravelOrchestratorService
from app.services.qloo import qloo_service
from app.services.weather import weather_service


@pytest.fixture
def orchestrator() -> TravelOrchestratorService:
    return TravelOrchestratorService()


@pytest.fixture
def base_context() -> ConversationContext:
    return ConversationContext(user_id="u1")


# ---- route_message ----


@pytest.mark.asyncio
async def test_route_message_exception_returns_fallback(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    with patch.object(orchestrator, "_classify_message", side_effect=Exception("boom")):
        result = await orchestrator.route_message("hello", base_context, [], None)
        assert isinstance(result, ChatResponse)
        assert result.confidence_score == 0.0
        assert "I apologize" in result.message


@pytest.mark.asyncio
async def test_route_message_cultural_routing(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    with (
        patch.object(orchestrator, "_classify_message", new=AsyncMock(return_value="cultural")),
        patch.object(
            orchestrator,
            "_handle_cultural_request",
            new=AsyncMock(return_value=ChatResponse(message="cultural", confidence_score=0.8)),
        ),
    ):
        res = await orchestrator.route_message("cultural tips", base_context, [], None)
        assert res.message == "cultural"


@pytest.mark.asyncio
async def test_route_message_logistics_routing(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    with (
        patch.object(orchestrator, "_classify_message", new=AsyncMock(return_value="logistics")),
        patch.object(
            orchestrator,
            "_handle_logistics_request",
            new=AsyncMock(return_value=ChatResponse(message="logistics", confidence_score=0.8)),
        ),
    ):
        res = await orchestrator.route_message("plan my trip", base_context, [], None)
        assert res.message == "logistics"


# ---- currency handler ----


@pytest.mark.asyncio
async def test_handle_currency_help_request_with_quick_replies(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    help_resp = {
        "message": "Here is help",
        "quick_replies": [
            {"text": "Convert different amount", "action": "currency_convert"},
            {"text": "Other currencies", "action": "currency_list"},
        ],
    }
    with (
        patch.object(
            orchestrator.currency_service,
            "handle_currency_help_request",
            new=AsyncMock(return_value=help_resp),
        ),
        patch.object(
            orchestrator.currency_service,
            "handle_currency_request",
            new=AsyncMock(return_value=None),
        ),
    ):
        res = await orchestrator._handle_currency_request("help currency", base_context)
        assert res.message == "Here is help"
        assert res.confidence_score == 0.9
        assert len(res.quick_replies) == 2
        assert res.quick_replies[0].text == "Convert different amount"
        assert res.quick_replies[0].action == "currency_convert"


@pytest.mark.asyncio
async def test_handle_currency_invalid_data_format(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    with (
        patch.object(
            orchestrator.currency_service,
            "handle_currency_help_request",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            orchestrator.currency_service,
            "handle_currency_request",
            new=AsyncMock(return_value={"success": True, "data": [1, 2, 3]}),
        ),
    ):
        res = await orchestrator._handle_currency_request("convert", base_context)
        assert res.confidence_score == 0.0
        assert "couldn't process" in res.message.lower()


@pytest.mark.asyncio
async def test_handle_currency_failure_path(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    with (
        patch.object(
            orchestrator.currency_service,
            "handle_currency_help_request",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            orchestrator.currency_service,
            "handle_currency_request",
            new=AsyncMock(return_value={"success": False}),
        ),
    ):
        res = await orchestrator._handle_currency_request("convert", base_context)
        assert res.confidence_score == 0.0


# ---- weather handler ----


@pytest.mark.asyncio
async def test_handle_weather_missing_destination(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    res = await orchestrator._handle_weather_request("how is weather?", base_context)
    assert res.confidence_score == 0.0
    assert "specify a destination" in res.message.lower()
    assert len(res.quick_replies) == 3


@pytest.mark.asyncio
async def test_handle_weather_with_data(orchestrator: TravelOrchestratorService):
    ctx = ConversationContext(user_id="u1", destination="Paris")
    with patch.object(
        weather_service, "get_weather_data", new=AsyncMock(return_value={"description": "Sunny"})
    ):
        res = await orchestrator._handle_weather_request("weather in paris", ctx)
        assert res.confidence_score == 0.8
        assert "weather for paris" in res.message.lower()


# ---- cultural handler ----


@pytest.mark.asyncio
async def test_handle_cultural_missing_destination(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    res = await orchestrator._handle_cultural_request("tell me culture", base_context)
    assert res.confidence_score == 0.0
    assert "specify a destination" in res.message.lower()


@pytest.mark.asyncio
async def test_handle_cultural_with_and_without_data(orchestrator: TravelOrchestratorService):
    ctx = ConversationContext(user_id="u1", destination="Japan", trip_purpose="leisure")
    with patch.object(
        qloo_service, "get_cultural_insights", new=AsyncMock(return_value={"summary": "Be polite"})
    ):
        res = await orchestrator._handle_cultural_request("cultural", ctx)
        assert res.confidence_score == 0.8
        assert "cultural insights for japan" in res.message.lower()

    with patch.object(qloo_service, "get_cultural_insights", new=AsyncMock(return_value=None)):
        res2 = await orchestrator._handle_cultural_request("cultural", ctx)
        assert res2.confidence_score == 0.8
        assert "couldn't get cultural information" in res2.message.lower()


# ---- wardrobe handler ----


@pytest.mark.asyncio
async def test_handle_wardrobe_basic(orchestrator: TravelOrchestratorService):
    ctx = ConversationContext(user_id="u1", destination="Paris")
    with (
        patch.object(
            weather_service,
            "get_weather_data",
            new=AsyncMock(return_value={"description": "Cloudy"}),
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(return_value=ChatResponse(message="wardrobe", confidence_score=0.77)),
        ),
    ):
        res = await orchestrator._handle_wardrobe_request("what to wear", ctx, [], {"id": "u1"})
        assert res.message == "wardrobe"
        assert res.confidence_score == 0.77
        # 3 wardrobe quick replies
        assert len(res.quick_replies) == 3


# ---- style handler ----


@pytest.mark.asyncio
async def test_handle_style_basic(orchestrator: TravelOrchestratorService):
    ctx = ConversationContext(user_id="u1", destination="Rome", trip_purpose="leisure")
    with (
        patch.object(
            qloo_service, "get_cultural_insights", new=AsyncMock(return_value={"dress": "casual"})
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(return_value=ChatResponse(message="style", confidence_score=0.66)),
        ),
    ):
        res = await orchestrator._handle_style_request("dress code", ctx, [], {"id": "u1"})
        assert res.message == "style"
        assert res.confidence_score == 0.66
        assert len(res.quick_replies) == 3


# ---- destination handler ----


@pytest.mark.asyncio
async def test_handle_destination_missing_destination(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    res = await orchestrator._handle_destination_request("tell me about", base_context, [], None)
    assert res.confidence_score == 0.0
    assert "specify a destination" in res.message.lower()
    assert len(res.quick_replies) == 3


@pytest.mark.asyncio
async def test_handle_destination_with_data(orchestrator: TravelOrchestratorService):
    ctx = ConversationContext(user_id="u1", destination="Tokyo", trip_purpose="leisure")
    with (
        patch.object(
            weather_service,
            "get_weather_data",
            new=AsyncMock(return_value={"description": "Rainy"}),
        ),
        patch.object(
            qloo_service,
            "get_cultural_insights",
            new=AsyncMock(return_value={"summary": "Respectful"}),
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(return_value=ChatResponse(message="dest", confidence_score=0.9)),
        ),
    ):
        res = await orchestrator._handle_destination_request("tell me", ctx, [], {"id": "u1"})
        assert res.message == "dest"
        assert any(q.text.lower().startswith("more about tokyo") for q in res.quick_replies)
        assert any("weather in tokyo" == q.text.lower() for q in res.quick_replies)


# ---- logistics handler ----


@pytest.mark.asyncio
async def test_handle_logistics_with_dates_extraction(orchestrator: TravelOrchestratorService):
    message = "Trip from 2025-09-02 to 2025-09-09 for London"
    ctx = ConversationContext(user_id="u1", destination="London")
    with (
        patch.object(
            weather_service, "get_weather_data", new=AsyncMock(return_value={"description": "Mild"})
        ),
        patch.object(
            qloo_service,
            "get_cultural_insights",
            new=AsyncMock(return_value={"summary": "Queueing"}),
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(return_value=ChatResponse(message="log", confidence_score=0.75)),
        ),
    ):
        res = await orchestrator._handle_logistics_request(message, ctx, [], {"id": "u1"})
        assert res.message == "log"
        assert len(res.quick_replies) == 4


@pytest.mark.asyncio
async def test_handle_logistics_no_destination_nor_dates(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    with patch.object(
        openai_service,
        "generate_response",
        new=AsyncMock(return_value=ChatResponse(message="ok", confidence_score=0.5)),
    ):
        res = await orchestrator._handle_logistics_request("just planning", base_context, [], None)
        assert res.message == "ok"
        assert len(res.quick_replies) == 4


# ---- general handler ----


@pytest.mark.asyncio
async def test_handle_general_success_and_enhancement(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    # safe api calls return data
    with (
        patch.object(
            qloo_service, "get_cultural_insights", new=AsyncMock(return_value={"summary": "tips"})
        ),
        patch.object(
            weather_service,
            "get_weather_data",
            new=AsyncMock(return_value={"description": "sunny"}),
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(return_value=ChatResponse(message="resp", confidence_score=0.88)),
        ),
    ):
        res = await orchestrator._handle_general_request(
            "Going to Tokyo for business", base_context, [], None
        )
        assert res.message == "resp"
        # Enhancement should add at least one quick reply when destination parsed
        assert any(q.text.lower().startswith("more about") for q in res.quick_replies)


@pytest.mark.asyncio
async def test_handle_general_exception_fallback(
    orchestrator: TravelOrchestratorService, base_context: ConversationContext
):
    with patch.object(
        openai_service, "generate_response", new=AsyncMock(side_effect=Exception("oops"))
    ):
        res = await orchestrator._handle_general_request("hello", base_context, [], None)
        assert res.confidence_score == 0.0
        assert "couldn't process" in res.message.lower()


# ---- parse_trip_context fallbacks ----


def test_parse_trip_context_uses_context_fallbacks(orchestrator: TravelOrchestratorService):
    ctx = ConversationContext(
        user_id="u1",
        destination="Zurich",
        travel_dates=["2025-01-01", "2025-01-05"],
        trip_purpose="leisure",
    )
    out = orchestrator._parse_trip_context("Hello only", ctx)
    assert out["destination"] == "Zurich"
    assert out["travel_dates"] == ["2025-01-01", "2025-01-05"]
    assert out["trip_purpose"] == "leisure"


# ---- Routing Tests ----


class TestOrchestratorRouting:
    """Test the routing functionality of the orchestrator."""

    def test_determine_message_type_currency(self, orchestrator):
        """Test that currency messages are correctly identified."""
        assert orchestrator._determine_message_type("Convert USD to EUR") == "currency"
        assert orchestrator._determine_message_type("What's the exchange rate?") == "currency"
        assert orchestrator._determine_message_type("currency_convert") == "currency"

    def test_determine_message_type_weather(self, orchestrator):
        """Test that weather messages are correctly identified."""
        assert orchestrator._determine_message_type("What's the weather like?") == "weather"
        assert orchestrator._determine_message_type("weather_info") == "weather"
        assert orchestrator._determine_message_type("Temperature forecast") == "weather"

    def test_determine_message_type_wardrobe(self, orchestrator):
        """Test that wardrobe messages are correctly identified."""
        assert orchestrator._determine_message_type("What should I pack?") == "wardrobe"
        assert orchestrator._determine_message_type("wardrobe_planning") == "wardrobe"
        assert orchestrator._determine_message_type("Packing tips") == "wardrobe"

    def test_determine_message_type_style(self, orchestrator):
        """Test that style messages are correctly identified."""
        assert orchestrator._determine_message_type("What's the dress code?") == "style"
        assert orchestrator._determine_message_type("style_etiquette") == "style"
        assert orchestrator._determine_message_type("Fashion advice") == "style"

    def test_determine_message_type_destination(self, orchestrator):
        """Test that destination messages are correctly identified."""
        assert orchestrator._determine_message_type("Tell me about Paris") == "destination"
        assert orchestrator._determine_message_type("destination_info") == "destination"
        assert orchestrator._determine_message_type("Going to Tokyo") == "destination"

    def test_determine_message_type_general(self, orchestrator):
        """Test that general messages fall back to general type."""
        assert orchestrator._determine_message_type("Hello") == "general"
        assert orchestrator._determine_message_type("How are you?") == "general"

    def test_extract_destination(self, orchestrator):
        """Test destination extraction from messages."""
        assert orchestrator._extract_destination("I'm going to Paris") == "Paris"
        assert orchestrator._extract_destination("Visiting Tokyo next week") == "Tokyo"
        assert orchestrator._extract_destination("Trip to New York") == "New York"
        assert orchestrator._extract_destination("Hello there") is None

    @pytest.mark.asyncio
    async def test_route_message_currency(self, orchestrator, base_context):
        """Test routing to currency handler."""
        with patch.object(orchestrator, "_handle_currency_request") as mock_handler:
            mock_handler.return_value = "currency_response"

            result = await orchestrator.route_message(
                "Convert 100 USD to EUR", base_context, [], None
            )

            mock_handler.assert_called_once()
            assert result == "currency_response"

    @pytest.mark.asyncio
    async def test_route_message_weather(self, orchestrator, base_context):
        """Test routing to weather handler."""
        with patch.object(orchestrator, "_handle_weather_request") as mock_handler:
            mock_handler.return_value = "weather_response"

            result = await orchestrator.route_message(
                "What's the weather like in Paris?", base_context, [], None
            )

            mock_handler.assert_called_once()
            assert result == "weather_response"

    @pytest.mark.asyncio
    async def test_route_message_wardrobe(self, orchestrator, base_context):
        """Test routing to wardrobe handler."""
        with patch.object(orchestrator, "_handle_wardrobe_request") as mock_handler:
            mock_handler.return_value = "wardrobe_response"

            result = await orchestrator.route_message(
                "What should I pack for my trip?", base_context, [], None
            )

            mock_handler.assert_called_once()
            assert result == "wardrobe_response"

    @pytest.mark.asyncio
    async def test_route_message_style(self, orchestrator, base_context):
        """Test routing to style handler."""
        with patch.object(orchestrator, "_handle_style_request") as mock_handler:
            mock_handler.return_value = "style_response"

            result = await orchestrator.route_message(
                "What's the dress code for restaurants?", base_context, [], None
            )

            mock_handler.assert_called_once()
            assert result == "style_response"

    @pytest.mark.asyncio
    async def test_route_message_destination(self, orchestrator, base_context):
        """Test routing to destination handler."""
        with patch.object(orchestrator, "_handle_destination_request") as mock_handler:
            mock_handler.return_value = "destination_response"

            result = await orchestrator.route_message("Tell me about Tokyo", base_context, [], None)

            mock_handler.assert_called_once()
            assert result == "destination_response"

    @pytest.mark.asyncio
    async def test_route_message_general(self, orchestrator, base_context):
        """Test routing to general handler."""
        with patch.object(orchestrator, "_handle_general_request") as mock_handler:
            mock_handler.return_value = "general_response"

            result = await orchestrator.route_message("Hello, how are you?", base_context, [], None)

            mock_handler.assert_called_once()
            assert result == "general_response"

    def test_backward_compatibility(self, orchestrator):
        """Test that the old method still works for backward compatibility."""
        assert hasattr(orchestrator, "generate_travel_recommendations")
        assert callable(orchestrator.generate_travel_recommendations)


# ---- AI Classification Tests ----


class TestOrchestratorAIClassification:
    """Test the AI-based message classification functionality."""

    @pytest.mark.asyncio
    async def test_classify_currency_message(self, orchestrator):
        """Test classification of currency-related messages."""
        with patch("app.services.orchestrator.openai_service") as mock_openai:
            mock_openai.get_completion.return_value = "currency"

            result = await orchestrator._classify_message("I want to convert USD to EUR")

            assert result == "currency"
            mock_openai.get_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_classify_weather_message(self, orchestrator):
        """Test classification of weather-related messages."""
        with patch("app.services.orchestrator.openai_service") as mock_openai:
            mock_openai.get_completion.return_value = "weather"

            result = await orchestrator._classify_message("What's the weather like in Paris?")

            assert result == "weather"
            mock_openai.get_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_classify_logistics_message(self, orchestrator):
        """Test classification of logistics-related messages."""
        with patch("app.services.orchestrator.openai_service") as mock_openai:
            mock_openai.get_completion.return_value = "logistics"

            result = await orchestrator._classify_message(
                "I would like to go to London from 2025-09-02 until 2025-09-09 and manage the currency exchange for the British Pound"
            )

            assert result == "logistics"
            mock_openai.get_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_classify_general_message(self, orchestrator):
        """Test classification of general messages."""
        with patch("app.services.orchestrator.openai_service") as mock_openai:
            mock_openai.get_completion.return_value = "general"

            result = await orchestrator._classify_message("Hello, how are you?")

            assert result == "general"
            mock_openai.get_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_classify_fallback_on_error(self, orchestrator):
        """Test that classification falls back to general on error."""
        with patch("app.services.orchestrator.openai_service") as mock_openai:
            mock_openai.get_completion.side_effect = Exception("API Error")

            result = await orchestrator._classify_message("Some message")

            assert result == "general"

    @pytest.mark.asyncio
    async def test_classify_invalid_response(self, orchestrator):
        """Test classification handles invalid responses."""
        with patch("app.services.orchestrator.openai_service") as mock_openai:
            mock_openai.get_completion.return_value = "invalid_category"

            result = await orchestrator._classify_message("Some message")

            assert result == "general"

    @pytest.mark.asyncio
    async def test_route_message_with_ai_classification(self, orchestrator, base_context):
        """Test that routing uses AI classification."""
        with patch.object(orchestrator, "_classify_message") as mock_classify:
            with patch.object(orchestrator, "_handle_currency_request") as mock_handler:
                mock_classify.return_value = "currency"
                mock_handler.return_value = "currency_response"

                result = await orchestrator.route_message(
                    "Convert 100 USD to EUR", base_context, [], None
                )

                mock_classify.assert_called_once_with("Convert 100 USD to EUR")
                mock_handler.assert_called_once()
                assert result == "currency_response"

    def test_extract_travel_dates(self, orchestrator):
        """Test travel date extraction."""
        # Test "until" format
        dates = orchestrator._extract_travel_dates("2025-09-02 until 2025-09-09")
        assert dates == ["2025-09-02", "2025-09-09"]

        # Test "from...to" format
        dates = orchestrator._extract_travel_dates("from 2025-09-02 to 2025-09-09")
        assert dates == ["2025-09-02", "2025-09-09"]

        # Test "to" format
        dates = orchestrator._extract_travel_dates("2025-09-02 to 2025-09-09")
        assert dates == ["2025-09-02", "2025-09-09"]

        # Test no dates
        dates = orchestrator._extract_travel_dates("Hello there")
        assert dates is None
