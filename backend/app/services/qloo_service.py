import httpx
import logging
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.cache import redis_client

logger = logging.getLogger(__name__)

class QlooService:
    def __init__(self):
        self.base_url = settings.QLOO_BASE_URL
        self.api_key = settings.QLOO_API_KEY
        self.timeout = 30.0
        
    async def get_cultural_insights(
        self,
        destination: str,
        context: str = "leisure",
        categories: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cultural insights for destination"""
        
        if categories is None:
            categories = ['fashion', 'etiquette', 'social_norms']
        
        # Check cache first
        cache_key = f"cultural_insights:{destination}:{context}"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cultural-insights",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "location": destination,
                        "context": context,
                        "categories": categories
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                processed_data = self._process_cultural_data(data, destination)
                
                # Cache for 24 hours
                await redis_client.setex(cache_key, 86400, processed_data)
                
                return processed_data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Qloo API HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException:
            logger.error("Qloo API timeout")
        except Exception as e:
            logger.error(f"Qloo API error: {str(e)}")
        
        # Return fallback data
        return self._get_fallback_cultural_data(destination)
    
    async def get_style_recommendations(
        self,
        destination: str,
        user_preferences: Dict[str, Any],
        occasion: str,
        weather_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get style recommendations based on location and preferences"""
        
        cache_key = f"style_recs:{destination}:{occasion}:{hash(str(user_preferences))}"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "location": destination,
                    "user_profile": {
                        "style_preferences": user_preferences.get("style", {}),
                        "body_type": user_preferences.get("body_type"),
                        "budget_range": user_preferences.get("budget")
                    },
                    "occasion": occasion
                }
                
                if weather_data:
                    payload["weather_conditions"] = weather_data
                
                response = await client.post(
                    f"{self.base_url}/style-recommendations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                processed_data = self._process_style_data(data)
                
                # Cache for 6 hours
                await redis_client.setex(cache_key, 21600, processed_data)
                
                return processed_data
                
        except Exception as e:
            logger.error(f"Qloo style recommendations error: {str(e)}")
            return self._get_fallback_style_data(destination)
    
    def _process_cultural_data(self, qloo_response: Dict, destination: str) -> Dict[str, Any]:
        """Process and structure Qloo cultural data"""
        return {
            "cultural_insights": {
                "dress_codes": qloo_response.get("etiquette", {}).get("dress_codes", []),
                "color_preferences": qloo_response.get("fashion", {}).get("color_trends", []),
                "style_norms": qloo_response.get("fashion", {}).get("local_styles", []),
                "taboos": qloo_response.get("etiquette", {}).get("fashion_taboos", [])
            },
            "local_context": {
                "formality_level": qloo_response.get("context", {}).get("formality", "moderate"),
                "seasonal_considerations": qloo_response.get("context", {}).get("seasonal", []),
                "cultural_significance": qloo_response.get("context", {}).get("cultural_notes", [])
            },
            "destination": destination,
            "data_source": "qloo"
        }
    
    def _process_style_data(self, qloo_response: Dict) -> Dict[str, Any]:
        """Process and structure Qloo style recommendations"""
        return {
            "style_recommendations": {
                "recommended_styles": qloo_response.get("recommendations", {}).get("styles", []),
                "specific_items": qloo_response.get("recommendations", {}).get("items", []),
                "color_palette": qloo_response.get("recommendations", {}).get("colors", []),
                "accessories": qloo_response.get("recommendations", {}).get("accessories", [])
            },
            "confidence_score": qloo_response.get("confidence", 0.8),
            "data_source": "qloo"
        }
    
    def _get_fallback_cultural_data(self, destination: str) -> Dict[str, Any]:
        """Fallback cultural data when API fails"""
        return {
            "cultural_insights": {
                "dress_codes": ["Smart casual recommended", "Respect local customs"],
                "color_preferences": ["Neutral colors are safe", "Avoid overly bright colors"],
                "style_norms": ["Conservative dress recommended"],
                "taboos": ["Research local dress codes"]
            },
            "local_context": {
                "formality_level": "moderate",
                "seasonal_considerations": ["Check weather conditions"],
                "cultural_significance": ["Be respectful of local customs"]
            },
            "destination": destination,
            "data_source": "fallback"
        }
    
    def _get_fallback_style_data(self, destination: str) -> Dict[str, Any]:
        """Fallback style recommendations when API fails"""
        return {
            "style_recommendations": {
                "recommended_styles": ["Smart casual", "Comfortable walking shoes"],
                "specific_items": ["Versatile pants", "Breathable tops"],
                "color_palette": ["Navy", "White", "Beige"],
                "accessories": ["Comfortable walking shoes", "Light jacket"]
            },
            "confidence_score": 0.5,
            "data_source": "fallback"
        }

# Singleton instance
qloo_service = QlooService() 