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

"""Orchestration service for TravelStyle AI: dispatches messages to specialized handlers.
This service acts as a router that takes messages from UI buttons and routes them to
appropriate specialized chat functions that return the correct response for display.
"""

import inspect
import logging
import re
from typing import Any

from app.models.responses import ChatResponse, ConversationContext, QuickReply
from app.services.currency import CurrencyService
from app.services.openai.openai_service import openai_service
from app.services.qloo import qloo_service
from app.services.weather import weather_service

logger = logging.getLogger(__name__)


class TravelOrchestratorService:
    """Main orchestration service that dispatches messages to specialized handlers."""

    def __init__(self):
        """Initialize the orchestrator."""
        self.currency_service = CurrencyService()

    async def route_message(
        self,
        user_message: str,
        context: ConversationContext,
        conversation_history: list[dict[str, str]],
        user_profile: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """
        Main routing function that dispatches messages to appropriate handlers.
        Acts as a case statement that routes based on message content or UI actions.
        """
        try:
            # Use OpenAI to classify the message type
            message_type = await self._classify_message(user_message)

            # Route to appropriate handler based on message type
            if message_type == "currency":
                return await self._handle_currency_request(user_message, context)
            elif message_type == "weather":
                return await self._handle_weather_request(user_message, context)
            elif message_type == "cultural":
                return await self._handle_cultural_request(user_message, context)
            elif message_type == "wardrobe":
                return await self._handle_wardrobe_request(
                    user_message, context, conversation_history, user_profile
                )
            elif message_type == "style":
                return await self._handle_style_request(
                    user_message, context, conversation_history, user_profile
                )
            elif message_type == "destination":
                return await self._handle_destination_request(
                    user_message, context, conversation_history, user_profile
                )
            elif message_type == "logistics":
                return await self._handle_logistics_request(
                    user_message, context, conversation_history, user_profile
                )
            else:
                # Default to general travel recommendations
                return await self._handle_general_request(
                    user_message, context, conversation_history, user_profile
                )

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Routing error: %s", type(e).__name__)
            logger.error("Error details: %s", str(e))
            import traceback

            logger.error("Traceback: %s", traceback.format_exc())
            return ChatResponse(
                message=(
                    "I apologize, but I'm having trouble processing your request right now. "
                    "Please try again."
                ),
                confidence_score=0.0,
            )

    async def _classify_message(self, user_message: str) -> str:
        """Use OpenAI to classify the message type."""
        try:
            classification_prompt = f"""
            Classify the following travel-related message into one of these categories:
            - currency: currency exchange, rates, money conversion, pounds, dollars, euros
            - weather: weather forecast, temperature, climate, weather conditions
            - cultural: cultural etiquette, local customs, traditions, cultural tips
            - wardrobe: packing, clothing, what to wear, outfit planning
            - style: dress code, fashion advice, formal vs casual attire
            - destination: information about a place, travel to, visiting
            - logistics: comprehensive travel planning, visas, vaccinations, travel preparation
            - general: general travel questions, greetings, or other topics

            Message: "{user_message}"

            Respond with only the category name (e.g., "currency", "weather", etc.):
            """

            response = openai_service.get_completion(
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0.1,
                max_tokens=10,
            )

            # Support both async and sync implementations/mocks
            if inspect.isawaitable(response):
                response = await response

            if response:
                # Clean up the response and extract the category
                category = response.strip().lower()
                valid_categories = [
                    "currency",
                    "weather",
                    "cultural",
                    "wardrobe",
                    "style",
                    "destination",
                    "logistics",
                    "general",
                ]

                if category in valid_categories:
                    return category

            # Fallback to general if classification fails
            return "general"

        except Exception as e:
            logger.error(f"Message classification error: {e}")
            return "general"

    def _determine_message_type(self, user_message: str) -> str:
        """Rule-based message type determination for quick routing and tests."""
        text = user_message.lower().strip()

        # Action-style hints
        if any(
            token in text
            for token in [
                "currency_convert",
                "currency_rate",
                "currency",
            ]
        ):
            return "currency"
        if any(token in text for token in ["weather_info", "weather"]):
            return "weather"
        if any(token in text for token in ["wardrobe_planning", "wardrobe"]):
            return "wardrobe"
        if any(token in text for token in ["style_etiquette", "style"]):
            return "style"
        if any(token in text for token in ["destination_info", "destination"]):
            return "destination"

        # Keyword heuristics
        currency_keywords = [
            "convert",
            "exchange rate",
            "rate",
            "usd",
            "eur",
            "gbp",
            "yen",
            "jpy",
        ]
        if any(k in text for k in currency_keywords):
            return "currency"

        weather_keywords = ["weather", "temperature", "forecast", "rain", "sunny"]
        if any(k in text for k in weather_keywords):
            return "weather"

        wardrobe_keywords = ["pack", "packing", "what should i pack", "outfit"]
        if any(k in text for k in wardrobe_keywords):
            return "wardrobe"

        style_keywords = ["dress code", "fashion", "etiquette", "style"]
        if any(k in text for k in style_keywords):
            return "style"

        destination_keywords = ["tell me about", "going to", "visiting", "trip to"]
        if any(k in text for k in destination_keywords):
            return "destination"

        logistics_keywords = ["visa", "vaccination", "itinerary", "logistics", "preparation"]
        if any(k in text for k in logistics_keywords):
            return "logistics"

        return "general"

    async def _handle_currency_request(
        self, user_message: str, context: ConversationContext
    ) -> ChatResponse:
        """Handle currency conversion and exchange rate requests."""
        try:
            # Check for currency help requests first
            help_response = await self.currency_service.handle_currency_help_request(user_message)
            if help_response:
                quick_replies = []
                if "quick_replies" in help_response:
                    quick_replies = [
                        QuickReply(text=qr["text"], action=qr["action"])
                        for qr in help_response["quick_replies"]
                    ]
                return ChatResponse(
                    message=help_response["message"],
                    confidence_score=0.9,
                    quick_replies=quick_replies,
                )

            # Process currency request
            result = await self.currency_service.handle_currency_request(user_message)

            if result and result.get("success") and "data" in result:
                data = result["data"]
                request_type = result.get("request_type", "conversion")

                if not isinstance(data, dict):
                    logger.error(f"Invalid data format from currency service: {type(data)}")
                    return ChatResponse(
                        message="Sorry, I couldn't process that currency conversion request.",
                        confidence_score=0.0,
                    )

                if request_type == "rate":
                    base_currency = data.get("base_code", "USD")
                    target_currency = data.get("target_code", "EUR")
                    rate = data.get("rate", 0.0)
                    message = f"Exchange rate: 1 {base_currency} = {rate:.4f} {target_currency}"
                else:
                    # Handle conversion request
                    original = data.get("original", {})
                    converted = data.get("converted", {})
                    message = (
                        f"{original.get('amount', 0):.2f} {original.get('currency', 'USD')} = "
                        f"{converted.get('amount', 0):.2f} {converted.get('currency', 'EUR')}"
                    )

                quick_replies = [
                    QuickReply(text="Convert different amount", action="currency_convert"),
                    QuickReply(text="Other currencies", action="currency_list"),
                ]

                if data.get("original", {}).get("amount", 0) > 0:
                    quick_replies.insert(
                        0, QuickReply(text="Show rate only", action="currency_rate_only")
                    )

                return ChatResponse(
                    message=message, confidence_score=0.9, quick_replies=quick_replies
                )

            return ChatResponse(
                message="Sorry, I couldn't process that currency conversion request.",
                confidence_score=0.0,
            )

        except Exception as e:
            logger.error(f"Currency handler error: {e}")
            return ChatResponse(
                message="Sorry, I couldn't process that currency request.",
                confidence_score=0.0,
            )

    async def _handle_weather_request(
        self, user_message: str, context: ConversationContext
    ) -> ChatResponse:
        """Handle weather-related requests."""
        try:
            # Extract destination from context or message
            destination = context.destination or self._extract_destination(user_message)

            if not destination:
                return ChatResponse(
                    message="Please specify a destination for weather information.",
                    confidence_score=0.0,
                    quick_replies=[
                        QuickReply(text="Weather for Paris", action="weather_paris"),
                        QuickReply(text="Weather for Tokyo", action="weather_tokyo"),
                        QuickReply(text="Weather for New York", action="weather_nyc"),
                    ],
                )

            weather_data = await weather_service.get_weather_data(destination, context.travel_dates)

            if weather_data:
                message = f"Weather for {destination}: {weather_data.get('description', 'Information available')}"
                quick_replies = [
                    QuickReply(text="Detailed forecast", action="weather_forecast"),
                    QuickReply(text="Weather for different city", action="weather_other"),
                ]
            else:
                message = f"Sorry, I couldn't get weather information for {destination}."
                quick_replies = []

            return ChatResponse(message=message, confidence_score=0.8, quick_replies=quick_replies)

        except Exception as e:
            logger.error(f"Weather handler error: {e}")
            return ChatResponse(
                message="Sorry, I couldn't get weather information right now.",
                confidence_score=0.0,
            )

    async def _handle_cultural_request(
        self, user_message: str, context: ConversationContext
    ) -> ChatResponse:
        """Handle cultural insights and etiquette requests."""
        try:
            destination = context.destination or self._extract_destination(user_message)

            if not destination:
                return ChatResponse(
                    message="Please specify a destination for cultural information.",
                    confidence_score=0.0,
                    quick_replies=[
                        QuickReply(text="Cultural tips for Japan", action="cultural_japan"),
                        QuickReply(text="Cultural tips for France", action="cultural_france"),
                        QuickReply(text="Cultural tips for Italy", action="cultural_italy"),
                    ],
                )

            cultural_insights = await qloo_service.get_cultural_insights(
                destination, context.trip_purpose or "leisure"
            )

            if cultural_insights:
                message = f"Cultural insights for {destination}: {cultural_insights.get('summary', 'Information available')}"
                quick_replies = [
                    QuickReply(text="More cultural tips", action="cultural_more"),
                    QuickReply(text="Etiquette guide", action="cultural_etiquette"),
                ]
            else:
                message = f"Sorry, I couldn't get cultural information for {destination}."
                quick_replies = []

            return ChatResponse(message=message, confidence_score=0.8, quick_replies=quick_replies)

        except Exception as e:
            logger.error(f"Cultural handler error: {e}")
            return ChatResponse(
                message="Sorry, I couldn't get cultural information right now.",
                confidence_score=0.0,
            )

    async def _handle_wardrobe_request(
        self,
        user_message: str,
        context: ConversationContext,
        conversation_history: list[dict[str, str]],
        user_profile: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """Handle wardrobe planning and packing requests."""
        try:
            # Get weather data for packing recommendations
            destination = context.destination or self._extract_destination(user_message)
            weather_data = None
            if destination:
                weather_data = await weather_service.get_weather_data(
                    destination, context.travel_dates
                )

            # Generate AI response for wardrobe planning
            ai_response = await openai_service.generate_response(
                user_message=user_message,
                conversation_history=conversation_history,
                weather_context=weather_data,
                user_profile=user_profile,
                context_type="wardrobe",
            )

            # Add wardrobe-specific quick replies
            quick_replies = [
                QuickReply(text="Packing checklist", action="wardrobe_checklist"),
                QuickReply(text="Style recommendations", action="wardrobe_style"),
                QuickReply(text="Weather-appropriate items", action="wardrobe_weather"),
            ]

            return ChatResponse(
                message=ai_response.message,
                confidence_score=ai_response.confidence_score,
                quick_replies=quick_replies,
            )

        except Exception as e:
            logger.error(f"Wardrobe handler error: {e}")
            return ChatResponse(
                message="Sorry, I couldn't help with wardrobe planning right now.",
                confidence_score=0.0,
            )

    async def _handle_style_request(
        self,
        user_message: str,
        context: ConversationContext,
        conversation_history: list[dict[str, str]],
        user_profile: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """Handle style and fashion etiquette requests."""
        try:
            # Get cultural insights for style recommendations
            destination = context.destination or self._extract_destination(user_message)
            cultural_insights = None
            if destination:
                cultural_insights = await qloo_service.get_cultural_insights(
                    destination, context.trip_purpose or "leisure"
                )

            # Generate AI response for style advice
            ai_response = await openai_service.generate_response(
                user_message=user_message,
                conversation_history=conversation_history,
                cultural_context=cultural_insights,
                user_profile=user_profile,
                context_type="style",
            )

            # Add style-specific quick replies
            quick_replies = [
                QuickReply(text="Dress code guide", action="style_dresscode"),
                QuickReply(text="Local fashion tips", action="style_local"),
                QuickReply(text="Formal vs casual", action="style_formal"),
            ]

            return ChatResponse(
                message=ai_response.message,
                confidence_score=ai_response.confidence_score,
                quick_replies=quick_replies,
            )

        except Exception as e:
            logger.error(f"Style handler error: {e}")
            return ChatResponse(
                message="Sorry, I couldn't help with style advice right now.",
                confidence_score=0.0,
            )

    async def _handle_destination_request(
        self,
        user_message: str,
        context: ConversationContext,
        conversation_history: list[dict[str, str]],
        user_profile: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """Handle destination-specific requests."""
        try:
            destination = context.destination or self._extract_destination(user_message)

            if not destination:
                return ChatResponse(
                    message="Please specify a destination for information.",
                    confidence_score=0.0,
                    quick_replies=[
                        QuickReply(text="Tell me about Paris", action="destination_paris"),
                        QuickReply(text="Tell me about Tokyo", action="destination_tokyo"),
                        QuickReply(text="Tell me about Rome", action="destination_rome"),
                    ],
                )

            # Gather comprehensive destination data using safe wrappers
            weather_data = await self._safe_api_call(
                weather_service.get_weather_data, destination, context.travel_dates
            )
            cultural_insights = await self._safe_api_call(
                qloo_service.get_cultural_insights, destination, context.trip_purpose or "leisure"
            )

            # Generate AI response for destination
            ai_response = await openai_service.generate_response(
                user_message=user_message,
                conversation_history=conversation_history,
                weather_context=weather_data,
                cultural_context=cultural_insights,
                user_profile=user_profile,
                context_type="destination",
            )

            # Add destination-specific quick replies
            quick_replies = [
                QuickReply(
                    text=f"More about {destination}",
                    action=f"destination_more_{destination.lower()}",
                ),
                QuickReply(
                    text="Weather in " + destination, action=f"weather_{destination.lower()}"
                ),
                QuickReply(
                    text="Cultural tips for " + destination,
                    action=f"cultural_{destination.lower()}",
                ),
            ]

            return ChatResponse(
                message=ai_response.message,
                confidence_score=ai_response.confidence_score,
                quick_replies=quick_replies,
            )

        except Exception as e:
            logger.error(f"Destination handler error: {e}")
            return ChatResponse(
                message="Sorry, I couldn't get destination information right now.",
                confidence_score=0.0,
            )

    async def _handle_logistics_request(
        self,
        user_message: str,
        context: ConversationContext,
        conversation_history: list[dict[str, str]],
        user_profile: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """Handle comprehensive travel logistics and planning requests."""
        try:
            # Extract travel details from the message
            destination = context.destination or self._extract_destination(user_message)
            travel_dates = context.travel_dates or self._extract_travel_dates(user_message)

            # Gather comprehensive data for logistics planning
            weather_data = None
            cultural_insights = None

            if destination:
                weather_data = await self._safe_api_call(
                    weather_service.get_weather_data, destination, travel_dates
                )
                cultural_insights = await self._safe_api_call(
                    qloo_service.get_cultural_insights,
                    destination,
                    context.trip_purpose or "leisure",
                )

            # Generate comprehensive logistics response
            ai_response = await openai_service.generate_response(
                user_message=user_message,
                conversation_history=conversation_history,
                weather_context=weather_data,
                cultural_context=cultural_insights,
                user_profile=user_profile,
                context_type="logistics",
            )

            # Add logistics-specific quick replies
            quick_replies = [
                QuickReply(text="Visa requirements", action="logistics_visa"),
                QuickReply(text="Vaccination info", action="logistics_vaccination"),
                QuickReply(text="Currency exchange", action="logistics_currency"),
                QuickReply(text="Weather forecast", action="logistics_weather"),
            ]

            return ChatResponse(
                message=ai_response.message,
                confidence_score=ai_response.confidence_score,
                quick_replies=quick_replies,
            )

        except Exception as e:
            logger.error(f"Logistics handler error: {e}")
            return ChatResponse(
                message="Sorry, I couldn't help with travel logistics right now.",
                confidence_score=0.0,
            )

    async def _handle_general_request(
        self,
        user_message: str,
        context: ConversationContext,
        conversation_history: list[dict[str, str]],
        user_profile: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """Handle general travel recommendations (default handler)."""
        try:
            # Parse trip context from user message
            trip_context = self._parse_trip_context(user_message, context)

            # Gather data from external APIs
            cultural_insights = await self._safe_api_call(
                qloo_service.get_cultural_insights,
                trip_context.get("destination"),
                trip_context.get("trip_purpose", "leisure"),
            )

            weather_data = await self._safe_api_call(
                weather_service.get_weather_data,
                trip_context.get("destination"),
                trip_context.get("travel_dates"),
            )

            # Generate AI response with all context
            ai_response = await openai_service.generate_response(
                user_message=user_message,
                conversation_history=conversation_history,
                cultural_context=cultural_insights,
                weather_context=weather_data,
                user_profile=user_profile,
            )

            # Enhance response with additional context
            enhanced_response = self._enhance_response(ai_response, trip_context)

            return enhanced_response

        except Exception as e:
            logger.error(f"General handler error: {e}")
            return ChatResponse(
                message="Sorry, I couldn't process your request right now.",
                confidence_score=0.0,
            )

    def _extract_destination(self, user_message: str) -> str | None:
        """Extract destination from user message."""
        destination_patterns = [
            r".*going to\s+([A-Za-z\s]+?)(?:\s+for|\s+on|\s+in|\s+to|\s+with|\s+next|\s+this|\s+that|[.?!,]|$)",
            r".*visiting\s+([A-Za-z\s]+?)(?:\s+for|\s+on|\s+in|\s+to|\s+with|\s+next|\s+this|\s+that|[.?!,]|$)",
            r".*trip to\s+([A-Za-z\s]+?)(?:\s+for|\s+on|\s+in|\s+to|\s+with|\s+next|\s+this|\s+that|[.?!,]|$)",
            r".*in\s+([A-Za-z\s]+?)(?:\s+for|\s+on|\s+to|\s+with|\s+next|\s+this|\s+that|[.?!,]|$)",
            r".*to\s+([A-Za-z\s]+?)(?:\s+for|\s+on|\s+in|\s+to|\s+with|\s+next|\s+this|\s+that|[.?!,]|$)",
            r".*I'm in\s+([A-Za-z\s]+?)(?:\s+for|\s+on|\s+to|\s+with|\s+next|\s+this|\s+that|[.?!,]|$)",
        ]

        for pattern in destination_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_travel_dates(self, user_message: str) -> list[str] | None:
        """Extract travel dates from user message."""
        # Look for date patterns like "2025-09-02 until 2025-09-09" or "from 2025-09-02 to 2025-09-09"
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})\s+until\s+(\d{4}-\d{2}-\d{2})",
            r"from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})",
            r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                return [match.group(1), match.group(2)]

        return None

    async def _safe_api_call(self, api_func, *args, **kwargs):
        """Safely call external APIs with error handling."""
        try:
            return await api_func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("API call error: %s", type(e).__name__)
            return None

    async def _return_none(self):
        """Helper method to return None for failed API calls."""
        return None

    def _parse_trip_context(
        self, user_message: str, context: ConversationContext
    ) -> dict[str, Any]:
        """Parse trip context from user message and conversation context."""
        trip_context = {}

        # Extract destination from user message if not in context
        if not context.destination:
            destination = self._extract_destination(user_message)
            if destination:
                trip_context["destination"] = destination

        # Extract trip purpose from user message
        trip_purpose_patterns = {
            "business": [r"business", r"work", r"meeting", r"conference"],
            "formal": [r"formal", r"wedding", r"ceremony", r"event"],
            "active": [r"hiking", r"skiing", r"sports", r"adventure", r"outdoor"],
        }

        for purpose, patterns in trip_purpose_patterns.items():
            if any(re.search(pattern, user_message, re.IGNORECASE) for pattern in patterns):
                trip_context["trip_purpose"] = purpose
                break

        # Use context values as fallback
        if context.destination:
            trip_context["destination"] = context.destination
        if context.travel_dates:
            trip_context["travel_dates"] = context.travel_dates
        if context.trip_purpose:
            trip_context["trip_purpose"] = context.trip_purpose

        return trip_context

    def _enhance_response(self, ai_response: ChatResponse, context: dict[str, Any]) -> ChatResponse:
        """Enhance AI response with additional context and suggestions."""
        # Add context-specific quick replies
        if context.get("destination"):
            ai_response.quick_replies.append(
                QuickReply(text=f"More about {context['destination']}", action="destination_info")
            )

        # Add weather-related quick replies if weather data is available
        if context.get("weather"):
            ai_response.quick_replies.append(
                QuickReply(text="Weather details", action="weather_info")
            )

        # Add cultural quick replies if cultural data is available
        if context.get("cultural_insights"):
            ai_response.quick_replies.append(
                QuickReply(text="Cultural tips", action="cultural_info")
            )

        return ai_response

    # Backward compatibility method
    async def generate_travel_recommendations(
        self,
        user_message: str,
        context: ConversationContext,
        conversation_history: list[dict[str, str]],
        user_profile: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """Backward compatibility method that routes to the new routing system."""
        return await self.route_message(user_message, context, conversation_history, user_profile)


# Singleton instance
orchestrator_service = TravelOrchestratorService()
