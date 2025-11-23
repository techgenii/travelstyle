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

"""Weather service for TravelStyle AI:
Handles weather data retrieval and clothing recommendations."""

import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import settings
from app.services.supabase import enhanced_supabase_cache

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for retrieving weather data and generating clothing recommendations."""

    # pylint: disable=too-few-public-methods

    def __init__(self):
        """Initialize the WeatherService with API credentials and timeout."""
        self.base_url = settings.VISUALCROSSING_BASE_URL
        self.api_key = settings.VISUALCROSSING_API_KEY
        self.timeout = 15.0

    async def get_weather_data(
        self,
        destination: str,
        dates: list[str] | None = None,
        state: str | None = None,
        country: str | None = None,
    ) -> dict[str, Any] | None:
        """Get comprehensive weather data for destination using Visual Crossing API.

        Args:
            destination: The destination location (city name, address, or lat,lon).
            dates: Optional list of dates for date range queries.
            state: Optional state (used for building location string).
            country: Optional country (used for building location string).

        Returns:
            Weather data dictionary or None if error.
        """
        # Check cache first
        cached_data = await enhanced_supabase_cache.get_weather_cache(destination)
        if cached_data:
            return cached_data

        try:
            # Build location string - Visual Crossing accepts addresses directly
            location_parts = [destination]
            if state:
                location_parts.append(state)
            if country:
                location_parts.append(country)
            location = ", ".join(location_parts)

            # Build URL with dates in the path (not query params)
            # Format: /timeline/{location} or /timeline/{location}/{date1} or /timeline/{location}/{date1}/{date2}
            url = f"{self.base_url}{location}"

            # Add dates to URL path if provided
            if dates and len(dates) >= 1:
                url = f"{url}/{dates[0]}"
                if len(dates) >= 2:
                    url = f"{url}/{dates[1]}"

            params = {
                "key": self.api_key,
                "unitGroup": "us",
                "include": "current,days,hours",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                current = data.get("currentConditions", {})
                days = data.get("days", [])

                if not current and not days:
                    return None

                # Process current conditions
                current_weather = None
                if current:
                    current_weather = {
                        "coord": {
                            "lon": data.get("longitude", 0),
                            "lat": data.get("latitude", 0),
                        },
                        "weather": [
                            {
                                "main": current.get("conditions", ""),
                                "description": current.get("conditions", ""),
                                "icon": self._map_conditions_to_icon(current.get("conditions", "")),
                            }
                        ],
                        "main": {
                            "temp": current.get("temp", 0),
                            "feels_like": current.get("feelslike", current.get("temp", 0)),
                            "humidity": current.get("humidity", 0),
                            "pressure": current.get("pressure", 0),
                        },
                        "wind": {
                            "speed": current.get("windspeed", 0),
                            "deg": current.get("winddir", 0),
                        },
                        "clouds": {"all": current.get("cloudcover", 0)},
                        "visibility": current.get("visibility", 10000),
                        "dt": current.get("datetimeEpoch", 0),
                        "timezone": data.get("timezone", ""),
                        "name": data.get("resolvedAddress", ""),
                    }

                # Process forecast
                forecast_data = None
                if days:
                    daily_forecasts = []
                    detailed_forecasts = []

                    for day in days[:7]:  # Limit to 7 days
                        # Daily summary
                        daily_forecasts.append(
                            {
                                "date": day.get("datetime", ""),
                                "temp_min": day.get("tempmin", 0),
                                "temp_max": day.get("tempmax", 0),
                                "humidity_min": day.get("humidity", 0),
                                "humidity_max": day.get("humidity", 0),
                                "weather_descriptions": [day.get("conditions", "")],
                                "conditions": day.get("conditions", ""),
                                "precipitation_chance": day.get("precipprob", 0),
                            }
                        )

                        # Hourly data for this day
                        hours = day.get("hours", [])
                        for hour in hours:
                            detailed_forecasts.append(
                                {
                                    "dt": hour.get("datetimeEpoch", 0),
                                    "main": {
                                        "temp": hour.get("temp", 0),
                                        "feels_like": hour.get("feelslike", hour.get("temp", 0)),
                                        "temp_min": hour.get("temp", 0),
                                        "temp_max": hour.get("temp", 0),
                                        "pressure": hour.get("pressure", 0),
                                        "humidity": hour.get("humidity", 0),
                                    },
                                    "weather": [
                                        {
                                            "main": hour.get("conditions", ""),
                                            "description": hour.get("conditions", ""),
                                        }
                                    ],
                                    "wind": {
                                        "speed": hour.get("windspeed", 0),
                                        "deg": hour.get("winddir", 0),
                                    },
                                    "pop": hour.get("precipprob", 0) / 100.0,
                                    "dt_txt": hour.get("datetime", ""),
                                }
                            )

                    temp_mins = [f["temp_min"] for f in daily_forecasts]
                    temp_maxs = [f["temp_max"] for f in daily_forecasts]
                    precip_chances = [f["precipitation_chance"] for f in daily_forecasts]

                    forecast_data = {
                        "list": detailed_forecasts,
                        "city": {
                            "name": data.get("resolvedAddress", ""),
                            "coord": {
                                "lat": data.get("latitude", 0),
                                "lon": data.get("longitude", 0),
                            },
                            "timezone": data.get("timezone", ""),
                        },
                        "daily_forecasts": daily_forecasts,
                        "temp_range": {
                            "min": min(temp_mins) if temp_mins else 0,
                            "max": max(temp_maxs) if temp_maxs else 0,
                        },
                        "precipitation_chance": max(precip_chances) if precip_chances else 0,
                    }

                weather_data = {
                    "current": current_weather,
                    "forecast": forecast_data,
                    "destination": destination,
                    "retrieved_at": datetime.now(UTC).isoformat(),
                }

                # Cache for 1 hour
                await enhanced_supabase_cache.set_weather_cache(destination, weather_data, 1)

                return weather_data

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Weather service error: %s", type(e).__name__)
            return None

    def _map_conditions_to_icon(self, conditions: str) -> str:
        """Map Visual Crossing conditions to icon codes.

        Args:
            conditions: Weather conditions string from Visual Crossing API.

        Returns:
            Icon code string.
        """
        if not conditions:
            return "02d"
        conditions_lower = conditions.lower()
        if "clear" in conditions_lower or "sunny" in conditions_lower:
            return "01d"
        elif "cloud" in conditions_lower:
            return "03d"
        elif "rain" in conditions_lower:
            return "09d"
        elif "snow" in conditions_lower:
            return "13d"
        elif "thunder" in conditions_lower:
            return "11d"
        else:
            return "02d"

    def _calculate_precipitation_chance(self, conditions: list[str]) -> int:
        """Calculate precipitation chance from conditions.

        Args:
            conditions: List of weather conditions.

        Returns:
            Precipitation chance as percentage.
        """
        rain_conditions = ["Rain", "Drizzle", "Thunderstorm", "Snow"]
        rain_count = sum(1 for condition in conditions if condition in rain_conditions)
        return int((rain_count / len(conditions)) * 100) if conditions else 0


# Singleton instance
weather_service = WeatherService()
