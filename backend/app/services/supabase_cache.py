import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseCacheService:
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    async def get_weather_cache(self, destination: str) -> Optional[Dict[str, Any]]:
        """Get cached weather data for destination"""
        try:
            response = self.client.table('weather_cache').select('*').eq('destination', destination).eq('is_active', True).single().execute()
            if response.data and not self._is_expired(response.data.get('expires_at')):
                return response.data.get('data')
            return None
        except Exception as e:
            logger.error(f"Weather cache get error: {str(e)}")
            return None
    
    async def set_weather_cache(self, destination: str, data: Dict[str, Any], ttl_hours: int = 1) -> bool:
        """Cache weather data for destination"""
        try:
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
            cache_data = {
                'destination': destination,
                'data': data,
                'expires_at': expires_at.isoformat(),
                'is_active': True,
                'created_at': datetime.utcnow().isoformat()
            }
            self.client.table('weather_cache').upsert(cache_data).execute()
            return True
        except Exception as e:
            logger.error(f"Weather cache set error: {str(e)}")
            return False
    
    async def get_cultural_cache(self, destination: str, context: str = "leisure") -> Optional[Dict[str, Any]]:
        """Get cached cultural insights for destination"""
        try:
            response = self.client.table('cultural_insights_cache').select('*').eq('destination', destination).eq('context', context).eq('is_active', True).single().execute()
            if response.data and not self._is_expired(response.data.get('expires_at')):
                return response.data.get('data')
            return None
        except Exception as e:
            logger.error(f"Cultural cache get error: {str(e)}")
            return None
    
    async def set_cultural_cache(self, destination: str, context: str, data: Dict[str, Any], ttl_hours: int = 24) -> bool:
        """Cache cultural insights for destination"""
        try:
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
            cache_data = {
                'destination': destination,
                'context': context,
                'data': data,
                'expires_at': expires_at.isoformat(),
                'is_active': True,
                'created_at': datetime.utcnow().isoformat()
            }
            self.client.table('cultural_insights_cache').upsert(cache_data).execute()
            return True
        except Exception as e:
            logger.error(f"Cultural cache set error: {str(e)}")
            return False
    
    async def get_currency_cache(self, base_currency: str) -> Optional[Dict[str, Any]]:
        """Get cached currency rates"""
        try:
            response = self.client.table('currency_rates_cache').select('*').eq('base_currency', base_currency).eq('is_active', True).single().execute()
            if response.data and not self._is_expired(response.data.get('expires_at')):
                return response.data.get('data')
            return None
        except Exception as e:
            logger.error(f"Currency cache get error: {str(e)}")
            return None
    
    async def set_currency_cache(self, base_currency: str, data: Dict[str, Any], ttl_hours: int = 1) -> bool:
        """Cache currency rates"""
        try:
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
            cache_data = {
                'base_currency': base_currency,
                'data': data,
                'expires_at': expires_at.isoformat(),
                'is_active': True,
                'created_at': datetime.utcnow().isoformat()
            }
            self.client.table('currency_rates_cache').upsert(cache_data).execute()
            return True
        except Exception as e:
            logger.error(f"Currency cache set error: {str(e)}")
            return False
    
    def _is_expired(self, expires_at: str) -> bool:
        """Check if cache entry is expired"""
        try:
            expiry = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            return datetime.utcnow() > expiry
        except Exception:
            return True

# Singleton instance
supabase_cache = SupabaseCacheService() 