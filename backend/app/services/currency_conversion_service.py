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

"""Dedicated service for handling currency conversion requests using OpenAI parsing."""

import json
import logging
import re

from app.services.currency_service import currency_service
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = {
    "AED",
    "AFN",
    "ALL",
    "AMD",
    "ANG",
    "AOA",
    "ARS",
    "AUD",
    "AWG",
    "AZN",
    "BAM",
    "BBD",
    "BDT",
    "BGN",
    "BHD",
    "BIF",
    "BMD",
    "BND",
    "BOB",
    "BRL",
    "BSD",
    "BTN",
    "BWP",
    "BYN",
    "BZD",
    "CAD",
    "CDF",
    "CHF",
    "CLP",
    "CNY",
    "COP",
    "CRC",
    "CUP",
    "CVE",
    "CZK",
    "DJF",
    "DKK",
    "DOP",
    "DZD",
    "EGP",
    "ERN",
    "ETB",
    "EUR",
    "FJD",
    "FKP",
    "FOK",
    "GBP",
    "GEL",
    "GGP",
    "GHS",
    "GIP",
    "GMD",
    "GNF",
    "GTQ",
    "GYD",
    "HKD",
    "HNL",
    "HRK",
    "HTG",
    "HUF",
    "IDR",
    "ILS",
    "IMP",
    "INR",
    "IQD",
    "IRR",
    "ISK",
    "JEP",
    "JMD",
    "JOD",
    "JPY",
    "KES",
    "KGS",
    "KHR",
    "KID",
    "KMF",
    "KRW",
    "KWD",
    "KYD",
    "KZT",
    "LAK",
    "LBP",
    "LKR",
    "LRD",
    "LSL",
    "LYD",
    "MAD",
    "MDL",
    "MGA",
    "MKD",
    "MMK",
    "MNT",
    "MOP",
    "MRU",
    "MUR",
    "MVR",
    "MWK",
    "MXN",
    "MYR",
    "MZN",
    "NAD",
    "NGN",
    "NIO",
    "NOK",
    "NPR",
    "NZD",
    "OMR",
    "PAB",
    "PEN",
    "PGK",
    "PHP",
    "PKR",
    "PLN",
    "PYG",
    "QAR",
    "RON",
    "RSD",
    "RUB",
    "RWF",
    "SAR",
    "SBD",
    "SCR",
    "SDG",
    "SEK",
    "SGD",
    "SHP",
    "SLE",
    "SLL",
    "SOS",
    "SRD",
    "SSP",
    "STN",
    "SYP",
    "SZL",
    "THB",
    "TJS",
    "TMT",
    "TND",
    "TOP",
    "TRY",
    "TTD",
    "TVD",
    "TWD",
    "TZS",
    "UAH",
    "UGX",
    "USD",
    "UYU",
    "UZS",
    "VES",
    "VND",
    "VUV",
    "WST",
    "XAF",
    "XCD",
    "XCG",
    "XDR",
    "XOF",
    "XPF",
    "YER",
    "ZAR",
    "ZMW",
    "ZWL",
}

COUNTRY_NAME_MAP = {
    "united states": "USD",
    "usa": "USD",
    "us": "USD",
    "america": "USD",
    "the states": "USD",
    "japan": "JPY",
    "nippon": "JPY",
    "united kingdom": "GBP",
    "uk": "GBP",
    "britain": "GBP",
    "great britain": "GBP",
    "england": "GBP",
    "germany": "EUR",
    "france": "EUR",
    "europe": "EUR",
    "eu": "EUR",
    "india": "INR",
    "bharat": "INR",
    "china": "CNY",
    "prc": "CNY",
    "mainland china": "CNY",
    "mexico": "MXN",
    "canada": "CAD",
    "australia": "AUD",
    "down under": "AUD",
    "oz": "AUD",
    "switzerland": "CHF",
    "swiss": "CHF",
    "brazil": "BRL",
    "brasil": "BRL",
    "south korea": "KRW",
    "republic of korea": "KRW",
    "korea": "KRW",
    "north korea": "KPW",
    "dprk": "KPW",
    "russia": "RUB",
    "russian federation": "RUB",
    "saudi arabia": "SAR",
    "ksa": "SAR",
    "united arab emirates": "AED",
    "uae": "AED",
    "south africa": "ZAR",
    "rsa": "ZAR",
    "new zealand": "NZD",
    "nz": "NZD",
    "singapore": "SGD",
    "hong kong": "HKD",
    "taiwan": "TWD",
    "republic of china": "TWD",
}


class CurrencyConversionService:
    """Service for handling currency conversion requests and responses using OpenAI parsing."""

    def __init__(self):
        pass

    def is_currency_request(self, user_input: str) -> bool:
        input_lower = user_input.lower()

        currency_keywords = [
            "exchange rate",
            "convert currency",
            "currency exchange",
            "exchange money",
            "convert money",
            "currency conversion",
            "currency",
            "convert",
            "money exchange",
        ]
        currency_codes = [code.lower() for code in SUPPORTED_CURRENCIES]
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
        ]
        currency_words = [
            "dollar",
            "euro",
            "yen",
            "pound",
            "rupees",
            "yuan",
            "bucks",
            "quid",
            "money",
            "currency",
        ]

        return (
            any(keyword in input_lower for keyword in currency_keywords)
            or any(code in input_lower for code in currency_codes)
            or any(word in input_lower for word in currency_words)
            or any(name in input_lower for name in country_names)
        )

    async def parse_currency_request(self, user_message: str) -> dict[str, any] | None:
        try:
            prompt = f"""
You are a currency exchange parser. When given a user message, extract the following:

1. The first currency code as a 3-letter ISO currency code (e.g., USD, JPY, EUR).
2. The second currency code as a 3-letter ISO currency code.
3. The amount to be exchanged, formatted as a float with two decimal places.

Supported input variations:
- Currency synonyms: "bucks", "quid", "yen", "rupees", etc.
- Country names or codes: "United States", "USD", "Japan", "JPY"
- Spelled-out numbers: "fifty", "one hundred", "twenty-five hundred"
- Currency symbols: "$", "€", "¥"
- Informal messages like:
  - "how much is 50 bucks in yen?"
  - "convert fifty dollars to euros"
  - "I want to change 1,000.75 dollars to pounds"

Currency Mapping Examples:
United States, USA, America, the States, bucks → USD
Japan, Nippon, yen → JPY
United Kingdom, Britain, UK, quid → GBP
Germany, France, Europe, euros → EUR
India, rupees → INR
China, yuan, renminbi → CNY
Mexico → MXN
Canada → CAD

Rules:
- Convert written numbers to float if possible.
- Return empty string if currency is missing, and 0.0 if amount not found.
- Output must be a **valid JSON object** with:
  {{
    "first_country": "<3-letter currency code>",
    "second_country": "<3-letter currency code>",
    "amount": <float with 2 decimal places>
  }}

Do not include any explanation. Return JSON only.

User message: {user_message}
"""

            response = await openai_service.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a currency exchange parser. Extract currency codes and amounts from user messages and return only valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=150,
            )

            content = response.choices[0].message.content.strip()
            logger.debug(f"Raw OpenAI response: {repr(content)}")

            try:
                parsed_data = json.loads(content)
                return self._clean_parsed_data(parsed_data)
            except json.JSONDecodeError:
                logger.warning("JSON parse failed, trying regex fallback")
                json_str = self._extract_json_from_text(content)
                if json_str:
                    try:
                        parsed_data = json.loads(json_str)
                        return self._clean_parsed_data(parsed_data)
                    except json.JSONDecodeError:
                        pass

            return None

        except Exception as e:
            logger.error("Failed to parse JSON: %s", e)
            return None

    def _extract_json_from_text(self, text: str) -> str:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group() if match else ""

    def _clean_parsed_data(self, data: dict) -> dict:
        return {
            "first_country": data.get("first_country", "").strip().upper(),
            "second_country": data.get("second_country", "").strip().upper(),
            "amount": round(float(data.get("amount", 0.0)), 2),
        }

    def validate_currency_code(self, currency_code: str) -> bool:
        return currency_code.upper() in SUPPORTED_CURRENCIES

    async def handle_currency_request(self, user_message: str) -> dict[str, any]:
        try:
            parsed = await self.parse_currency_request(user_message)
            if not parsed:
                return None

            from_currency = parsed.get("first_country", "")
            to_currency = parsed.get("second_country", "")
            amount = parsed.get("amount", 0.0)

            if not self.validate_currency_code(from_currency) or not self.validate_currency_code(
                to_currency
            ):
                logger.error(f"Invalid currency code: {from_currency} or {to_currency}")
                return None

            if not self.validate_currency_code(from_currency) or not self.validate_currency_code(
                to_currency
            ):
                logger.error(f"Invalid currency code: {from_currency} or {to_currency}")
                return None

            pair_data = await currency_service.get_pair_exchange_rate(from_currency, to_currency)
            if not pair_data:
                return None

            conversion_rate = pair_data["rate"]
            converted_amount = round(amount * conversion_rate, 2)

            return {
                "original": {"amount": round(amount, 2), "currency": from_currency},
                "converted": {"amount": converted_amount, "currency": to_currency},
                "rate": conversion_rate,
                "last_updated_unix": pair_data["last_updated_unix"],
                "last_updated_utc": pair_data["last_updated_utc"],
            }

        except Exception as e:
            logger.error(f"Error handling currency request: {e}")
            return None

    def get_supported_currencies(self) -> list[str]:
        return list(SUPPORTED_CURRENCIES)

    def format_currency_response(
        self,
        from_currency: str,
        to_currency: str,
        amount: float,
        rate: float,
        converted_amount: float,
    ) -> str:
        """Format currency conversion response."""
        return f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency} (Rate: {rate:.4f})"


# Singleton instance
currency_conversion_service = CurrencyConversionService()
