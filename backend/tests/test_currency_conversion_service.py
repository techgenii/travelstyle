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

"""Tests for currency conversion service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.currency_conversion_service import currency_conversion_service


class TestIsCurrencyRequest:
    """Test the is_currency_request method."""

    def test_is_currency_request_true_keywords(self):
        """Test identifying currency requests with keywords."""
        assert currency_conversion_service.is_currency_request("What's the exchange rate?") is True
        assert currency_conversion_service.is_currency_request("Convert USD to EUR") is True
        assert (
            currency_conversion_service.is_currency_request("currency between US and Germany")
            is True
        )
        assert currency_conversion_service.is_currency_request("convert money") is True
        assert currency_conversion_service.is_currency_request("currency exchange") is True
        assert currency_conversion_service.is_currency_request("exchange money") is True
        assert currency_conversion_service.is_currency_request("currency conversion") is True

    def test_is_currency_request_true_currency_codes(self):
        """Test identifying currency requests with currency codes."""
        assert currency_conversion_service.is_currency_request("Convert USD to EUR") is True
        assert currency_conversion_service.is_currency_request("JPY to GBP rate") is True
        assert currency_conversion_service.is_currency_request("What's the USD rate?") is True

    def test_is_currency_request_true_country_names(self):
        """Test identifying currency requests with country names."""
        assert (
            currency_conversion_service.is_currency_request("convert from United States to Japan")
            is True
        )
        assert currency_conversion_service.is_currency_request("USA to UK exchange") is True
        assert currency_conversion_service.is_currency_request("America to Britain") is True
        assert currency_conversion_service.is_currency_request("India to China") is True

    def test_is_currency_request_true_currency_words(self):
        """Test identifying currency requests with currency words."""
        assert currency_conversion_service.is_currency_request("convert dollars to euros") is True
        assert currency_conversion_service.is_currency_request("yen to pounds") is True
        assert currency_conversion_service.is_currency_request("rupees to yuan") is True
        assert currency_conversion_service.is_currency_request("bucks to quid") is True

    def test_is_currency_request_false(self):
        """Test identifying non-currency requests."""
        assert currency_conversion_service.is_currency_request("Hello, how are you?") is False
        assert currency_conversion_service.is_currency_request("Tell me about the weather") is False
        assert currency_conversion_service.is_currency_request("What's the temperature?") is False
        assert currency_conversion_service.is_currency_request("") is False
        assert currency_conversion_service.is_currency_request("   ") is False

    def test_is_currency_request_case_insensitive(self):
        """Test that currency request detection is case insensitive."""
        assert currency_conversion_service.is_currency_request("EXCHANGE RATE") is True
        assert currency_conversion_service.is_currency_request("convert CURRENCY") is True
        assert currency_conversion_service.is_currency_request("usd to eur") is True


class TestValidateCurrencyCode:
    """Test the validate_currency_code method."""

    def test_validate_currency_code_valid(self):
        """Test currency code validation with valid codes."""
        assert currency_conversion_service.validate_currency_code("USD") is True
        assert currency_conversion_service.validate_currency_code("EUR") is True
        assert currency_conversion_service.validate_currency_code("JPY") is True
        assert currency_conversion_service.validate_currency_code("GBP") is True
        assert currency_conversion_service.validate_currency_code("CAD") is True

    def test_validate_currency_code_invalid(self):
        """Test currency code validation with invalid codes."""
        assert currency_conversion_service.validate_currency_code("INVALID") is False
        assert currency_conversion_service.validate_currency_code("XXX") is False
        assert currency_conversion_service.validate_currency_code("YYY") is False
        assert currency_conversion_service.validate_currency_code("") is False
        assert currency_conversion_service.validate_currency_code("   ") is False

    def test_validate_currency_code_case_insensitive(self):
        """Test that currency code validation is case insensitive."""
        assert currency_conversion_service.validate_currency_code("usd") is True
        assert currency_conversion_service.validate_currency_code("Usd") is True
        assert currency_conversion_service.validate_currency_code("USD") is True
        assert currency_conversion_service.validate_currency_code("eur") is True
        assert currency_conversion_service.validate_currency_code("Eur") is True


class TestFormatCurrencyResponse:
    """Test the format_currency_response method."""

    def test_format_currency_response_basic(self):
        """Test formatting currency conversion response."""
        response = currency_conversion_service.format_currency_response(
            "USD", "EUR", 100.0, 0.85, 85.0
        )
        expected = "100.00 USD = 85.00 EUR (Rate: 0.8500)"
        assert response == expected

    def test_format_currency_response_zero_amount(self):
        """Test formatting currency response with zero amount."""
        response = currency_conversion_service.format_currency_response(
            "USD", "EUR", 0.0, 0.85, 0.0
        )
        expected = "0.00 USD = 0.00 EUR (Rate: 0.8500)"
        assert response == expected

    def test_format_currency_response_large_amount(self):
        """Test formatting currency response with large amount."""
        response = currency_conversion_service.format_currency_response(
            "USD", "JPY", 1000.0, 150.25, 150250.0
        )
        expected = "1000.00 USD = 150250.00 JPY (Rate: 150.2500)"
        assert response == expected

    def test_format_currency_response_decimal_amount(self):
        """Test formatting currency response with decimal amount."""
        response = currency_conversion_service.format_currency_response(
            "EUR", "USD", 50.75, 1.15, 58.36
        )
        expected = "50.75 EUR = 58.36 USD (Rate: 1.1500)"
        assert response == expected


class TestGetSupportedCurrencies:
    """Test the get_supported_currencies method."""

    def test_get_supported_currencies(self):
        """Test getting supported currencies."""
        currencies = currency_conversion_service.get_supported_currencies()

        assert "USD" in currencies
        assert "EUR" in currencies
        assert "GBP" in currencies
        assert "JPY" in currencies
        assert "CAD" in currencies
        assert "AUD" in currencies
        assert "CHF" in currencies
        assert "CNY" in currencies
        assert "INR" in currencies
        assert "MXN" in currencies
        # The service supports 163 currencies
        assert len(currencies) == 163

    def test_get_supported_currencies_type(self):
        """Test that get_supported_currencies returns a list."""
        currencies = currency_conversion_service.get_supported_currencies()
        assert isinstance(currencies, list)
        assert all(isinstance(currency, str) for currency in currencies)


class TestParseCurrencyRequest:
    """Test the parse_currency_request method."""

    @pytest.mark.asyncio
    async def test_parse_currency_request_valid_json(self):
        """Test parsing currency request with valid JSON response."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with valid JSON
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": 100.50}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $100.50 USD to EUR"
            )

            assert result["first_country"] == "USD"
            assert result["second_country"] == "EUR"
            assert result["amount"] == 100.50

    @pytest.mark.asyncio
    async def test_parse_currency_request_invalid_json(self):
        """Test parsing currency request with invalid JSON response."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with invalid JSON
            mock_choice = MagicMock()
            mock_choice.message.content = "Invalid JSON response"

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $50 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_json_decode_error(self):
        """Test parsing currency request with JSON decode error."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with malformed JSON
            mock_choice = MagicMock()
            mock_choice.message.content = '{"first_country": "USD", "second_country": "EUR", "amount": 100.50'  # Missing closing brace

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $100.50 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_openai_exception(self):
        """Test parsing currency request when OpenAI raises an exception."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Make OpenAI raise an exception
            mock_create.side_effect = Exception("OpenAI API error")

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_whitespace(self):
        """Test parsing currency request with whitespace in currency codes."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with whitespace in currency codes
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": " USD ", "second_country": " EUR ", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result["first_country"] == "USD"  # Should be stripped and uppercased
            assert result["second_country"] == "EUR"  # Should be stripped and uppercased
            assert result["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_missing_amount(self):
        """Test parsing currency request with missing amount field."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with missing amount
            mock_choice = MagicMock()
            mock_choice.message.content = '{"first_country": "USD", "second_country": "EUR"}'

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request("convert USD to EUR")

            assert result["first_country"] == "USD"
            assert result["second_country"] == "EUR"
            assert result["amount"] == 0.0  # Should default to 0.0 for missing field

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_formatted_json(self):
        """Test parsing currency request with formatted JSON (with newlines and spaces)."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with formatted JSON
            mock_choice = MagicMock()
            mock_choice.message.content = """{
  "first_country": "USD",
  "second_country": "EUR",
  "amount": 100.0
}"""

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result["first_country"] == "USD"
            assert result["second_country"] == "EUR"
            assert result["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_extra_text(self):
        """Test parsing currency request with extra text around JSON."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with extra text around JSON
            mock_choice = MagicMock()
            mock_choice.message.content = 'Here is the parsed data: {"first_country": "USD", "second_country": "EUR", "amount": 100.0} Thank you!'

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result["first_country"] == "USD"
            assert result["second_country"] == "EUR"
            assert result["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_amount_zero(self):
        """Test parsing currency request with amount zero."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with amount zero
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": 0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request("convert USD to EUR")

            assert result["first_country"] == "USD"
            assert result["second_country"] == "EUR"
            assert result["amount"] == 0.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_negative_amount(self):
        """Test parsing currency request with negative amount."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with negative amount
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": -50.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert -$50 USD to EUR"
            )

            assert result["first_country"] == "USD"
            assert result["second_country"] == "EUR"
            assert result["amount"] == -50.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_missing_currencies(self):
        """Test parsing currency request with missing currency information."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with missing currencies
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "", "second_country": "", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request("convert something")

            assert result["first_country"] == ""  # Should be empty string
            assert result["second_country"] == ""  # Should be empty string
            assert result["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_non_numeric_amount(self):
        """Test parsing currency request with non-numeric amount."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with non-numeric amount
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": "invalid"}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request("convert USD to EUR")

            # Should handle the error gracefully and return None or default value
            assert result is None or result["amount"] == 0.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_regex_fallback(self):
        """Test parsing currency request using regex fallback when JSON parsing fails."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with JSON embedded in text
            mock_choice = MagicMock()
            mock_choice.message.content = 'I found this data: {"first_country": "USD", "second_country": "EUR", "amount": 100.0} in the request.'

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result["first_country"] == "USD"
            assert result["second_country"] == "EUR"
            assert result["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_regex_fallback_failure(self):
        """Test parsing currency request when both JSON parsing and regex fallback fail."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with invalid JSON that regex can't fix
            mock_choice = MagicMock()
            mock_choice.message.content = "Invalid response without proper JSON structure"

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_regex_fallback_json_decode_error(self):
        """Test parsing currency request when regex fallback also fails JSON decode."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with malformed JSON that regex extracts but can't parse
            mock_choice = MagicMock()
            mock_choice.message.content = 'Here is the data: {"first_country": "USD", "second_country": "EUR", "amount": 100.0'  # Missing closing brace

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_non_numeric_amount_exception(self):
        """Test parsing currency request with non-numeric amount that causes exception."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with non-numeric amount
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": "invalid"}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request("convert USD to EUR")

            # Should handle the error gracefully and return None
            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_debug_logging(self):
        """Test parsing currency request to trigger debug logging."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_create:
            # Create a proper mock response with valid JSON that should trigger debug logging
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result["first_country"] == "USD"
            assert result["second_country"] == "EUR"
            assert result["amount"] == 100.0


class TestHandleCurrencyRequest:
    """Test the handle_currency_request method."""

    @pytest.mark.asyncio
    async def test_handle_currency_request_with_amount(self):
        """Test currency request with valid amount and exchange rate."""
        with (
            patch(
                "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
                new_callable=AsyncMock,
            ) as mock_openai,
            patch(
                "app.services.currency_conversion_service.currency_service.convert_currency",
                new_callable=AsyncMock,
            ) as mock_convert,
        ):
            # Create a proper mock response with valid currencies and amount
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            # Mock currency conversion service response
            mock_convert.return_value = {
                "original": {"amount": 100.0, "currency": "USD"},
                "converted": {"amount": 85.0, "currency": "EUR"},
                "rate": 0.85,
                "last_updated_utc": "2024-01-01T12:00:00Z",
                "last_updated_unix": 1704110400,
            }

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 USD to EUR"
            )

            assert result["original"]["amount"] == 100.0
            assert result["original"]["currency"] == "USD"
            assert result["converted"]["amount"] == 85.0
            assert result["converted"]["currency"] == "EUR"
            assert result["rate"] == 0.85
            assert result["last_updated_utc"] == "2024-01-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_handle_currency_request_without_amount(self):
        """Test currency request without amount (just exchange rate)."""
        with (
            patch(
                "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
                new_callable=AsyncMock,
            ) as mock_openai,
            patch(
                "app.services.currency_conversion_service.currency_service.convert_currency",
                new_callable=AsyncMock,
            ) as mock_convert,
        ):
            # Create a proper mock response with valid currencies but no amount
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": 0.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            # Mock currency conversion service response
            mock_convert.return_value = {
                "original": {"amount": 0.0, "currency": "USD"},
                "converted": {"amount": 0.0, "currency": "EUR"},
                "rate": 0.85,
                "last_updated_utc": "2024-01-01T12:00:00Z",
                "last_updated_unix": 1704110400,
            }

            result = await currency_conversion_service.handle_currency_request(
                "What's the USD to EUR rate?"
            )

            assert result["original"]["amount"] == 0.0
            assert result["original"]["currency"] == "USD"
            assert result["converted"]["amount"] == 0.0
            assert result["converted"]["currency"] == "EUR"
            assert result["rate"] == 0.85
            assert result["last_updated_utc"] == "2024-01-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_handle_currency_request_missing_currencies(self):
        """Test currency request with missing currency information."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_openai:
            # Create a proper mock response with missing currencies
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "", "second_country": "", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            result = await currency_conversion_service.handle_currency_request("convert something")

            assert result is None

    @pytest.mark.asyncio
    async def test_handle_currency_request_unsupported_from_currency(self):
        """Test currency request with unsupported from currency."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_openai:
            # Create a proper mock response with unsupported currency
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "XXX", "second_country": "EUR", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 XXX to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_handle_currency_request_unsupported_to_currency(self):
        """Test currency request with unsupported to currency."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_openai:
            # Create a proper mock response with unsupported currency
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "YYY", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 USD to YYY"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_handle_currency_request_no_exchange_rate(self):
        """Test currency request when exchange rate service returns None."""
        with (
            patch(
                "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
                new_callable=AsyncMock,
            ) as mock_openai,
            patch(
                "app.services.currency_conversion_service.currency_service.convert_currency",
                new_callable=AsyncMock,
            ) as mock_convert,
        ):
            # Create a proper mock response with valid currencies
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            # Make currency conversion service return None
            mock_convert.return_value = None

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_handle_currency_request_no_rate_in_response(self):
        """Test currency request when currency conversion service returns None."""
        with (
            patch(
                "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
                new_callable=AsyncMock,
            ) as mock_openai,
            patch(
                "app.services.currency_conversion_service.currency_service.convert_currency",
                new_callable=AsyncMock,
            ) as mock_convert,
        ):
            # Create a proper mock response with valid currencies
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            # Mock currency conversion service returning None (API error or invalid response)
            mock_convert.return_value = None

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_handle_currency_request_parse_failure(self):
        """Test currency request when parsing fails."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_openai:
            # Make OpenAI raise an exception
            mock_openai.side_effect = Exception("Service error")

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_handle_currency_request_exception(self):
        """Test currency request when an exception occurs."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_openai:
            # Make OpenAI raise an exception
            mock_openai.side_effect = Exception("Service error")

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_handle_currency_request_with_decimal_amount(self):
        """Test currency request with decimal amount."""
        with (
            patch(
                "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
                new_callable=AsyncMock,
            ) as mock_openai,
            patch(
                "app.services.currency_conversion_service.currency_service.convert_currency",
                new_callable=AsyncMock,
            ) as mock_convert,
        ):
            # Create a proper mock response with decimal amount
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": 50.75}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            # Mock currency conversion service response
            mock_convert.return_value = {
                "original": {"amount": 50.75, "currency": "USD"},
                "converted": {"amount": 43.14, "currency": "EUR"},
                "rate": 0.85,
                "last_updated_utc": "2024-01-01T12:00:00Z",
                "last_updated_unix": 1704110400,
            }

            result = await currency_conversion_service.handle_currency_request(
                "convert 50.75 USD to EUR"
            )

            assert result["original"]["amount"] == 50.75
            assert result["original"]["currency"] == "USD"
            assert result["converted"]["amount"] == 43.14  # 50.75 * 0.85
            assert result["converted"]["currency"] == "EUR"
            assert result["rate"] == 0.85

    @pytest.mark.asyncio
    async def test_handle_currency_request_with_negative_amount(self):
        """Test currency request with negative amount."""
        with (
            patch(
                "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
                new_callable=AsyncMock,
            ) as mock_openai,
            patch(
                "app.services.currency_conversion_service.currency_service.convert_currency",
                new_callable=AsyncMock,
            ) as mock_convert,
        ):
            # Create a proper mock response with negative amount
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": -25.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            # Mock currency conversion service response
            mock_convert.return_value = {
                "original": {"amount": -25.0, "currency": "USD"},
                "converted": {"amount": -21.25, "currency": "EUR"},
                "rate": 0.85,
                "last_updated_utc": "2024-01-01T12:00:00Z",
                "last_updated_unix": 1704110400,
            }

            result = await currency_conversion_service.handle_currency_request(
                "convert -25 USD to EUR"
            )

            assert result["original"]["amount"] == -25.0
            assert result["original"]["currency"] == "USD"
            assert result["converted"]["amount"] == -21.25  # -25.0 * 0.85
            assert result["converted"]["currency"] == "EUR"
            assert result["rate"] == 0.85

    @pytest.mark.asyncio
    async def test_handle_currency_request_generic_exception(self):
        """Test currency request when a generic exception occurs during processing."""
        with patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_openai:
            # Make OpenAI raise an exception during processing
            mock_openai.side_effect = Exception("Unexpected error during processing")

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_handle_currency_request_duplicate_validation(self):
        """Test currency request to cover the duplicate validation check."""
        with (
            patch(
                "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
                new_callable=AsyncMock,
            ) as mock_openai,
            patch(
                "app.services.currency_conversion_service.currency_service.convert_currency",
                new_callable=AsyncMock,
            ) as mock_convert,
        ):
            # Create a proper mock response with valid currencies
            mock_choice = MagicMock()
            mock_choice.message.content = (
                '{"first_country": "USD", "second_country": "EUR", "amount": 100.0}'
            )

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value = mock_response

            # Mock currency conversion service response
            mock_convert.return_value = {
                "original": {"amount": 100.0, "currency": "USD"},
                "converted": {"amount": 85.0, "currency": "EUR"},
                "rate": 0.85,
                "last_updated_utc": "2024-01-01T12:00:00Z",
                "last_updated_unix": 1704110400,
            }

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 USD to EUR"
            )

            # This should pass both validation checks and return a valid result
            assert result["original"]["amount"] == 100.0
            assert result["original"]["currency"] == "USD"
            assert result["converted"]["amount"] == 85.0
            assert result["converted"]["currency"] == "EUR"
            assert result["rate"] == 0.85


class TestHelperMethods:
    """Test helper methods in the currency conversion service."""

    def test_clean_parsed_data(self):
        """Test the _clean_parsed_data helper method."""
        service = currency_conversion_service

        # Test with normal data
        data = {"first_country": " usd ", "second_country": " eur ", "amount": 100.0}
        result = service._clean_parsed_data(data)
        assert result["first_country"] == "USD"
        assert result["second_country"] == "EUR"
        assert result["amount"] == 100.0

        # Test with missing fields
        data = {"first_country": "USD"}
        result = service._clean_parsed_data(data)
        assert result["first_country"] == "USD"
        assert result["second_country"] == ""
        assert result["amount"] == 0.0

        # Test with empty data
        data = {}
        result = service._clean_parsed_data(data)
        assert result["first_country"] == ""
        assert result["second_country"] == ""
        assert result["amount"] == 0.0

    def test_extract_json_from_text(self):
        """Test the _extract_json_from_text helper method."""
        service = currency_conversion_service

        # Test with JSON in text
        text = 'Here is the data: {"first_country": "USD", "second_country": "EUR", "amount": 100.0} Thank you!'
        result = service._extract_json_from_text(text)
        assert result == '{"first_country": "USD", "second_country": "EUR", "amount": 100.0}'

        # Test with no JSON
        text = "No JSON here"
        result = service._extract_json_from_text(text)
        assert result == ""

        # Test with empty string
        text = ""
        result = service._extract_json_from_text(text)
        assert result == ""

        # Test with multiple JSON objects (regex is greedy, matches from first { to last })
        text = 'First: {"a": 1} Second: {"b": 2}'
        result = service._extract_json_from_text(text)
        assert result == '{"a": 1} Second: {"b": 2}'
