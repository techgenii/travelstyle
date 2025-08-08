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

"""Tests for the AI-based message classification functionality."""

from unittest.mock import patch

import pytest
from app.models.responses import ConversationContext
from app.services.orchestrator import TravelOrchestratorService


class TestOrchestratorAIClassification:
    """Test the AI-based message classification functionality."""

    @pytest.fixture
    def orchestrator(self):
        """Create a fresh orchestrator instance for each test."""
        return TravelOrchestratorService()

    @pytest.fixture
    def context(self):
        """Create a basic conversation context."""
        return ConversationContext(user_id="test_user")

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
        """Test that classification handles invalid responses."""
        with patch("app.services.orchestrator.openai_service") as mock_openai:
            mock_openai.get_completion.return_value = "invalid_category"

            result = await orchestrator._classify_message("Some message")

            assert result == "general"

    @pytest.mark.asyncio
    async def test_route_message_with_ai_classification(self, orchestrator, context):
        """Test that routing uses AI classification."""
        with patch.object(orchestrator, "_classify_message") as mock_classify:
            with patch.object(orchestrator, "_handle_currency_request") as mock_handler:
                mock_classify.return_value = "currency"
                mock_handler.return_value = "currency_response"

                result = await orchestrator.route_message(
                    "Convert 100 USD to EUR", context, [], None
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
