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
Currency package for TravelStyle AI application.
Provides modular currency operations for conversions, parsing, and formatting.
"""

from app.services.currency.constants import (
    CURRENCY_PATTERNS,
    DEFAULT_BASE_CURRENCY,
    SUPPORTED_CURRENCIES,
)
from app.services.currency.exceptions import (
    CurrencyAPIError,
    CurrencyConversionError,
    CurrencyValidationError,
)
from app.services.currency.helpers import CurrencyService
from app.services.currency.validators import (
    normalize_currency_code,
    validate_amount,
    validate_currency_code,
    validate_currency_request,
)

__all__ = [
    "CurrencyService",
    "SUPPORTED_CURRENCIES",
    "CURRENCY_PATTERNS",
    "DEFAULT_BASE_CURRENCY",
    "CurrencyAPIError",
    "CurrencyConversionError",
    "CurrencyValidationError",
    "validate_currency_code",
    "validate_amount",
    "validate_currency_request",
    "normalize_currency_code",
]
