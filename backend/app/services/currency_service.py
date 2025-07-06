"""Currency service for handling exchange rates and currency conversions."""

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.services.supabase_cache import supabase_cache

logger = logging.getLogger(__name__)

class CurrencyService:
    """Service for handling currency exchange rates and conversions."""

    def __init__(self):
        """Initialize the currency service."""
        self.base_url = settings.EXCHANGE_BASE_URL
        self.api_key = settings.EXCHANGE_API_KEY
        self.timeout = 10.0

    async def get_exchange_rates(self, base_currency: str = "USD") -> dict[str, Any] | None:
        """Get current exchange rates.

        Args:
            base_currency: The base currency code (default: USD)

        Returns:
            Dictionary containing exchange rates or None if error
        """
        # Check cache first
        cached_data = await supabase_cache.get_currency_cache(base_currency)
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
                await supabase_cache.set_currency_cache(base_currency, rates_data, 1)

                return rates_data

        except httpx.RequestError as e:
            logger.error("Currency service request error: %s", str(e))
            return None
        except httpx.HTTPError as e:
            logger.error("Currency service HTTP error: %s", str(e))
            return None
        except ValueError as e:
            logger.error("Currency service JSON decode error: %s", str(e))
            return None

    async def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> dict[str, Any] | None:
        """Convert currency amounts.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Dictionary containing conversion result or None if error
        """
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

        except KeyError as e:
            logger.error("Currency conversion key error: %s", str(e))
            return None
        except TypeError as e:
            logger.error("Currency conversion type error: %s", str(e))
            return None


# Singleton instance
currency_service = CurrencyService()
