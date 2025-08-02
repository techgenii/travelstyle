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

"""
Currency API operations for TravelStyle AI application.
"""

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.services.currency.constants import (
    CACHE_DURATION_HOURS,
    DEFAULT_BASE_CURRENCY,
    DEFAULT_TIMEOUT,
)
from app.services.currency.exceptions import CurrencyAPIError, CurrencyValidationError
from app.services.currency.validators import normalize_currency_code
from app.services.supabase import enhanced_supabase_cache

logger = logging.getLogger(__name__)


class CurrencyAPI:
    """Service for handling currency exchange rates and conversions."""

    def __init__(self):
        """Initialize the currency API service."""
        self.base_url = settings.EXCHANGE_BASE_URL
        self.api_key = settings.EXCHANGE_API_KEY
        self.timeout = DEFAULT_TIMEOUT

    async def get_exchange_rates(
        self, base_currency: str = DEFAULT_BASE_CURRENCY
    ) -> dict[str, Any] | None:
        """Get current exchange rates.

        Args:
            base_currency: The base currency code (default: USD)

        Returns:
            Dictionary containing exchange rates or None if error
        """
        try:
            # Normalize and validate currency code
            normalized_currency = normalize_currency_code(base_currency)

            # Check cache first
            cached_data = await enhanced_supabase_cache.get_currency_cache(normalized_currency)
            if cached_data:
                return cached_data

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Ensure no double slashes
                latest_url = f"{self.base_url}{self.api_key}/latest/{normalized_currency}"
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

                # Cache for specified duration
                await enhanced_supabase_cache.set_currency_cache(
                    normalized_currency, rates_data, CACHE_DURATION_HOURS
                )
                return rates_data

        except CurrencyAPIError:
            # Re-raise validation errors
            raise
        except httpx.RequestError as e:
            logger.error("Currency service request error: %s", type(e).__name__)
            return None
        except httpx.HTTPError as e:
            logger.error("Currency service HTTP error: %s", type(e).__name__)
            return None
        except ValueError as e:
            logger.error("Currency service JSON decode error: %s", type(e).__name__)
            return None
        except Exception as e:
            logger.error("Unexpected error in get_exchange_rates: %s", e)
            return None

    async def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> dict[str, Any] | None:
        """Convert currency amounts using the direct conversion endpoint.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Dictionary containing conversion result or None if error
        """
        try:
            # Validate inputs
            from app.services.currency.validators import validate_currency_request

            validate_currency_request(from_currency, to_currency, amount)

            # Normalize currency codes
            from_curr = normalize_currency_code(from_currency)
            to_curr = normalize_currency_code(to_currency)

            # Get exchange rates
            rates_data = await self.get_exchange_rates(from_curr)
            if not rates_data:
                return None

            conversion_rates = rates_data.get("conversion_rates", {})
            if to_curr not in conversion_rates:
                logger.error(f"Target currency {to_curr} not found in conversion rates")
                return None

            rate = conversion_rates[to_curr]
            converted_amount = amount * rate

            return {
                "original": {"amount": amount, "currency": from_curr},
                "converted": {"amount": converted_amount, "currency": to_curr},
                "rate": rate,
                "last_updated_unix": rates_data.get("last_updated_unix"),
                "last_updated_utc": rates_data.get("last_updated_utc"),
            }

        except (CurrencyAPIError, CurrencyValidationError):
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return None

    async def get_pair_exchange_rate(
        self,
        base_currency: str = DEFAULT_BASE_CURRENCY,
        target_currency: str = DEFAULT_BASE_CURRENCY,
    ) -> dict[str, Any] | None:
        """Get exchange rate for a specific currency pair.

        Args:
            base_currency: Base currency code
            target_currency: Target currency code

        Returns:
            Dictionary containing exchange rate or None if error
        """
        try:
            # Validate currency codes
            base_curr = normalize_currency_code(base_currency)
            target_curr = normalize_currency_code(target_currency)

            # Get exchange rates
            rates_data = await self.get_exchange_rates(base_curr)
            if not rates_data:
                return None

            conversion_rates = rates_data.get("conversion_rates", {})
            if target_curr not in conversion_rates:
                logger.error(f"Target currency {target_curr} not found in conversion rates")
                return None

            return {
                "base_code": base_curr,
                "target_code": target_curr,
                "rate": conversion_rates[target_curr],
                "last_updated_unix": rates_data.get("last_updated_unix"),
                "last_updated_utc": rates_data.get("last_updated_utc"),
            }

        except (CurrencyAPIError, CurrencyValidationError):
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error getting pair exchange rate: {e}")
            return None
