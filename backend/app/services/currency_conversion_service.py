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
Dedicated service for handling currency conversion requests using OpenAI parsing.

This module is maintained for backward compatibility.
For new code, use the modular structure in app.services.currency.*
"""

# Import everything from the new modular structure
from app.services.currency import (
    CURRENCY_PATTERNS,
    DEFAULT_BASE_CURRENCY,
    SUPPORTED_CURRENCIES,
    CurrencyAPIError,
    CurrencyConversionError,
    CurrencyService,
    CurrencyValidationError,
    normalize_currency_code,
    validate_amount,
    validate_currency_code,
    validate_currency_request,
)

# Re-export for backward compatibility
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

# Create a singleton instance for backward compatibility
currency_conversion_service = CurrencyService()

# Alias for backward compatibility
CurrencyConversionService = CurrencyService

# Add openai_service attribute for backward compatibility
from app.services.currency_service import currency_service  # noqa: E402
from app.services.openai.openai_service import openai_service  # noqa: E402

currency_conversion_service.openai_service = openai_service
currency_conversion_service.currency_service = currency_service
