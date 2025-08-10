"""Tests for the OpenAI service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.responses import ChatResponse
from app.services.openai.openai_service import OpenAIService
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage


class TestOpenAIService:
    """Test cases for OpenAIService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = OpenAIService()
        self.service.client = AsyncMock()

    def test_init(self):
        """Test service initialization."""
        service = OpenAIService()
        assert service.model == "gpt-4o-mini"
        assert service.temperature == 0.7
        assert service.max_tokens == 1000

    @patch("app.services.openai.openai_service.settings")
    def test_init_with_settings(self, mock_settings):
        """Test service initialization with mocked settings."""
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_ORG_ID = "test-org"

        with patch("app.services.openai.openai_service.AsyncOpenAI") as mock_client:
            service = OpenAIService()
            mock_client.assert_called_once_with(api_key="test-key", organization="test-org")

    @pytest.mark.asyncio
    async def test_generate_response_success(self):
        """Test successful response generation."""
        # Mock the OpenAI response
        mock_response = MagicMock(spec=ChatCompletion)
        mock_choice = MagicMock(spec=Choice)
        mock_message = MagicMock(spec=ChatCompletionMessage)
        mock_message.content = 'Test AI response with [QUICK: "Test quick reply"]'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        self.service.client.chat.completions.create.return_value = mock_response

        result = await self.service.generate_response(
            user_message="Test message",
            conversation_history=[{"role": "user", "content": "Previous message"}],
            cultural_context={"note": "Test culture"},
            weather_context={"temperature": 25},
            user_profile={"style_preferences": "casual"},
            context_type="wardrobe",
        )

        assert isinstance(result, ChatResponse)
        assert "Test AI response with" in result.message
        assert len(result.quick_replies) == 1
        assert result.quick_replies[0].text == "Test quick reply"
        assert result.confidence_score == 0.85

    @pytest.mark.asyncio
    async def test_generate_response_no_content(self):
        """Test response generation when AI returns no content."""
        # Mock the OpenAI response with no content
        mock_response = MagicMock(spec=ChatCompletion)
        mock_choice = MagicMock(spec=Choice)
        mock_message = MagicMock(spec=ChatCompletionMessage)
        mock_message.content = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        self.service.client.chat.completions.create.return_value = mock_response

        result = await self.service.generate_response(
            user_message="Test message", conversation_history=[], context_type="style"
        )

        assert isinstance(result, ChatResponse)
        assert "I apologize, but I'm having trouble" in result.message
        assert result.confidence_score == 0.0

    @pytest.mark.asyncio
    async def test_generate_response_exception(self):
        """Test response generation when an exception occurs."""
        self.service.client.chat.completions.create.side_effect = Exception("API Error")

        result = await self.service.generate_response(
            user_message="Test message", conversation_history=[], context_type="destination"
        )

        assert isinstance(result, ChatResponse)
        assert "I apologize, but I'm having trouble" in result.message
        assert result.confidence_score == 0.0

    @pytest.mark.asyncio
    async def test_get_completion_success(self):
        """Test successful completion retrieval."""
        mock_response = MagicMock(spec=ChatCompletion)
        mock_choice = MagicMock(spec=Choice)
        mock_message = MagicMock(spec=ChatCompletionMessage)
        mock_message.content = "Test completion"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        self.service.client.chat.completions.create.return_value = mock_response

        result = await self.service.get_completion(
            messages=[{"role": "user", "content": "Test"}], temperature=0.5, max_tokens=500
        )

        assert result == "Test completion"
        self.service.client.chat.completions.create.assert_called_once_with(
            model=self.service.model,
            messages=[{"role": "user", "content": "Test"}],
            temperature=0.5,
            max_tokens=500,
        )

    @pytest.mark.asyncio
    async def test_get_completion_no_content(self):
        """Test completion retrieval when AI returns no content."""
        mock_response = MagicMock(spec=ChatCompletion)
        mock_choice = MagicMock(spec=Choice)
        mock_message = MagicMock(spec=ChatCompletionMessage)
        mock_message.content = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        self.service.client.chat.completions.create.return_value = mock_response

        result = await self.service.get_completion(messages=[{"role": "user", "content": "Test"}])

        assert result is None

    @pytest.mark.asyncio
    async def test_get_completion_exception(self):
        """Test completion retrieval when an exception occurs."""
        self.service.client.chat.completions.create.side_effect = Exception("API Error")

        result = await self.service.get_completion(messages=[{"role": "user", "content": "Test"}])

        assert result is None

    def test_build_system_prompt_default(self):
        """Test system prompt building with default context."""
        result = self.service._build_system_prompt()

        assert "TravelStyle AI" in result
        assert "culturally intelligent" in result
        assert "wardrobe expert" in result
        assert "5 tops, 4 bottoms, 3 shoes, 2 layers, 1 accessory set" in result

    def test_build_system_prompt_wardrobe(self):
        """Test system prompt building with wardrobe context."""
        result = self.service._build_system_prompt("wardrobe")

        assert "WARDROBE FOCUS" in result
        assert "clothing and packing recommendations" in result
        assert "layering strategies" in result

    def test_build_system_prompt_style(self):
        """Test system prompt building with style context."""
        result = self.service._build_system_prompt("style")

        assert "STYLE FOCUS" in result
        assert "fashion etiquette" in result
        assert "dress codes" in result

    def test_build_system_prompt_destination(self):
        """Test system prompt building with destination context."""
        result = self.service._build_system_prompt("destination")

        assert "DESTINATION FOCUS" in result
        assert "comprehensive destination information" in result
        assert "cultural insights" in result

    def test_build_system_prompt_logistics(self):
        """Test system prompt building with logistics context."""
        result = self.service._build_system_prompt("logistics")

        assert "LOGISTICS FOCUS" in result
        assert "visa requirements" in result
        assert "vaccination needs" in result
        assert "actionable steps and timelines" in result

    def test_build_context_prompt_all_contexts(self):
        """Test context prompt building with all contexts provided."""
        user_profile = {"style": "casual", "preference": "comfortable"}
        weather_context = {"temperature": 25, "description": "sunny"}
        cultural_context = {"note": "formal dress expected"}

        result = self.service._build_context_prompt(cultural_context, weather_context, user_profile)

        assert "CURRENT TRAVEL CONTEXT" in result
        assert "User Preferences" in result
        assert "Weather Summary" in result
        assert "Cultural Insights" in result
        assert "25" in result  # temperature
        assert "sunny" in result  # description
        assert "formal dress expected" in result  # cultural note

    def test_build_context_prompt_no_contexts(self):
        """Test context prompt building with no contexts provided."""
        result = self.service._build_context_prompt(None, None, None)

        assert "CURRENT TRAVEL CONTEXT" in result
        assert len(result.split("\n\n")) == 1  # Only the header

    def test_build_context_prompt_partial_contexts(self):
        """Test context prompt building with partial contexts."""
        # Only user profile
        result = self.service._build_context_prompt(None, None, {"test": "value"})
        assert "User Preferences" in result
        assert "Weather Summary" not in result
        assert "Cultural Insights" not in result

        # Only weather
        result = self.service._build_context_prompt(None, {"temp": 20}, None)
        assert "Weather Summary" in result
        assert "User Preferences" not in result
        assert "Cultural Insights" not in result

        # Only cultural
        result = self.service._build_context_prompt({"note": "test"}, None, None)
        assert "Cultural Insights" in result
        assert "User Preferences" not in result
        assert "Weather Summary" not in result

    def test_process_response_with_quick_replies(self):
        """Test response processing with quick replies."""
        ai_message = 'Here is a response [QUICK: "Option 1"] and another [QUICK: "Option 2"]'

        result = self.service._process_response(ai_message)

        assert isinstance(result, ChatResponse)
        assert "Here is a response  and another" in result.message
        assert len(result.quick_replies) == 2
        assert result.quick_replies[0].text == "Option 1"
        assert result.quick_replies[1].text == "Option 2"
        assert result.confidence_score == 0.85

    def test_process_response_with_suggestions(self):
        """Test response processing with suggestion detection."""
        ai_message = "Would you like more details? Also consider alternatives."

        result = self.service._process_response(ai_message)

        assert isinstance(result, ChatResponse)
        assert len(result.suggestions) == 2
        assert "Get more details" in result.suggestions
        assert "Show alternatives" in result.suggestions

    def test_process_response_no_quick_replies_or_suggestions(self):
        """Test response processing without quick replies or suggestions."""
        ai_message = "Simple response without special markers."

        result = self.service._process_response(ai_message)

        assert isinstance(result, ChatResponse)
        assert result.message == "Simple response without special markers."
        assert len(result.quick_replies) == 0
        assert len(result.suggestions) == 0

    def test_enrich_user_profile_with_data(self):
        """Test user profile enrichment with provided data."""
        user_profile = {
            "style_preferences": "formal",
            "packing_methods": "minimalist",
            "luggage_type": "checked",
            "trip_length_days": 14,
        }

        result = self.service._enrich_user_profile(user_profile)

        assert result["style_preferences"] == "formal"
        assert result["packing_methods"] == "minimalist"
        assert result["luggage_type"] == "checked"
        assert result["trip_length_days"] == 14

    def test_enrich_user_profile_without_data(self):
        """Test user profile enrichment without data."""
        result = self.service._enrich_user_profile(None)

        assert result["style_preferences"] == "casual chic"
        assert result["packing_methods"] == "5-4-3-2-1"
        assert result["luggage_type"] == "carry-on"
        assert result["trip_length_days"] == 7

    def test_enrich_user_profile_partial_data(self):
        """Test user profile enrichment with partial data."""
        user_profile = {"style_preferences": "elegant"}

        result = self.service._enrich_user_profile(user_profile)

        assert result["style_preferences"] == "elegant"
        assert result["packing_methods"] == "5-4-3-2-1"  # default
        assert result["luggage_type"] == "carry-on"  # default
        assert result["trip_length_days"] == 7  # default

    def test_enrich_weather_without_data(self):
        """Test weather enrichment without data."""
        result = self.service._enrich_weather(None)

        assert result["description"] == "Weather not available"
        assert result["temp_range"]["min"] == 20
        assert result["temp_range"]["max"] == 25
        assert result["precipitation_chance"] == 0
        assert result["temperature"] == 22
        assert result["feels_like"] == 22
        assert result["humidity"] == 50
        assert result["wind_speed"] == 3
        assert result["visibility"] == 10
        assert result["pressure"] == 1013

    def test_enrich_weather_with_data(self):
        """Test weather enrichment with provided data."""
        weather_data = {
            "temperature": 30,
            "feels_like": 32,
            "humidity": 80,
            "description": "Hot and humid",
            "wind_speed": 5,
            "visibility": 8,
            "pressure": 1000,
            "temp_range": {"min": 28, "max": 35},
            "precipitation_chance": 20,
        }

        result = self.service._enrich_weather(weather_data)

        assert result["temperature"] == 30
        assert result["feels_like"] == 32
        assert result["humidity"] == 80
        assert result["description"] == "Hot and humid"
        assert result["wind_speed"] == 5
        assert result["visibility"] == 8
        assert result["pressure"] == 1000
        assert result["temp_range"]["min"] == 28
        assert result["temp_range"]["max"] == 35
        assert result["precipitation_chance"] == 20

    def test_enrich_weather_partial_data(self):
        """Test weather enrichment with partial data."""
        weather_data = {"temperature": 15}

        result = self.service._enrich_weather(weather_data)

        assert result["temperature"] == 15
        assert result["feels_like"] == 22  # default
        assert result["humidity"] == 50  # default
        assert result["description"] == "Partly cloudy"  # default
        assert result["wind_speed"] == 3  # default
        assert result["visibility"] == 10  # default
        assert result["pressure"] == 1013  # default
        assert result["temp_range"]["min"] == 20  # default
        assert result["temp_range"]["max"] == 25  # default
        assert result["precipitation_chance"] == 10  # default

    def test_enrich_weather_empty_temp_range(self):
        """Test weather enrichment with empty temp_range."""
        weather_data = {"temp_range": {}}

        result = self.service._enrich_weather(weather_data)

        assert result["temp_range"]["min"] == 20  # default
        assert result["temp_range"]["max"] == 25  # default
