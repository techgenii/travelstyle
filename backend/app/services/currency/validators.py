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
Currency validation functions for TravelStyle AI application.
"""

from typing import Any

from app.services.currency.constants import SUPPORTED_CURRENCIES
from app.services.currency.exceptions import CurrencyValidationError


def validate_currency_code(currency_code: str) -> bool:
    """Validate if a currency code is supported."""
    if not currency_code or not isinstance(currency_code, str):
        return False

    normalized_code = currency_code.strip().upper()
    return normalized_code in SUPPORTED_CURRENCIES


def validate_amount(amount: Any) -> bool:
    """Validate if an amount is a valid number."""
    if not isinstance(amount, int | float):
        return False

    try:
        float_amount = float(amount)
        return float_amount > 0
    except (ValueError, TypeError):
        return False


def validate_currency_request(from_currency: str, to_currency: str, amount: Any) -> bool:
    """Validate a complete currency conversion request."""
    if not validate_currency_code(from_currency):
        raise CurrencyValidationError(f"Invalid from_currency: {from_currency}")

    if not validate_currency_code(to_currency):
        raise CurrencyValidationError(f"Invalid to_currency: {to_currency}")

    if not validate_amount(amount):
        raise CurrencyValidationError(f"Invalid amount: {amount}")

    return True


def normalize_currency_code(currency_code: str) -> str:
    """Normalize a currency code to uppercase."""
    if not currency_code:
        raise CurrencyValidationError("Currency code cannot be empty")

    normalized = currency_code.strip().upper()
    if not validate_currency_code(normalized):
        raise CurrencyValidationError(f"Unsupported currency code: {currency_code}")

    return normalized
