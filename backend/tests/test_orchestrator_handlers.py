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
Additional tests for TravelOrchestratorService handlers and error branches to improve coverage.
"""

from unittest.mock import AsyncMock, patch

import pytest
from app.models.responses import ChatResponse, ConversationContext
from app.services.currency_conversion_service import currency_conversion_service
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
            currency_conversion_service,
            "handle_currency_help_request",
            new=AsyncMock(return_value=help_resp),
        ),
        patch.object(
            currency_conversion_service, "handle_currency_request", new=AsyncMock(return_value=None)
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
            currency_conversion_service,
            "handle_currency_help_request",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            currency_conversion_service,
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
            currency_conversion_service,
            "handle_currency_help_request",
            new=AsyncMock(return_value=None),
        ),
        patch.object(
            currency_conversion_service,
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
