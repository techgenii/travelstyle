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

"""Orchestration service for TravelStyle AI: coordinates external APIs for travel recommendations.
This service gathers data from multiple APIs and generates comprehensive travel recommendations.
"""

import logging
import re
from typing import Any

from app.models.responses import ChatResponse, ConversationContext, QuickReply
from app.services.currency_conversion_service import currency_conversion_service
from app.services.currency_service import currency_service
from app.services.openai.openai_service import openai_service
from app.services.qloo import qloo_service
from app.services.weather import weather_service

logger = logging.getLogger(__name__)


class TravelOrchestratorService:
    """Main orchestration service that coordinates all external APIs."""

    # pylint: disable=too-few-public-methods

    async def generate_travel_recommendations(
        self,
        user_message: str,
        context: ConversationContext,
        conversation_history: list[dict[str, str]],
        user_profile: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """
        Main orchestration function that gathers data from all APIs
        and generates comprehensive travel recommendations.
        """
        try:
            # Check if this is a currency request first
            if currency_conversion_service.is_currency_request(user_message):
                # Check for currency help requests first
                help_response = await currency_conversion_service.handle_currency_help_request(
                    user_message
                )
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

                # Continue with normal currency processing...
                result = await currency_conversion_service.handle_currency_request(user_message)

                if result and result.get("success") and "data" in result:
                    data = result["data"]
                    request_type = result.get("request_type", "conversion")

                    if request_type == "rate":
                        # Handle rate request
                        base_currency = data.get("base_code", "USD")
                        target_currency = data.get("target_code", "EUR")
                        rate = data.get("rate", 0.0)

                        message = f"Exchange rate: 1 {base_currency} = {rate:.4f} {target_currency}"

                        quick_replies = [
                            QuickReply(text="Convert different amount", action="currency_convert"),
                            QuickReply(text="Other currencies", action="currency_list"),
                        ]

                        return ChatResponse(
                            message=message, confidence_score=0.9, quick_replies=quick_replies
                        )
                    elif request_type == "conversion":
                        # Handle conversion request
                        original = data.get("original", {})
                        converted = data.get("converted", {})
                        rate = data.get("rate", 0.0)

                        # Format message to match test expectations
                        message = (
                            f"{original.get('amount', 0):.2f} {original.get('currency', 'USD')} = "
                            f"{converted.get('amount', 0):.2f} {converted.get('currency', 'EUR')}"
                        )

                        quick_replies = [
                            QuickReply(text="Convert different amount", action="currency_convert"),
                            QuickReply(text="Other currencies", action="currency_list"),
                        ]

                        # Add specific quick reply if amount was provided
                        if original.get("amount", 0) > 0:
                            quick_replies.insert(
                                0, QuickReply(text="Show rate only", action="currency_rate_only")
                            )

                        return ChatResponse(
                            message=message, confidence_score=0.9, quick_replies=quick_replies
                        )
                    else:
                        # Handle unknown request types as conversion requests
                        original = data.get("original", {})
                        converted = data.get("converted", {})
                        rate = data.get("rate", 0.0)

                        # Format message to match test expectations
                        message = (
                            f"{original.get('amount', 0):.2f} {original.get('currency', 'USD')} = "
                            f"{converted.get('amount', 0):.2f} {converted.get('currency', 'EUR')}"
                        )

                        quick_replies = [
                            QuickReply(text="Convert different amount", action="currency_convert"),
                            QuickReply(text="Other currencies", action="currency_list"),
                        ]

                        # Add specific quick reply if amount was provided
                        if original.get("amount", 0) > 0:
                            quick_replies.insert(
                                0, QuickReply(text="Show rate only", action="currency_rate_only")
                            )

                        return ChatResponse(
                            message=message, confidence_score=0.9, quick_replies=quick_replies
                        )

                # If currency processing failed, return error response
                return ChatResponse(
                    message="Sorry, I couldn't process that currency conversion request.",
                    confidence_score=0.0,
                )

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

            # Get style recommendations (currently unused but available for future use)
            _ = await self._safe_api_call(
                qloo_service.get_style_recommendations,
                trip_context.get("destination"),
                trip_context.get("trip_purpose", "leisure"),
            )

            # Get exchange rates for currency conversion if needed (currently unused but available for future use)  # noqa: E501
            _ = await self._safe_api_call(currency_service.get_exchange_rates, "USD")

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

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Orchestration error: %s", type(e).__name__)
            return ChatResponse(
                message=(
                    "I apologize, but I'm having trouble processing your request right now. "
                    "Please try again."
                ),
                confidence_score=0.0,
            )

    async def _safe_api_call(self, api_func, *args, **kwargs):
        """Safely call external APIs with error handling."""
        try:
            return await api_func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("API call error: %s", type(e).__name__)
            return await self._return_none()

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
            destination_patterns = [
                r"going to ([A-Za-z\s]+?)(?:\s+for|\s+on|\s+in|\s+to|\s+with|\s+next|\s+this|\s+that|\s+$)",  # noqa: E501
                r"visiting ([A-Za-z\s]+?)(?:\s+for|\s+on|\s+in|\s+to|\s+with|\s+next|\s+this|\s+that|\s+$)",  # noqa: E501
                r"in ([A-Za-z\s]+?)(?:\s+for|\s+on|\s+in|\s+to|\s+with|\s+next|\s+this|\s+that|\s+$)",  # noqa: E501
                r"trip to ([A-Za-z\s]+?)(?:\s+for|\s+on|\s+in|\s+to|\s+with|\s+next|\s+this|\s+that|\s+$)",  # noqa: E501
            ]
            for pattern in destination_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    # Strip whitespace from captured destination
                    destination = match.group(1).strip()
                    trip_context["destination"] = destination
                    break

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


# Singleton instance
orchestrator_service = TravelOrchestratorService()
