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
Currency response formatting for TravelStyle AI application.
"""

import logging

logger = logging.getLogger(__name__)


class CurrencyFormatter:
    """Service for formatting currency conversion responses."""

    def __init__(self):
        """Initialize the currency formatter service."""
        pass

    def format_currency_response(
        self,
        from_currency: str,
        to_currency: str,
        amount: float,
        rate: float,
        converted_amount: float,
    ) -> str:
        """Format a currency conversion response."""
        try:
            # Format the response with proper currency formatting
            response = (
                f"💱 **Currency Conversion**\n\n"
                f"**{amount:,.2f} {from_currency}** = **{converted_amount:,.2f} {to_currency}**\n\n"
                f"📊 **Exchange Rate:** 1 {from_currency} = {rate:.4f} {to_currency}\n\n"
                f"💡 *Rates are updated in real-time and may vary slightly.*"
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
        try:
            response = (
                f"📊 **Exchange Rate**\n\n**1 {from_currency}** = **{rate:.4f} {to_currency}**\n\n"
            )

            if last_updated:
                response += f"🕒 *Last updated: {last_updated}*\n\n"

            response += "💡 *Rates are updated in real-time and may vary slightly.*"

            return response

        except Exception as e:
            logger.error(f"Error formatting exchange rate response: {e}")
            return "Sorry, I encountered an error formatting the exchange rate."

    def format_currency_help_response(self) -> str:
        """Format a currency help response."""
        help_text = (
            "💱 **Currency Converter Help**\n\n"
            "I can help you with currency conversions and exchange rates!\n\n"
            "**Examples:**\n"
            "• Convert 100 USD to EUR\n"
            "• 50 EUR to USD\n"
            "• Exchange rate USD EUR\n"
            "• 1000 JPY to GBP\n\n"
            "**Supported Currencies:**\n"
            "I support all major world currencies including USD, EUR, GBP, JPY, CAD, AUD, and many more.\n\n"
            "**Tips:**\n"
            "• Use 3-letter currency codes (USD, EUR, etc.)\n"
            "• Include the amount you want to convert\n"
            "• Ask for exchange rates without amounts\n\n"
            "💡 *Rates are updated in real-time from reliable sources.*"
        )

        return help_text

    def format_error_response(self, error_message: str = "Unknown error") -> str:
        """Format an error response."""
        return f"❌ **Currency Conversion Error**\n\nSorry, I couldn't process your currency request: {error_message}\n\nPlease try again with a different format or check the supported currencies."
