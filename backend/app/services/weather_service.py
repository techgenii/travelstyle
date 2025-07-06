"""Weather service for TravelStyle AI:
Handles weather data retrieval and clothing recommendations."""

import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import settings
from app.services.supabase_cache import supabase_cache

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for retrieving weather data and generating clothing recommendations."""

    # pylint: disable=too-few-public-methods

    def __init__(self):
        """Initialize the WeatherService with API credentials and timeout."""
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.api_key = settings.OPENWEATHER_API_KEY
        self.timeout = 15.0

    async def get_weather_data(
        self,
        destination: str,
        dates: list[str] | None = None,  # pylint: disable=unused-argument
    ) -> dict[str, Any] | None:
        """Get comprehensive weather data for destination.

        Args:
            destination: The destination location.
            dates: Optional list of dates (unused in current implementation).

        Returns:
            Weather data dictionary or None if error.
        """
        # Check cache first
        cached_data = await supabase_cache.get_weather_cache(destination)
        if cached_data:
            return cached_data

        try:
            # Get current weather and forecast
            current_weather = await self._get_current_weather(destination)
            forecast_data = await self._get_forecast(destination)

            if not current_weather:
                return None

            weather_data = {
                "current": current_weather,
                "forecast": forecast_data,
                "clothing_recommendations": self._generate_clothing_recommendations(
                    current_weather, forecast_data
                ),
                "destination": destination,
                "retrieved_at": datetime.now(UTC).isoformat(),
            }

            # Cache for 1 hour
            await supabase_cache.set_weather_cache(destination, weather_data, 1)

            return weather_data

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Weather service error: %s", str(e))
            return None

    async def _get_current_weather(self, destination: str) -> dict[str, Any] | None:
        """Get current weather conditions.

        Args:
            destination: The destination location.

        Returns:
            Current weather data or None if error.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={"q": destination, "appid": self.api_key, "units": "metric"},
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                    "wind_speed": data["wind"]["speed"],
                    "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                    "pressure": data["main"]["pressure"],
                }

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Current weather error: %s", str(e))
            return None

    async def _get_forecast(self, destination: str) -> dict[str, Any] | None:
        """Get 5-day weather forecast.

        Args:
            destination: The destination location.

        Returns:
            Forecast data or None if error.
        """
        # pylint: disable=too-many-locals
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={"q": destination, "appid": self.api_key, "units": "metric"},
                )
                response.raise_for_status()

                data = response.json()
                daily_forecasts = []

                # Group by day and get daily summaries
                current_date = None
                daily_temps = []
                daily_conditions = []

                for item in data["list"]:
                    dt = datetime.fromtimestamp(item["dt"])
                    date_str = dt.strftime("%Y-%m-%d")

                    if current_date != date_str:
                        if current_date is not None:
                            daily_forecasts.append(
                                {
                                    "date": current_date,
                                    "temp_min": min(daily_temps),
                                    "temp_max": max(daily_temps),
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

                    daily_temps.append(item["main"]["temp"])
                    daily_conditions.append(item["weather"][0]["main"])

                # Use generators for better performance
                temp_mins = (f["temp_min"] for f in daily_forecasts[:7])
                temp_maxs = (f["temp_max"] for f in daily_forecasts[:7])
                precip_chances = (f["precipitation_chance"] for f in daily_forecasts[:7])

                return {
                    "daily_forecasts": daily_forecasts[:7],  # 7 days max
                    "temp_range": {
                        "min": min(temp_mins) if daily_forecasts else 0,
                        "max": max(temp_maxs) if daily_forecasts else 0,
                    },
                    "precipitation_chance": (max(precip_chances) if daily_forecasts else 0),
                }

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Forecast error: %s", str(e))
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

    def _generate_clothing_recommendations(
        self, current: dict[str, Any], forecast: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Generate clothing recommendations based on weather.

        Args:
            current: Current weather data.
            forecast: Optional forecast data.

        Returns:
            Clothing recommendations dictionary.
        """
        recommendations = {
            "layers": [],
            "footwear": [],
            "accessories": [],
            "materials": [],
            "special_considerations": [],
        }

        if not current:
            return recommendations

        temp = current["temperature"]
        # May be used in future enhancements
        # feels_like = current["feels_like"]

        # Temperature-based recommendations
        if temp < 0:
            recommendations["layers"].extend(
                ["Heavy winter coat", "Thermal underwear", "Warm sweater"]
            )
            recommendations["footwear"].extend(["Insulated boots", "Warm socks"])
            recommendations["accessories"].extend(["Winter hat", "Gloves", "Scarf"])
        elif temp < 10:
            recommendations["layers"].extend(["Warm jacket", "Long pants", "Long sleeves"])
            recommendations["footwear"].extend(["Closed shoes", "Warm socks"])
            recommendations["accessories"].append("Light scarf")
        elif temp < 20:
            recommendations["layers"].extend(["Light jacket or cardigan", "Long pants or jeans"])
            recommendations["footwear"].extend(["Comfortable walking shoes"])
        elif temp < 30:
            recommendations["layers"].extend(
                ["Light clothing", "T-shirts", "Shorts or light pants"]
            )
            recommendations["footwear"].extend(["Breathable shoes", "Sandals"])
            recommendations["accessories"].extend(["Sun hat", "Sunglasses"])
        else:
            recommendations["layers"].extend(["Very light clothing", "Breathable fabrics"])
            recommendations["footwear"].extend(["Open-toe sandals", "Breathable shoes"])
            recommendations["accessories"].extend(["Sun hat", "Sunglasses", "Sunscreen"])
            recommendations["special_considerations"].append("Stay hydrated and seek shade")

        # Weather condition recommendations
        if "rain" in current["description"].lower():
            recommendations["accessories"].extend(["Rain jacket", "Umbrella"])
            recommendations["footwear"].append("Waterproof shoes")
            recommendations["materials"].append("Water-resistant fabrics")

        # Forecast-based recommendations
        if forecast and forecast["precipitation_chance"] > 50:
            recommendations["accessories"].extend(["Pack rain gear", "Waterproof bag"])
            recommendations["special_considerations"].append("High chance of rain during trip")

        # Wind considerations
        if current.get("wind_speed", 0) > 10:
            recommendations["accessories"].append("Windbreaker")
            recommendations["special_considerations"].append("Windy conditions expected")

        # Humidity considerations
        if current.get("humidity", 0) > 80:
            recommendations["materials"].extend(
                ["Breathable fabrics", "Moisture-wicking materials"]
            )
            recommendations["special_considerations"].append(
                "High humidity - choose breathable clothing"
            )

        return recommendations


# Singleton instance
weather_service = WeatherService()
