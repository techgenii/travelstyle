"""Qloo service for TravelStyle AI: handles cultural insights and style recommendations."""

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.services.supabase_cache import supabase_cache

logger = logging.getLogger(__name__)


class QlooService:
    """Service for interacting with Qloo API for cultural insights and style recommendations."""

    def __init__(self):
        """Initialize the QlooService with API credentials and timeout."""
        self.base_url = settings.QLOO_BASE_URL
        self.api_key = settings.QLOO_API_KEY
        self.timeout = 30.0

    async def get_cultural_insights(
        self, destination: str, context: str = "leisure", categories: list[str] | None = None
    ) -> dict[str, Any] | None:
        """Get cultural insights for destination.

        Args:
            destination: The destination location.
            context: The travel context (default: leisure).
            categories: List of categories to fetch (default: fashion, etiquette, social_norms).

        Returns:
            Dictionary containing cultural insights or None if error.
        """
        if categories is None:
            categories = ["fashion", "etiquette", "social_norms"]

        # Check cache first
        cached_data = await supabase_cache.get_cultural_cache(destination, context)
        if cached_data:
            return cached_data

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cultural-insights",
                    headers={
                        "X-Api-Key": "{self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"location": destination, "context": context, "categories": categories},
                )
                response.raise_for_status()

                data = response.json()
                processed_data = self._process_cultural_data(data, destination)

                # Cache for 24 hours
                await supabase_cache.set_cultural_cache(destination, context, processed_data, 24)

                return processed_data

        except httpx.HTTPStatusError as e:
            logger.error("Qloo API HTTP error: %s - %s", e.response.status_code, e.response.text)
        except httpx.TimeoutException:
            logger.error("Qloo API timeout")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Qloo API error: %s", type(e).__name__)

        # Return fallback data
        return self._get_fallback_cultural_data(destination)

    async def get_style_recommendations(
        self,
        destination: str,
        user_preferences: dict[str, Any],
        occasion: str,
        weather_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Get style recommendations based on location and preferences.

        Args:
            destination: The destination location.
            user_preferences: User's style preferences.
            occasion: The occasion type.
            weather_data: Optional weather data.

        Returns:
            Dictionary containing style recommendations or None if error.
        """
        # Note: Style recommendations not cached in MVP - could add to schema later
        # For now, always fetch fresh data

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "location": destination,
                    "user_profile": {
                        "style_preferences": user_preferences.get("style", {}),
                        "body_type": user_preferences.get("body_type"),
                        "budget_range": user_preferences.get("budget"),
                    },
                    "occasion": occasion,
                }

                if weather_data:
                    payload["weather_conditions"] = weather_data

                response = await client.post(
                    f"{self.base_url}/style-recommendations",
                    headers={
                        "X-Api-Key": "{self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()
                processed_data = self._process_style_data(data)

                # Note: Style recommendations not cached in MVP

                return processed_data

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Qloo style recommendations error: %s", type(e).__name__)
            return self._get_fallback_style_data(destination)

    def _process_cultural_data(self, qloo_response: dict, destination: str) -> dict[str, Any]:
        """Process and structure Qloo cultural data.

        Args:
            qloo_response: Raw response from Qloo API.
            destination: The destination location.

        Returns:
            Processed cultural data dictionary.
        """
        return {
            "cultural_insights": {
                "dress_codes": qloo_response.get("etiquette", {}).get("dress_codes", []),
                "color_preferences": qloo_response.get("fashion", {}).get("color_trends", []),
                "style_norms": qloo_response.get("fashion", {}).get("local_styles", []),
                "taboos": qloo_response.get("etiquette", {}).get("fashion_taboos", []),
            },
            "local_context": {
                "formality_level": qloo_response.get("context", {}).get("formality", "moderate"),
                "seasonal_considerations": qloo_response.get("context", {}).get("seasonal", []),
                "cultural_significance": qloo_response.get("context", {}).get("cultural_notes", []),
            },
            "destination": destination,
            "data_source": "qloo",
        }

    def _process_style_data(self, qloo_response: dict) -> dict[str, Any]:
        """Process and structure Qloo style recommendations.

        Args:
            qloo_response: Raw response from Qloo API.

        Returns:
            Processed style data dictionary.
        """
        return {
            "style_recommendations": {
                "recommended_styles": qloo_response.get("recommendations", {}).get("styles", []),
                "specific_items": qloo_response.get("recommendations", {}).get("items", []),
                "color_palette": qloo_response.get("recommendations", {}).get("colors", []),
                "accessories": qloo_response.get("recommendations", {}).get("accessories", []),
            },
            "confidence_score": qloo_response.get("confidence", 0.8),
            "data_source": "qloo",
        }

    def _get_fallback_cultural_data(self, destination: str) -> dict[str, Any]:
        """Fallback cultural data when API fails.

        Args:
            destination: The destination location (used in return data).

        Returns:
            Fallback cultural data dictionary.
        """
        return {
            "cultural_insights": {
                "dress_codes": ["Smart casual recommended", "Respect local customs"],
                "color_preferences": ["Neutral colors are safe", "Avoid overly bright colors"],
                "style_norms": ["Conservative dress recommended"],
                "taboos": ["Research local dress codes"],
            },
            "local_context": {
                "formality_level": "moderate",
                "seasonal_considerations": ["Check weather conditions"],
                "cultural_significance": ["Be respectful of local customs"],
            },
            "destination": destination,
            "data_source": "fallback",
        }

    def _get_fallback_style_data(self, destination: str) -> dict[str, Any]:
        """Fallback style recommendations when API fails.

        Args:
            destination: The destination location (unused but kept for API consistency).

        Returns:
            Fallback style data dictionary.
        """
        # pylint: disable=unused-argument
        return {
            "style_recommendations": {
                "recommended_styles": ["Smart casual", "Comfortable walking shoes"],
                "specific_items": ["Versatile pants", "Breathable tops"],
                "color_palette": ["Navy", "White", "Beige"],
                "accessories": ["Comfortable walking shoes", "Light jacket"],
            },
            "confidence_score": 0.5,
            "data_source": "fallback",
        }


# Singleton instance
qloo_service = QlooService()
