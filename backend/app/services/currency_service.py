import httpx
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.cache import redis_client

logger = logging.getLogger(__name__)

class CurrencyService:
    def __init__(self):
        self.base_url = settings.EXCHANGE_BASE_URL
        self.api_key = settings.EXCHANGE_API_KEY
        self.timeout = 10.0
    
    async def get_exchange_rates(self, base_currency: str = "USD") -> Optional[Dict[str, Any]]:
        """Get current exchange rates"""
        
        cache_key = f"exchange_rates:{base_currency}"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/{base_currency}")
                response.raise_for_status()
                
                data = response.json()
                rates_data = {
                    "base": data["base"],
                    "rates": data["rates"],
                    "last_updated": data["date"]
                }
                
                # Cache for 1 hour
                await redis_client.setex(cache_key, 3600, rates_data)
                
                return rates_data
                
        except Exception as e:
            logger.error(f"Currency service error: {str(e)}")
            return None
    
    async def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Optional[Dict[str, Any]]:
        """Convert currency amounts"""
        
        rates = await self.get_exchange_rates(from_currency)
        if not rates:
            return None
        
        try:
            if to_currency not in rates["rates"]:
                return None
            
            conversion_rate = rates["rates"][to_currency]
            converted_amount = round(amount * conversion_rate, 2)
            
            return {
                "original": {"amount": amount, "currency": from_currency},
                "converted": {"amount": converted_amount, "currency": to_currency},
                "rate": conversion_rate,
                "last_updated": rates["last_updated"]
            }
            
        except Exception as e:
            logger.error(f"Currency conversion error: {str(e)}")
            return None

# Singleton instance
currency_service = CurrencyService() 