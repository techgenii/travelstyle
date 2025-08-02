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
Currency request parsing for TravelStyle AI application.
"""

import json
import logging
import re
from typing import Any

from app.services.currency.constants import CURRENCY_PATTERNS, SUPPORTED_CURRENCIES
from app.services.currency.validators import validate_currency_code
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)


class CurrencyParser:
    """Service for parsing currency conversion requests from user messages."""

    def __init__(self):
        """Initialize the currency parser service."""
        pass

    def is_currency_request(self, user_input: str) -> bool:
        """Check if a user message is a currency conversion request."""
        if not user_input or not isinstance(user_input, str):
            return False

        input_lower = user_input.lower()

        # Check for currency-related keywords
        currency_keywords = [
            "convert",
            "exchange",
            "currency",
            "rate",
            "usd",
            "eur",
            "gbp",
            "jpy",
            "dollar",
            "euro",
            "pound",
            "yen",
            "peso",
            "franc",
            "yuan",
            "won",
            "rupee",
            "ruble",
            "dinar",
            "dirham",
            "riyal",
            "ringgit",
            "baht",
            "dong",
            "peso",
            "real",
            "rand",
            "krona",
            "krone",
            "zloty",
            "forint",
            "bucks",
            "quid",
            "money",
        ]

        # Check for currency codes (3-letter codes)
        currency_codes = re.findall(r"\b[A-Z]{3}\b", user_input.upper())

        # Check for country names
        country_names = [
            "united states",
            "usa",
            "america",
            "japan",
            "uk",
            "britain",
            "india",
            "china",
            "mexico",
            "canada",
            "australia",
            "switzerland",
            "brazil",
            "south korea",
            "russia",
            "saudi arabia",
            "united arab emirates",
            "south africa",
            "new zealand",
            "singapore",
            "hong kong",
            "taiwan",
        ]

        # Check for numbers followed by currency codes
        amount_patterns = [
            r"\d+(?:\.\d+)?\s*[A-Z]{3}",
            r"[A-Z]{3}\s*\d+(?:\.\d+)?",
        ]

        # Check for conversion patterns
        conversion_patterns = [
            r"to\s+[A-Z]{3}",
            r"convert\s+\d+",
            r"exchange\s+rate",
        ]

        # Check if any currency keywords are present
        has_keywords = any(keyword in input_lower for keyword in currency_keywords)

        # Check if currency codes are present
        has_codes = len(currency_codes) > 0

        # Check if country names are present
        has_country_names = any(name in input_lower for name in country_names)

        # Check if amount patterns are present
        has_amounts = any(re.search(pattern, user_input.upper()) for pattern in amount_patterns)

        # Check if conversion patterns are present
        has_conversion = any(
            re.search(pattern, user_input.lower()) for pattern in conversion_patterns
        )

        # Check for specific currency patterns
        for pattern in CURRENCY_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True

        # Return True if we have currency codes, country names, or keywords with conversion indicators
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
            """

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

    def _clean_parsed_data(self, data: dict) -> dict:
        """Clean and normalize parsed data."""
        cleaned = {}

        # Normalize currency codes
        if "from_currency" in data:
            cleaned["from_currency"] = data["from_currency"].strip().upper()

        if "to_currency" in data:
            cleaned["to_currency"] = data["to_currency"].strip().upper()

        # Normalize amount
        if "amount" in data:
            try:
                cleaned["amount"] = float(data["amount"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid amount: {data['amount']}")
                return None
        else:
            # Default to 0.0 if amount is missing
            cleaned["amount"] = 0.0

        # Copy request type
        if "request_type" in data:
            cleaned["request_type"] = data["request_type"].lower()

        return cleaned

    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currency codes."""
        return sorted(list(SUPPORTED_CURRENCIES))
