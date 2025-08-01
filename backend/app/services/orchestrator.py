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

import asyncio
import logging
import re
from typing import Any

from app.models.responses import ChatResponse, ConversationContext, QuickReply
from app.services.currency_conversion_service import currency_conversion_service
from app.services.currency_service import currency_service
from app.services.openai_service import openai_service
from app.services.qloo_service import qloo_service
from app.services.weather_service import weather_service

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

                if result and "rate" in result:
                    # Format the response message
                    original = result["original"]
                    converted = result["converted"]
                    rate = result["rate"]

                    message = f"{original['amount']:.2f} {original['currency']} = {converted['amount']:.2f} {converted['currency']} (Rate: {rate:.4f})"

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
                    return ChatResponse(
                        message="I couldn't understand the currency conversion request. Please specify the currencies and amount clearly.",
                        confidence_score=0.0,
                    )

            # Parse context for API calls
            trip_context = self._parse_trip_context(user_message, context)

            # Gather data from all APIs concurrently
            api_tasks = []

            if trip_context.get("destination"):
                # Cultural insights
                api_tasks.append(
                    self._safe_api_call(
                        qloo_service.get_cultural_insights,
                        trip_context["destination"],
                        trip_context.get("context", "leisure"),
                    )
                )

                # Weather data
                api_tasks.append(
                    self._safe_api_call(
                        weather_service.get_weather_data,
                        trip_context["destination"],
                        trip_context.get("dates"),
                    )
                )

                # Style recommendations
                if user_profile:
                    api_tasks.append(
                        self._safe_api_call(
                            qloo_service.get_style_recommendations,
                            trip_context["destination"],
                            user_profile,
                            trip_context.get("occasion", "leisure"),
                        )
                    )
                else:
                    api_tasks.append(asyncio.create_task(self._return_none()))
            else:
                # No destination specified, skip location-based APIs
                api_tasks = [
                    asyncio.create_task(self._return_none()),
                    asyncio.create_task(self._return_none()),
                    asyncio.create_task(self._return_none()),
                ]

            # Currency data (always fetch for user's home currency)
            home_currency = user_profile.get("home_currency", "USD") if user_profile else "USD"
            api_tasks.append(
                asyncio.create_task(
                    self._safe_api_call(currency_service.get_exchange_rates, home_currency)
                )
            )

            # Execute all API calls concurrently
            cultural_data, weather_data, style_data, currency_data = await asyncio.gather(
                *api_tasks
            )

            # Combine all context data
            enhanced_context = {
                "cultural_intelligence": cultural_data,
                "weather_conditions": weather_data,
                "style_recommendations": style_data,
                "currency_info": currency_data,
                "trip_context": trip_context,
                "user_profile": user_profile,
            }

            # Generate AI response with all context
            ai_response = await openai_service.generate_response(
                user_message=user_message,
                conversation_history=conversation_history,
                cultural_context=cultural_data,
                weather_context=weather_data,
                user_profile=user_profile,
            )

            # Enhance response with additional context
            return self._enhance_response(ai_response, enhanced_context)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Orchestration error: %s", type(e).__name__)
            return ChatResponse(
                message=(
                    "I apologize, but I'm having trouble processing your "
                    "request. Please try again or be more specific about your "
                    "travel plans."
                ),
                confidence_score=0.0,
            )

    async def _safe_api_call(self, api_func, *args, **kwargs):
        """Safely call API functions with error handling."""
        try:
            return await api_func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("API call failed: %s - %s", api_func.__name__, type(e).__name__)
            return None

    async def _return_none(self):
        """Helper function to return None for unused API slots."""
        return None

    def _parse_trip_context(
        self, user_message: str, context: ConversationContext
    ) -> dict[str, Any]:
        """Parse user message and context to extract trip information."""
        trip_context = {
            "destination": context.destination,
            "dates": context.travel_dates,
            "purpose": context.trip_purpose,
            "context": "leisure",  # default
        }
        # Simple keyword detection (could be enhanced with NLP)
        message_lower = user_message.lower()
        # Detect travel purpose/context
        if any(word in message_lower for word in ["business", "work", "meeting", "conference"]):
            trip_context["context"] = "business"
            trip_context["occasion"] = "business"
        elif any(word in message_lower for word in ["formal", "dinner", "wedding", "event"]):
            trip_context["context"] = "formal"
            trip_context["occasion"] = "formal"
        elif any(word in message_lower for word in ["beach", "vacation", "holiday", "leisure"]):
            trip_context["context"] = "leisure"
            trip_context["occasion"] = "leisure"
        elif any(word in message_lower for word in ["hiking", "outdoor", "adventure", "active"]):
            trip_context["context"] = "active"
            trip_context["occasion"] = "active"
        # Try to extract destination from message if not in context
        if not trip_context["destination"]:
            # Simple destination extraction (could be enhanced with NER)
            destination_patterns = [
                r"to ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"visiting ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            ]
            for pattern in destination_patterns:
                match = re.search(pattern, user_message)
                if match:
                    trip_context["destination"] = match.group(1)
                    break
        return trip_context

    def _enhance_response(self, ai_response: ChatResponse, context: dict[str, Any]) -> ChatResponse:
        """Enhance AI response with additional context and suggestions."""
        # Add contextual quick replies based on available data
        if context.get("weather_conditions"):
            ai_response.quick_replies.append(
                QuickReply(text="More weather details", action="get_weather_details")
            )
        if context.get("cultural_intelligence"):
            ai_response.quick_replies.append(
                QuickReply(text="Cultural tips", action="get_cultural_tips")
            )
        if context.get("currency_info"):
            ai_response.quick_replies.append(
                QuickReply(text="Currency help", action="currency_conversion")
            )
        # Add suggestions based on context
        if context.get("trip_context", {}).get("destination"):
            ai_response.suggestions.extend(
                ["Get packing checklist", "Local shopping tips", "Emergency contact info"]
            )
        return ai_response


# Singleton instance
orchestrator_service = TravelOrchestratorService()
