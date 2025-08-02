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
Currency parsing utilities for TravelStyle AI.
Handles detection and parsing of currency conversion requests.
"""

import json
import logging
import re
from typing import Any

from app.services.currency.constants import SUPPORTED_CURRENCIES
from app.services.currency.validators import validate_currency_code
from app.services.openai.openai_service import openai_service

logger = logging.getLogger(__name__)


class CurrencyParser:
    """Parser for currency conversion requests using OpenAI and regex fallback."""

    def __init__(self):
        """Initialize the CurrencyParser."""
        self.currency_patterns = {
            "USD": r"\b(?:USD|dollars?|bucks?)\b",
            "EUR": r"\b(?:EUR|euros?)\b",
            "GBP": r"\b(?:GBP|pounds?|sterling)\b",
            "JPY": r"\b(?:JPY|yen)\b",
            "CAD": r"\b(?:CAD|canadian\s+dollars?)\b",
            "AUD": r"\b(?:AUD|australian\s+dollars?)\b",
            "CHF": r"\b(?:CHF|swiss\s+francs?)\b",
            "CNY": r"\b(?:CNY|yuan|renminbi)\b",
            "INR": r"\b(?:INR|rupees?)\b",
            "BRL": r"\b(?:BRL|reais?)\b",
        }

    def is_currency_request(self, user_input: str) -> bool:
        """
        Check if the user input is a currency-related request.

        Args:
            user_input: The user's message

        Returns:
            bool: True if the input is a currency request
        """
        if not user_input:
            return False

        input_lower = user_input.lower()

        # Check for currency keywords
        currency_keywords = [
            "convert",
            "exchange",
            "rate",
            "currency",
            "dollar",
            "euro",
            "pound",
            "yen",
            "yuan",
            "rupee",
            "franc",
            "real",
            "dollars",
            "euros",
            "pounds",
        ]

        has_keywords = any(keyword in input_lower for keyword in currency_keywords)

        # Check for currency codes
        has_codes = any(
            re.search(pattern, input_lower, re.IGNORECASE)
            for pattern in self.currency_patterns.values()
        )

        # Check for country names that might indicate currency conversion
        country_names = [
            "us",
            "usa",
            "united states",
            "america",
            "american",
            "europe",
            "european",
            "uk",
            "britain",
            "british",
            "japan",
            "japanese",
            "china",
            "chinese",
            "india",
            "indian",
            "brazil",
            "brazilian",
            "canada",
            "canadian",
            "australia",
            "australian",
            "switzerland",
            "swiss",
        ]

        has_country_names = any(country in input_lower for country in country_names)

        # Check for conversion indicators
        conversion_indicators = ["to", "into", "=", "equals", "worth"]
        has_conversion = any(indicator in input_lower for indicator in conversion_indicators)

        # Check for amounts (numbers)
        has_amounts = bool(re.search(r"\d+(?:\.\d+)?", input_lower))

        # Return True if we have currency codes, country names, or keywords with conversion indicators  # noqa: E501
        return (has_codes and (has_amounts or has_conversion)) or has_keywords or has_country_names

    async def parse_currency_request(self, user_message: str) -> dict[str, Any] | None:
        """Parse a currency conversion request using OpenAI."""
        try:
            # Create a structured prompt for OpenAI
            prompt = f"""
            Parse the following currency conversion request and return a JSON object with the following structure:
            {{
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100.0,
                "request_type": "conversion"
            }}

            If it's a rate request, use:
            {{
                "from_currency": "USD",
                "to_currency": "EUR",
                "request_type": "rate"
            }}

            If it's a help request, use:
            {{
                "request_type": "help"
            }}

            Supported currencies: {", ".join(sorted(SUPPORTED_CURRENCIES))}

            User message: "{user_message}"

            Return only the JSON object, no additional text.
            """  # noqa: E501

            response = await openai_service.get_completion(
                messages=[{"role": "user", "content": prompt}], temperature=0.1, max_tokens=200
            )

            if not response:
                logger.error("No response from OpenAI for currency parsing")
                return None

            # Extract JSON from response
            json_text = self._extract_json_from_text(response)
            if not json_text:
                logger.error("No JSON found in OpenAI response")
                return None

            try:
                parsed_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from OpenAI response: {e}")
                return None

            # Clean and validate the parsed data
            cleaned_data = self._clean_parsed_data(parsed_data)

            # Validate currency codes if present
            if "from_currency" in cleaned_data and not validate_currency_code(
                cleaned_data["from_currency"]
            ):
                logger.error(f"Invalid from_currency: {cleaned_data['from_currency']}")
                return None

            if "to_currency" in cleaned_data and not validate_currency_code(
                cleaned_data["to_currency"]
            ):
                logger.error(f"Invalid to_currency: {cleaned_data['to_currency']}")
                return None

            # For conversion requests, both currencies are required
            if cleaned_data.get("request_type") == "conversion":
                if "from_currency" not in cleaned_data or "to_currency" not in cleaned_data:
                    logger.error("Missing required currency codes for conversion request")
                    return None

            # For rate requests, both currencies are required
            if cleaned_data.get("request_type") == "rate":
                if "from_currency" not in cleaned_data or "to_currency" not in cleaned_data:
                    logger.error("Missing required currency codes for rate request")
                    return None

            return cleaned_data

        except Exception as e:
            logger.error(f"Error parsing currency request: {e}")
            return None

    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from text that may contain additional content."""
        # Look for JSON object in the text
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return ""

    def _clean_parsed_data(self, data: dict) -> dict | None:
        """Clean and normalize parsed data."""
        cleaned = {}

        # Normalize currency codes
        if "from_currency" in data:
            cleaned["from_currency"] = data["from_currency"].strip().upper()

        if "to_currency" in data:
            cleaned["to_currency"] = data["to_currency"].strip().upper()

        # Normalize amount - handle non-numeric amounts
        if "amount" in data:
            try:
                # Handle string amounts
                if isinstance(data["amount"], str):
                    # Remove any non-numeric characters except decimal point and minus
                    cleaned_amount = re.sub(r"[^\d.-]", "", data["amount"])
                    if cleaned_amount:  # Only try to convert if we have numeric content
                        cleaned["amount"] = float(cleaned_amount)
                    else:
                        logger.error(f"Invalid amount: {data['amount']}")
                        return None
                else:
                    cleaned["amount"] = float(data["amount"])
            except (ValueError, TypeError):
                logger.error(f"Invalid amount: {data['amount']}")
                return None

        # Normalize request type
        if "request_type" in data:
            cleaned["request_type"] = data["request_type"].strip().lower()

        return cleaned

    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currencies."""
        return sorted(SUPPORTED_CURRENCIES)
