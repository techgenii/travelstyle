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
        self.model = "gpt-4"
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
        """Generate AI response with full context.

        Args:
            user_message: The user's message.
            conversation_history: List of previous messages.
            cultural_context: Cultural context dict.
            weather_context: Weather context dict.
            user_profile: User profile dict.

        Returns:
            ChatResponse object with AI's reply and quick replies.
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        try:
            system_prompt = self._build_system_prompt()
            context_prompt = self._build_context_prompt(
                cultural_context, weather_context, user_profile
            )

            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": context_prompt},
            ]
            # Add conversation history (last 10 messages)
            messages.extend(cast(list[ChatCompletionMessageParam], conversation_history[-10:]))
            messages.append({"role": "user", "content": user_message})

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
            # Process response to extract quick replies and suggestions
            return self._process_response(ai_message)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("OpenAI API error: %s", type(e).__name__)
            return ChatResponse(
                message=(
                    "I apologize, but I'm having trouble processing your request right now. "
                    "Please try again."
                ),
                confidence_score=0.0,
            )

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI model."""
        return """
You are TravelStyle AI, an expert travel wardrobe consultant with cultural intelligence.

CAPABILITIES:
- Wardrobe planning with cultural awareness
- Local etiquette and dress code guidance
- Weather-appropriate recommendations
- Currency conversion assistance

PERSONALITY:
- Friendly, professional, culturally sensitive
- Practical and actionable advice
- Concise but comprehensive responses

RESPONSE FORMAT:
- Always include cultural context when relevant
- Suggest quick-reply options when appropriate (format: [QUICK: option text])
- Reference weather conditions in recommendations
- Be specific about clothing items and styles

CULTURAL SENSITIVITY:
- Respect local customs and dress codes
- Provide context for cultural recommendations
- Avoid stereotypes, focus on practical guidance
- Include both traditional and modern perspectives

For quick replies, use format: [QUICK: "Tell me about colors"] [QUICK: "Show accessories"]
"""

    def _build_context_prompt(
        self,
        cultural_context: dict[str, Any] | None,
        weather_context: dict[str, Any] | None,
        user_profile: dict[str, Any] | None,
    ) -> str:
        """Builds a context prompt from cultural, weather, and user profile data."""
        context_parts = ["CURRENT CONTEXT:"]

        if cultural_context:
            context_parts.append(f"Cultural insights: {json.dumps(cultural_context, indent=2)}")
        if weather_context:
            context_parts.append(f"Weather conditions: {json.dumps(weather_context, indent=2)}")
        if user_profile:
            context_parts.append(f"User preferences: {json.dumps(user_profile, indent=2)}")
        return "\n".join(context_parts)

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


# Singleton instance
openai_service = OpenAIService()
