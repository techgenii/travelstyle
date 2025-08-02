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
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.api_key = settings.OPENWEATHER_API_KEY
        self.timeout = 15.0

    async def get_lat_lon_for_city(
        self, city: str, state: str | None = None, country: str | None = None, limit: int = 1
    ):
        """Get latitude and longitude for a city using OpenStreetMap Nominatim API."""
        try:
            # Build the query string
            q_parts = [city]
            if state:
                q_parts.append(state)
            if country:
                q_parts.append(country)
            q = ", ".join(q_parts)

            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": q, "format": "json", "limit": limit}

            # Add User-Agent header (required by Nominatim usage policy)
            headers = {
                "User-Agent": "TravelStyle/1.0"  # Replace with your actual app name
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                if not data:
                    return None, None

                # OpenStreetMap returns lat/lon as strings, convert to float
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.error("Geocoding error: %s", type(e).__name__)
            return None, None

    async def get_weather_data(
        self,
        destination: str,
        dates: list[str] | None = None,  # pylint: disable=unused-argument
        state: str | None = None,
        country: str | None = None,
    ) -> dict[str, Any] | None:
        """Get comprehensive weather data for destination.

        Args:
            destination: The destination location.
            dates: Optional list of dates (unused in current implementation).

        Returns:
            Weather data dictionary or None if error.
        """
        # Check cache first
        cached_data = await enhanced_supabase_cache.get_weather_cache(destination)
        if cached_data:
            return cached_data

        try:
            lat, lon = await self.get_lat_lon_for_city(destination, state, country)
            if lat is None or lon is None:
                logger.error("Could not geocode destination: %s", destination)
                return None

            # Get current weather and forecast
            current_weather = await self._get_current_weather(lat, lon)
            forecast_data = await self._get_forecast(lat, lon)

            if not current_weather:
                return None

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

    async def _get_current_weather(self, lat: float, lon: float) -> dict[str, Any] | None:
        """Get current weather conditions.

        Args:
            lat: Latitude coordinate.
            lon: Longitude coordinate.

        Returns:
            Current weather data or None if error.
        """
        try:
            # Fix: Use correct URL construction
            url = f"{self.base_url}data/2.5/weather"
            params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "imperial"}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                # Return complete current weather data
                return {
                    "coord": {"lon": data["coord"]["lon"], "lat": data["coord"]["lat"]},
                    "weather": [
                        {
                            "id": data["weather"][0]["id"],
                            "main": data["weather"][0]["main"],
                            "description": data["weather"][0]["description"],
                            "icon": data["weather"][0]["icon"],
                        }
                    ],
                    "base": data.get("base", "stations"),
                    "main": {
                        "temp": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "temp_min": data["main"]["temp_min"],
                        "temp_max": data["main"]["temp_max"],
                        "pressure": data["main"]["pressure"],
                        "humidity": data["main"]["humidity"],
                        "sea_level": data["main"].get("sea_level", 0),
                        "grnd_level": data["main"].get("grnd_level", 0),
                    },
                    "visibility": data.get("visibility", 10000),
                    "wind": {"speed": data["wind"]["speed"], "deg": data["wind"]["deg"]},
                    "clouds": {"all": data["clouds"]["all"]},
                    "dt": data["dt"],
                    "sys": {
                        "type": data["sys"].get("type", 0),
                        "id": data["sys"].get("id", 0),
                        "country": data["sys"].get("country", ""),
                        "sunrise": data["sys"].get("sunrise", 0),
                        "sunset": data["sys"].get("sunset", 0),
                    },
                    "timezone": data.get("timezone", 0),
                    "id": data.get("id", 0),
                    "name": data.get("name", ""),
                }

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Current weather error: %s", type(e).__name__)
            return None

    async def _get_forecast(self, lat: float, lon: float) -> dict[str, Any] | None:
        """Get 5-day weather forecast.

        Args:
            lat: Latitude coordinate.
            lon: Longitude coordinate.

        Returns:
            Forecast data or None if error.
        """
        # pylint: disable=too-many-locals
        try:
            # Fix: Use correct URL construction
            url = f"{self.base_url}data/2.5/forecast"
            params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "imperial"}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                # Process detailed forecast data
                detailed_forecasts = []
                daily_forecasts = []

                # Group by day and get daily summaries
                current_date = None
                daily_temps = []
                daily_conditions = []
                daily_humidity = []
                daily_descriptions = []

                for item in data["list"]:
                    # Create detailed forecast entry
                    detailed_forecast = {
                        "dt": item["dt"],
                        "main": {
                            "temp": item["main"]["temp"],
                            "feels_like": item["main"]["feels_like"],
                            "temp_min": item["main"]["temp_min"],
                            "temp_max": item["main"]["temp_max"],
                            "pressure": item["main"]["pressure"],
                            "sea_level": item["main"].get("sea_level", 0),
                            "grnd_level": item["main"].get("grnd_level", 0),
                            "humidity": item["main"]["humidity"],
                            "temp_kf": item["main"].get("temp_kf", 0),
                        },
                        "weather": [
                            {
                                "id": item["weather"][0]["id"],
                                "main": item["weather"][0]["main"],
                                "description": item["weather"][0]["description"],
                                "icon": item["weather"][0]["icon"],
                            }
                        ],
                        "clouds": {"all": item["clouds"]["all"]},
                        "wind": {
                            "speed": item["wind"]["speed"],
                            "deg": item["wind"]["deg"],
                            "gust": item["wind"].get("gust", 0),
                        },
                        "visibility": item.get("visibility", 10000),
                        "pop": item.get("pop", 0),
                        "sys": {"pod": item["sys"]["pod"]},
                        "dt_txt": item["dt_txt"],
                    }
                    detailed_forecasts.append(detailed_forecast)

                    # Process for daily summaries
                    dt = datetime.fromtimestamp(item["dt"])
                    date_str = dt.strftime("%Y-%m-%d")

                    if current_date != date_str:
                        if current_date is not None:
                            daily_forecasts.append(
                                {
                                    "date": current_date,
                                    "temp_min": min(daily_temps),
                                    "temp_max": max(daily_temps),
                                    "humidity_min": min(daily_humidity),
                                    "humidity_max": max(daily_humidity),
                                    "weather_descriptions": list(set(daily_descriptions)),
                                    "conditions": max(
                                        set(daily_conditions), key=daily_conditions.count
                                    ),
                                    "precipitation_chance": self._calculate_precipitation_chance(
                                        daily_conditions
                                    ),
                                }
                            )
                        current_date = date_str
                        daily_temps = []
                        daily_conditions = []
                        daily_humidity = []
                        daily_descriptions = []

                    daily_temps.append(item["main"]["temp"])
                    daily_conditions.append(item["weather"][0]["main"])
                    daily_humidity.append(item["main"]["humidity"])
                    daily_descriptions.append(item["weather"][0]["description"])

                # Add the last day if exists
                if current_date is not None:
                    daily_forecasts.append(
                        {
                            "date": current_date,
                            "temp_min": min(daily_temps),
                            "temp_max": max(daily_temps),
                            "humidity_min": min(daily_humidity),
                            "humidity_max": max(daily_humidity),
                            "weather_descriptions": list(set(daily_descriptions)),
                            "conditions": max(set(daily_conditions), key=daily_conditions.count),
                            "precipitation_chance": self._calculate_precipitation_chance(
                                daily_conditions
                            ),
                        }
                    )

                # Use generators for better performance
                temp_mins = (f["temp_min"] for f in daily_forecasts[:7])
                temp_maxs = (f["temp_max"] for f in daily_forecasts[:7])
                precip_chances = (f["precipitation_chance"] for f in daily_forecasts[:7])

                return {
                    "list": detailed_forecasts,
                    "city": data.get("city", {}),
                    "daily_forecasts": daily_forecasts[:7],  # 7 days max
                    "temp_range": {
                        "min": min(temp_mins) if daily_forecasts else 0,
                        "max": max(temp_maxs) if daily_forecasts else 0,
                    },
                    "precipitation_chance": (max(precip_chances) if daily_forecasts else 0),
                }

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Forecast error: %s", type(e).__name__)
            return None

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
