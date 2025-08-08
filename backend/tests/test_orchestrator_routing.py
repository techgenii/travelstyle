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

"""Tests for the new orchestrator routing functionality."""

from unittest.mock import patch

import pytest
from app.models.responses import ConversationContext
from app.services.orchestrator import TravelOrchestratorService


class TestOrchestratorRouting:
    """Test the new routing functionality of the orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create a fresh orchestrator instance for each test."""
        return TravelOrchestratorService()

    @pytest.fixture
    def context(self):
        """Create a basic conversation context."""
        return ConversationContext(user_id="test_user")

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
    async def test_route_message_currency(self, orchestrator, context):
        """Test routing to currency handler."""
        with patch.object(orchestrator, "_handle_currency_request") as mock_handler:
            mock_handler.return_value = "currency_response"

            result = await orchestrator.route_message("Convert 100 USD to EUR", context, [], None)

            mock_handler.assert_called_once()
            assert result == "currency_response"

    @pytest.mark.asyncio
    async def test_route_message_weather(self, orchestrator, context):
        """Test routing to weather handler."""
        with patch.object(orchestrator, "_handle_weather_request") as mock_handler:
            mock_handler.return_value = "weather_response"

            result = await orchestrator.route_message(
                "What's the weather like in Paris?", context, [], None
            )

            mock_handler.assert_called_once()
            assert result == "weather_response"

    @pytest.mark.asyncio
    async def test_route_message_wardrobe(self, orchestrator, context):
        """Test routing to wardrobe handler."""
        with patch.object(orchestrator, "_handle_wardrobe_request") as mock_handler:
            mock_handler.return_value = "wardrobe_response"

            result = await orchestrator.route_message(
                "What should I pack for my trip?", context, [], None
            )

            mock_handler.assert_called_once()
            assert result == "wardrobe_response"

    @pytest.mark.asyncio
    async def test_route_message_style(self, orchestrator, context):
        """Test routing to style handler."""
        with patch.object(orchestrator, "_handle_style_request") as mock_handler:
            mock_handler.return_value = "style_response"

            result = await orchestrator.route_message(
                "What's the dress code for restaurants?", context, [], None
            )

            mock_handler.assert_called_once()
            assert result == "style_response"

    @pytest.mark.asyncio
    async def test_route_message_destination(self, orchestrator, context):
        """Test routing to destination handler."""
        with patch.object(orchestrator, "_handle_destination_request") as mock_handler:
            mock_handler.return_value = "destination_response"

            result = await orchestrator.route_message("Tell me about Tokyo", context, [], None)

            mock_handler.assert_called_once()
            assert result == "destination_response"

    @pytest.mark.asyncio
    async def test_route_message_general(self, orchestrator, context):
        """Test routing to general handler."""
        with patch.object(orchestrator, "_handle_general_request") as mock_handler:
            mock_handler.return_value = "general_response"

            result = await orchestrator.route_message("Hello, how are you?", context, [], None)

            mock_handler.assert_called_once()
            assert result == "general_response"

    def test_backward_compatibility(self, orchestrator):
        """Test that the old method still works for backward compatibility."""
        assert hasattr(orchestrator, "generate_travel_recommendations")
        assert callable(orchestrator.generate_travel_recommendations)
