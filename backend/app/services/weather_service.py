import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.cache import redis_client

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.api_key = settings.OPENWEATHER_API_KEY
        self.timeout = 15.0
    
    async def get_weather_data(
        self,
        destination: str,
        dates: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive weather data for destination"""
        
        cache_key = f"weather:{destination}:{dates}"
        cached_data = await redis_client.get(cache_key)
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
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
            # Cache for 30 minutes
            await redis_client.setex(cache_key, 1800, weather_data)
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Weather service error: {str(e)}")
            return None
    
    async def _get_current_weather(self, destination: str) -> Optional[Dict[str, Any]]:
        """Get current weather conditions"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": destination,
                        "appid": self.api_key,
                        "units": "metric"
                    }
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
                    "pressure": data["main"]["pressure"]
                }
                
        except Exception as e:
            logger.error(f"Current weather error: {str(e)}")
            return None
    
    async def _get_forecast(self, destination: str) -> Optional[Dict[str, Any]]:
        """Get 5-day weather forecast"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "q": destination,
                        "appid": self.api_key,
                        "units": "metric"
                    }
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
                            daily_forecasts.append({
                                "date": current_date,
                                "temp_min": min(daily_temps),
                                "temp_max": max(daily_temps),
                                "conditions": max(set(daily_conditions), key=daily_conditions.count),
                                "precipitation_chance": self._calculate_precipitation_chance(daily_conditions)
                            })
                        
                        current_date = date_str
                        daily_temps = []
                        daily_conditions = []
                    
                    daily_temps.append(item["main"]["temp"])
                    daily_conditions.append(item["weather"][0]["main"])
                
                return {
                    "daily_forecasts": daily_forecasts[:7],  # 7 days max
                    "temp_range": {
                        "min": min([f["temp_min"] for f in daily_forecasts[:7]]),
                        "max": max([f["temp_max"] for f in daily_forecasts[:7]])
                    },
                    "precipitation_chance": max([f["precipitation_chance"] for f in daily_forecasts[:7]]) if daily_forecasts else 0
                }
                
        except Exception as e:
            logger.error(f"Forecast error: {str(e)}")
            return None
    
    def _calculate_precipitation_chance(self, conditions: List[str]) -> int:
        """Calculate precipitation chance from conditions"""
        rain_conditions = ["Rain", "Drizzle", "Thunderstorm", "Snow"]
        rain_count = sum(1 for condition in conditions if condition in rain_conditions)
        return int((rain_count / len(conditions)) * 100) if conditions else 0
    
    def _generate_clothing_recommendations(
        self,
        current: Dict[str, Any],
        forecast: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate clothing recommendations based on weather"""
        
        recommendations = {
            "layers": [],
            "footwear": [],
            "accessories": [],
            "materials": [],
            "special_considerations": []
        }
        
        if not current:
            return recommendations
        
        temp = current["temperature"]
        feels_like = current["feels_like"]
        
        # Temperature-based recommendations
        if temp < 0:
            recommendations["layers"].extend(["Heavy winter coat", "Thermal underwear", "Warm sweater"])
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
            recommendations["layers"].extend(["Light clothing", "T-shirts", "Shorts or light pants"])
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
            recommendations["materials"].extend(["Breathable fabrics", "Moisture-wicking materials"])
            recommendations["special_considerations"].append("High humidity - choose breathable clothing")
        
        return recommendations

# Singleton instance
weather_service = WeatherService() 