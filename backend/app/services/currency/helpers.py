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
Main currency helpers for TravelStyle AI application.
Provides a unified interface for all currency operations.
"""

import logging
from typing import Any

from app.services.currency.api import CurrencyAPI
from app.services.currency.exceptions import (
    CurrencyAPIError,
    CurrencyConversionError,
    CurrencyValidationError,
)
from app.services.currency.formatter import CurrencyFormatter
from app.services.currency.parser import CurrencyParser
from app.services.currency.validators import validate_currency_code

logger = logging.getLogger(__name__)


class CurrencyService:
    """Main currency service class that provides unified access to all currency operations."""

    def __init__(self):
        """Initialize the currency service."""
        self.api = CurrencyAPI()
        self.parser = CurrencyParser()
        self.formatter = CurrencyFormatter()

    # API operations - delegate to CurrencyAPI
    async def get_exchange_rates(self, base_currency: str = "USD") -> dict[str, Any] | None:
        """Get current exchange rates."""
        return await self.api.get_exchange_rates(base_currency)

    async def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> dict[str, Any] | None:
        """Convert currency amounts."""
        return await self.api.convert_currency(amount, from_currency, to_currency)

    async def get_pair_exchange_rate(
        self, base_currency: str = "USD", target_currency: str = "USD"
    ) -> dict[str, Any] | None:
        """Get exchange rate for a specific currency pair."""
        return await self.api.get_pair_exchange_rate(base_currency, target_currency)

    # Parser operations - delegate to CurrencyParser
    def is_currency_request(self, user_input: str) -> bool:
        """Check if a user message is a currency conversion request."""
        return self.parser.is_currency_request(user_input)

    async def parse_currency_request(self, user_message: str) -> dict[str, Any] | None:
        """Parse a currency conversion request using OpenAI."""
        return await self.parser.parse_currency_request(user_message)

    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currency codes."""
        return self.parser.get_supported_currencies()

    # Backward compatibility methods
    def validate_currency_code(self, currency_code: str) -> bool:
        """Validate if a currency code is supported (backward compatibility)."""
        return validate_currency_code(currency_code)

    def _clean_parsed_data(self, data: dict) -> dict:
        """Clean and normalize parsed data (backward compatibility)."""
        return self.parser._clean_parsed_data(data)

    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from text (backward compatibility)."""
        return self.parser._extract_json_from_text(text)

    # Formatter operations - delegate to CurrencyFormatter
    def format_currency_response(
        self,
        original_data: dict,
        converted_data: dict,
        rate: float,
    ) -> str:
        """Format a currency conversion response (backward compatibility)."""
        try:
            from_currency = original_data.get("currency", "")
            to_currency = converted_data.get("currency", "")
            amount = original_data.get("amount", 0)
            converted_amount = converted_data.get("amount", 0)

            # Format the response to match test expectations
            response = (
                f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}\n"
                f"Rate: {rate:.4f}"
            )

            return response

        except Exception as e:
            logger.error(f"Error formatting currency response: {e}")
            return "Sorry, I encountered an error formatting the currency conversion."

    def format_exchange_rate_response(
        self,
        from_currency: str,
        to_currency: str,
        rate: float,
        last_updated: str = None,
    ) -> str:
        """Format an exchange rate response."""
        return self.formatter.format_exchange_rate_response(
            from_currency, to_currency, rate, last_updated
        )

    def format_currency_help_response(self) -> str:
        """Format a currency help response."""
        return self.formatter.format_currency_help_response()

    def format_error_response(self, error_message: str = "Unknown error") -> str:
        """Format an error response."""
        return self.formatter.format_error_response(error_message)

    # High-level operations that combine multiple components
    async def handle_currency_request(self, user_message: str) -> dict[str, Any]:
        """Handle a complete currency request from parsing to response."""
        try:
            # Parse the request
            parsed_data = await self.parse_currency_request(user_message)
            if not parsed_data:
                return {
                    "success": False,
                    "message": self.format_error_response("Could not parse currency request"),
                }

            request_type = parsed_data.get("request_type", "conversion")

            if request_type == "help":
                return {
                    "success": True,
                    "message": self.format_currency_help_response(),
                    "request_type": "help",
                }

            elif request_type == "rate":
                # Handle exchange rate request
                from_currency = parsed_data.get("from_currency")
                to_currency = parsed_data.get("to_currency")

                if not from_currency or not to_currency:
                    return {
                        "success": False,
                        "message": self.format_error_response("Missing currency codes"),
                    }

                rate_data = await self.get_pair_exchange_rate(from_currency, to_currency)
                if not rate_data:
                    return {
                        "success": False,
                        "message": self.format_error_response("Could not fetch exchange rate"),
                    }

                response = self.format_exchange_rate_response(
                    rate_data["base_currency"],
                    rate_data["target_currency"],
                    rate_data["rate"],
                    rate_data.get("last_updated"),
                )

                return {
                    "success": True,
                    "message": response,
                    "request_type": "rate",
                    "data": rate_data,
                }

            elif request_type == "conversion":
                # Handle currency conversion request
                from_currency = parsed_data.get("from_currency")
                to_currency = parsed_data.get("to_currency")
                amount = parsed_data.get("amount")

                if not all([from_currency, to_currency, amount]):
                    return {
                        "success": False,
                        "message": self.format_error_response("Missing required conversion data"),
                    }

                conversion_data = await self.convert_currency(amount, from_currency, to_currency)
                if not conversion_data:
                    return {
                        "success": False,
                        "message": "Exchange rate not available",
                    }

                # Check if rate is present in response
                if "rate" not in conversion_data:
                    return {
                        "success": False,
                        "message": "Invalid response format",
                    }

                response = self.format_currency_response(
                    conversion_data["original"],
                    conversion_data["converted"],
                    conversion_data["rate"],
                )

                return {
                    "success": True,
                    "message": response,
                    "request_type": "conversion",
                    "data": conversion_data,
                }

            else:
                return {
                    "success": False,
                    "message": self.format_error_response("Unknown request type"),
                }

        except (CurrencyValidationError, CurrencyAPIError, CurrencyConversionError) as e:
            logger.error(f"Currency service error: {e}")
            error_message = str(e)
            if "Unsupported currency code" in error_message:
                error_message = "Unsupported currency"
            elif "Invalid from_currency" in error_message or "Invalid to_currency" in error_message:
                error_message = "Unsupported currency"
            return {"success": False, "message": error_message}
        except Exception as e:
            logger.error(f"Unexpected error in handle_currency_request: {e}")
            return {
                "success": False,
                "message": "Error processing currency request",
            }

    async def handle_currency_help_request(self, user_message: str) -> dict[str, Any] | None:
        """Handle currency help requests."""
        help_keywords = ["help", "support", "how", "what", "currency help"]
        user_lower = user_message.lower()

        if any(keyword in user_lower for keyword in help_keywords):
            return {
                "success": True,
                "response": self.format_currency_help_response(),
                "request_type": "help",
            }

        return None
