"""OpenAI service for TravelStyle AI: handles chat completions and response processing."""

import json
import logging
import re
from typing import Any, cast

from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from app.core.config import settings
from app.models.responses import ChatResponse, QuickReply

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI's chat models for TravelStyle AI."""

    # pylint: disable=too-few-public-methods

    def __init__(self):
        """Initialize the OpenAIService with API credentials and default parameters."""
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, organization=settings.OPENAI_ORG_ID
        )
        self.model = "gpt-4o-mini"
        self.temperature = 0.7
        self.max_tokens = 1000

    async def generate_response(
        self,
        user_message: str,
        conversation_history: list[dict[str, str]],
        cultural_context: dict[str, Any] | None = None,
        weather_context: dict[str, Any] | None = None,
        user_profile: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """Generate AI response with full context, fallback logic, and improved prompt formatting."""
        try:
            # ---- Step 1: Enrich or fallback missing context ----
            enriched_profile = self._enrich_user_profile(user_profile)
            enriched_weather = self._enrich_weather(weather_context)
            enriched_culture = cultural_context or {"note": "No cultural insights available."}

            # ---- Step 2: Build prompt blocks ----
            system_prompt = self._build_system_prompt()
            context_prompt = self._build_context_prompt(
                enriched_culture, enriched_weather, enriched_profile
            )

            # ---- Step 3: Assemble full message list ----
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": context_prompt},
            ]
            messages.extend(cast(list[ChatCompletionMessageParam], conversation_history[-10:]))
            messages.append({"role": "user", "content": user_message})

            # ---- Step 4: Call OpenAI ----
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            ai_message = response.choices[0].message.content
            if not ai_message:
                raise ValueError("No content in AI response")

            return self._process_response(ai_message)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("OpenAI API error: %s", type(e).__name__)
            return ChatResponse(
                message="I apologize, but I'm having trouble processing your request right now. Please try again.",
                confidence_score=0.0,
            )

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI model."""
        return """
    You are TravelStyle AI, a culturally intelligent, weather-aware travel wardrobe expert.

    CAPABILITIES:
    - Wardrobe planning with cultural and climate awareness
    - Local etiquette and dress code guidance
    - Weather-responsive outfit planning using forecast and current conditions
    - Packing strategy recommendations based on duration and method
    - Currency tips if needed

    PERSONALITY:
    - Friendly, professional, culturally sensitive
    - Practical and actionable advice
    - Concise but comprehensive responses

    RESPONSE FORMAT:
    - Include cultural insights if relevant (e.g. modesty norms, temple visits)
    - Reference weather and travel dates in wardrobe recommendations
    - Recommend specific items (e.g. 2 long-sleeve tops, 1 rain jacket)
    - Use mix-and-match packing methods such as 5-4-3-2-1 when available
    - Add quick replies like [QUICK: "Swap packing method"] or [QUICK: "Show layers"]

    DEFAULTS:
    - If no packing method found, use: 5 tops, 4 bottoms, 3 shoes, 2 layers, 1 accessory set
    - Assume carry-on sized packing unless otherwise stated

    SENSITIVITY:
    - Avoid cultural stereotypes
    - Focus on practical, inclusive recommendations
    - Show both modern and traditional perspectives

    GOAL:
    Help the user confidently pack for their destination with culturally respectful, stylish, and weather-appropriate clothing.
    """

    def _build_context_prompt(
        self,
        cultural_context: dict[str, Any] | None,
        weather_context: dict[str, Any] | None,
        user_profile: dict[str, Any] | None,
    ) -> str:
        """Builds a context prompt from cultural, weather, and user profile data."""
        context_parts = ["CURRENT TRAVEL CONTEXT:"]

        if user_profile:
            context_parts.append("User Preferences:\n" + json.dumps(user_profile, indent=2))

        if weather_context:
            weather_summary = {
                "Current Temperature (°C)": weather_context.get("temperature"),
                "Feels Like (°C)": weather_context.get("feels_like"),
                "Humidity (%)": weather_context.get("humidity"),
                "Weather Description": weather_context.get("description"),
                "Wind Speed (m/s)": weather_context.get("wind_speed"),
                "Visibility (km)": weather_context.get("visibility"),
                "Pressure (hPa)": weather_context.get("pressure"),
                "Forecast Range (°C)": weather_context.get("temp_range", {}),
                "Chance of Precipitation (%)": weather_context.get("precipitation_chance"),
            }
            context_parts.append("Weather Summary:\n" + json.dumps(weather_summary, indent=2))

        if cultural_context:
            context_parts.append("Cultural Insights:\n" + json.dumps(cultural_context, indent=2))

        return "\n\n".join(context_parts)

    def _process_response(self, ai_message: str) -> ChatResponse:
        """Extract quick replies and clean up response."""
        quick_replies = []
        quick_reply_pattern = r'\[QUICK:\s*"([^"]+)"\]'
        matches = re.findall(quick_reply_pattern, ai_message)
        for match in matches:
            quick_replies.append(QuickReply(text=match))
        # Remove quick reply markers from message
        cleaned_message = re.sub(quick_reply_pattern, "", ai_message).strip()
        # Extract suggestions (simple heuristic)
        suggestions = []
        if "would you like" in cleaned_message.lower():
            suggestions.append("Get more details")
        if "also consider" in cleaned_message.lower():
            suggestions.append("Show alternatives")
        return ChatResponse(
            message=cleaned_message,
            quick_replies=quick_replies,
            suggestions=suggestions,
            confidence_score=0.85,
        )

    def _enrich_user_profile(self, user_profile: dict[str, Any] | None) -> dict[str, Any]:
        profile = user_profile or {}
        return {
            "style_preferences": profile.get("style_preferences", "casual chic"),
            "packing_methods": profile.get("packing_methods", "5-4-3-2-1"),
            "luggage_type": profile.get("luggage_type", "carry-on"),
            "trip_length_days": profile.get("trip_length_days", 7),
        }

    def _enrich_weather(self, weather: dict[str, Any] | None) -> dict[str, Any]:
        if not weather:
            return {
                "description": "Weather not available",
                "temp_range": {"min": 20, "max": 25},
                "precipitation_chance": 0,
                "temperature": 22,
                "feels_like": 22,
                "humidity": 50,
                "wind_speed": 3,
                "visibility": 10,
                "pressure": 1013,
            }

        forecast = weather.get("temp_range", {})
        return {
            "temperature": weather.get("temperature", 22),
            "feels_like": weather.get("feels_like", 22),
            "humidity": weather.get("humidity", 50),
            "description": weather.get("description", "Partly cloudy"),
            "wind_speed": weather.get("wind_speed", 3),
            "visibility": weather.get("visibility", 10),
            "pressure": weather.get("pressure", 1013),
            "temp_range": {
                "min": forecast.get("min", 20),
                "max": forecast.get("max", 25),
            },
            "precipitation_chance": weather.get("precipitation_chance", 10),
        }


# Singleton instance
openai_service = OpenAIService()
