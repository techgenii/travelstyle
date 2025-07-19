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
        new_currency = base_currency.strip().upper()
        cached_data = await supabase_cache.get_currency_cache(new_currency)
        if cached_data:
            return cached_data

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Ensure no double slashes
                latest_url = f"{self.base_url}{self.api_key}/latest/{new_currency}"
                response = await client.get(latest_url)
                response.raise_for_status()
                try:
                    data = response.json()
                except Exception as e:
                    logger.error("Failed to parse JSON: %s, content: %s", e, response.content)
                    return None

                logger.debug("Currency exchange rate API response: %s", data)
                if not isinstance(data, dict):
                    return None

                rates_data = {
                    "base_code": data["base_code"],
                    "conversion_rates": data["conversion_rates"],
                    "last_updated_unix": data["time_last_update_unix"],
                    "last_updated_utc": data["time_last_update_utc"],
                }

                # Cache for 1 hour
                await supabase_cache.set_currency_cache(new_currency, rates_data, 1)
                return rates_data

        except httpx.RequestError as e:
            logger.error("Currency service request error: %s", type(e).__name__)
            return None
        except httpx.HTTPError as e:
            logger.error("Currency service HTTP error: %s", type(e).__name__)
            return None
        except ValueError as e:
            logger.error("Currency service JSON decode error: %s", type(e).__name__)
            return None

    async def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> dict[str, Any] | None:
        """Convert currency amounts.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Dictionary containing conversion result or None if error
        """
        pair_data = await self.get_pair_exchange_rate(from_currency, to_currency)
        if not pair_data:
            return None

        conversion_rate = pair_data["rate"]
        converted_amount = round(amount * conversion_rate, 2)
        return {
            "original": {"amount": amount, "currency": from_currency},
            "converted": {"amount": converted_amount, "currency": to_currency},
            "rate": conversion_rate,
            "last_updated_unix": pair_data["last_updated_unix"],
            "last_updated_utc": pair_data["last_updated_utc"],
        }

    async def get_pair_exchange_rate(
        self, base_currency: str = "USD", target_currency: str = "USD"
    ) -> dict[str, Any] | None:
        try:
            base_currency = base_currency.strip().upper()
            target_currency = target_currency.strip().upper()
            pair_url = f"{self.base_url}{self.api_key}/pair/{base_currency}/{target_currency}"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(pair_url)
                response.raise_for_status()
                try:
                    data = response.json()
                except Exception as e:
                    logger.error("Failed to parse JSON: %s, content: %s", e, response.content)
                    return None

                logger.debug("Pair exchange rate API response: %s", data)
                if not isinstance(data, dict) or data.get("result") != "success":
                    return None

                return {
                    "base_code": data["base_code"],
                    "target_code": data["target_code"],
                    "rate": data["conversion_rate"],
                    "last_updated_unix": data["time_last_update_unix"],
                    "last_updated_utc": data["time_last_update_utc"],
                }
        except Exception as e:
            logger.error("Pair exchange rate error: %s", type(e).__name__)
            return None


# Singleton instance
currency_service = CurrencyService()
