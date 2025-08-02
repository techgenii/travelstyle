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
Tests for currency conversion service.
"""

from unittest.mock import AsyncMock, patch

import pytest
from app.services.currency_conversion_service import currency_conversion_service


class TestIsCurrencyRequest:
    """Test currency request detection."""

    def test_is_currency_request_true_keywords(self):
        """Test currency request detection with keywords."""
        assert currency_conversion_service.is_currency_request("convert USD to EUR")
        assert currency_conversion_service.is_currency_request("exchange rate")
        assert currency_conversion_service.is_currency_request("currency conversion")

    def test_is_currency_request_true_currency_codes(self):
        """Test currency request detection with currency codes."""
        assert currency_conversion_service.is_currency_request("USD to EUR")
        assert currency_conversion_service.is_currency_request("100 GBP to JPY")

    def test_is_currency_request_true_country_names(self):
        """Test currency request detection with country names."""
        assert currency_conversion_service.is_currency_request("dollars to euros")
        assert currency_conversion_service.is_currency_request("pounds to yen")

    def test_is_currency_request_true_currency_words(self):
        """Test currency request detection with currency words."""
        assert currency_conversion_service.is_currency_request("convert dollars to euros")
        assert currency_conversion_service.is_currency_request("exchange pounds for yen")

    def test_is_currency_request_false(self):
        """Test currency request detection with non-currency text."""
        assert not currency_conversion_service.is_currency_request("Hello world")
        assert not currency_conversion_service.is_currency_request("Travel to Paris")
        assert not currency_conversion_service.is_currency_request("")

    def test_is_currency_request_case_insensitive(self):
        """Test currency request detection is case insensitive."""
        assert currency_conversion_service.is_currency_request("Convert USD to EUR")
        assert currency_conversion_service.is_currency_request("convert usd to eur")


class TestValidateCurrencyCode:
    """Test currency code validation."""

    def test_validate_currency_code_valid(self):
        """Test validation of valid currency codes."""
        assert currency_conversion_service.validate_currency_code("USD")
        assert currency_conversion_service.validate_currency_code("EUR")
        assert currency_conversion_service.validate_currency_code("GBP")

    def test_validate_currency_code_invalid(self):
        """Test validation of invalid currency codes."""
        assert not currency_conversion_service.validate_currency_code("INVALID")
        assert not currency_conversion_service.validate_currency_code("123")
        assert not currency_conversion_service.validate_currency_code("")

    def test_validate_currency_code_case_insensitive(self):
        """Test currency code validation is case insensitive."""
        assert currency_conversion_service.validate_currency_code("usd")
        assert currency_conversion_service.validate_currency_code("Usd")


class TestFormatCurrencyResponse:
    """Test currency response formatting."""

    def test_format_currency_response_basic(self):
        """Test basic currency response formatting."""
        response = currency_conversion_service.format_currency_response(
            {"amount": 100, "currency": "USD"}, {"amount": 85, "currency": "EUR"}, 0.85
        )
        assert "100.00 USD = 85.00 EUR" in response
        assert "Rate: 0.8500" in response

    def test_format_currency_response_zero_amount(self):
        """Test currency response formatting with zero amount."""
        response = currency_conversion_service.format_currency_response(
            {"amount": 0, "currency": "USD"}, {"amount": 0, "currency": "EUR"}, 0.85
        )
        assert "0.00 USD = 0.00 EUR" in response

    def test_format_currency_response_large_amount(self):
        """Test currency response formatting with large amount."""
        response = currency_conversion_service.format_currency_response(
            {"amount": 1000000, "currency": "USD"}, {"amount": 850000, "currency": "EUR"}, 0.85
        )
        assert "1000000.00 USD = 850000.00 EUR" in response

    def test_format_currency_response_decimal_amount(self):
        """Test currency response formatting with decimal amount."""
        response = currency_conversion_service.format_currency_response(
            {"amount": 100.50, "currency": "USD"}, {"amount": 85.43, "currency": "EUR"}, 0.85
        )
        assert "100.50 USD = 85.43 EUR" in response


class TestGetSupportedCurrencies:
    """Test supported currencies functionality."""

    def test_get_supported_currencies(self):
        """Test getting supported currencies."""
        currencies = currency_conversion_service.get_supported_currencies()
        assert isinstance(currencies, list)
        assert len(currencies) > 0
        assert "USD" in currencies
        assert "EUR" in currencies
        assert "GBP" in currencies

    def test_get_supported_currencies_type(self):
        """Test that supported currencies returns a list."""
        currencies = currency_conversion_service.get_supported_currencies()
        assert isinstance(currencies, list)


class TestParseCurrencyRequest:
    """Test currency request parsing."""

    @pytest.mark.asyncio
    async def test_parse_currency_request_valid_json(self):
        """Test parsing currency request with valid JSON response."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return valid JSON
            mock_get_completion.return_value = '{"from_currency": "USD", "to_currency": "EUR", "amount": 100.50, "request_type": "conversion"}'

            result = await currency_conversion_service.parse_currency_request(
                "convert $100.50 USD to EUR"
            )

            assert result["from_currency"] == "USD"
            assert result["to_currency"] == "EUR"
            assert result["amount"] == 100.50

    @pytest.mark.asyncio
    async def test_parse_currency_request_invalid_json(self):
        """Test parsing currency request with invalid JSON response."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return invalid JSON
            mock_get_completion.return_value = "Invalid JSON response"

            result = await currency_conversion_service.parse_currency_request(
                "convert $50 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_json_decode_error(self):
        """Test parsing currency request with JSON decode error."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return malformed JSON
            mock_get_completion.return_value = '{"from_currency": "USD", "to_currency": "EUR", "amount": 100.50'  # Missing closing brace

            result = await currency_conversion_service.parse_currency_request(
                "convert $100.50 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_openai_exception(self):
        """Test parsing currency request when OpenAI raises an exception."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Make OpenAI raise an exception
            mock_get_completion.side_effect = Exception("OpenAI API error")

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_whitespace(self):
        """Test parsing currency request with whitespace in currency codes."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return JSON with whitespace
            mock_get_completion.return_value = (
                '{"from_currency": " USD ", "to_currency": " EUR ", "amount": 100.0}'
            )

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result["from_currency"] == "USD"  # Should be stripped and uppercased
            assert result["to_currency"] == "EUR"  # Should be stripped and uppercased
            assert result["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_formatted_json(self):
        """Test parsing currency request with formatted JSON response."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return formatted JSON
            mock_get_completion.return_value = """
            {
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100.50,
                "request_type": "conversion"
            }
            """

            result = await currency_conversion_service.parse_currency_request(
                "convert $100.50 USD to EUR"
            )

            assert result["from_currency"] == "USD"
            assert result["to_currency"] == "EUR"
            assert result["amount"] == 100.50

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_extra_text(self):
        """Test parsing currency request with extra text in response."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return JSON with extra text
            mock_get_completion.return_value = 'Here is the result: {"from_currency": "USD", "to_currency": "EUR", "amount": 100.0}'

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result["from_currency"] == "USD"
            assert result["to_currency"] == "EUR"
            assert result["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_amount_zero(self):
        """Test parsing currency request with zero amount."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return JSON with zero amount
            mock_get_completion.return_value = '{"from_currency": "USD", "to_currency": "EUR", "amount": 0, "request_type": "conversion"}'

            result = await currency_conversion_service.parse_currency_request(
                "convert $0 USD to EUR"
            )

            assert result["from_currency"] == "USD"
            assert result["to_currency"] == "EUR"
            assert result["amount"] == 0

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_negative_amount(self):
        """Test parsing currency request with negative amount."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return JSON with negative amount
            mock_get_completion.return_value = '{"from_currency": "USD", "to_currency": "EUR", "amount": -100, "request_type": "conversion"}'

            result = await currency_conversion_service.parse_currency_request(
                "convert -$100 USD to EUR"
            )

            assert result["from_currency"] == "USD"
            assert result["to_currency"] == "EUR"
            assert result["amount"] == -100

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_missing_currencies(self):
        """Test parsing currency request with missing currency codes."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return JSON with missing currencies
            mock_get_completion.return_value = '{"amount": 100, "request_type": "conversion"}'

            result = await currency_conversion_service.parse_currency_request("convert $100")

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_non_numeric_amount(self):
        """Test parsing currency request with non-numeric amount."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return JSON with non-numeric amount
            mock_get_completion.return_value = '{"from_currency": "USD", "to_currency": "EUR", "amount": "invalid", "request_type": "conversion"}'

            result = await currency_conversion_service.parse_currency_request(
                "convert invalid USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_regex_fallback(self):
        """Test parsing currency request with regex fallback."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return None (fallback to regex)
            mock_get_completion.return_value = None

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            # Should return None since regex fallback is not implemented in this version
            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_regex_fallback_failure(self):
        """Test parsing currency request with regex fallback failure."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return None
            mock_get_completion.return_value = None

            result = await currency_conversion_service.parse_currency_request(
                "convert $100 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_regex_fallback_json_decode_error(self):
        """Test parsing currency request with regex fallback JSON decode error."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return malformed JSON
            mock_get_completion.return_value = '{"from_currency": "USD", "to_currency": "EUR", "amount": 100.50'  # Missing closing brace

            result = await currency_conversion_service.parse_currency_request(
                "convert $100.50 USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_non_numeric_amount_exception(self):
        """Test parsing currency request with non-numeric amount exception."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return JSON with non-numeric amount
            mock_get_completion.return_value = '{"from_currency": "USD", "to_currency": "EUR", "amount": "invalid", "request_type": "conversion"}'

            result = await currency_conversion_service.parse_currency_request(
                "convert invalid USD to EUR"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_with_debug_logging(self):
        """Test parsing currency request with debug logging."""
        with patch(
            "app.services.openai.openai_service.openai_service.get_completion",
            new_callable=AsyncMock,
        ) as mock_get_completion:
            # Mock the get_completion method to return valid JSON
            mock_get_completion.return_value = '{"from_currency": "USD", "to_currency": "EUR", "amount": 100.50, "request_type": "conversion"}'

            result = await currency_conversion_service.parse_currency_request(
                "convert $100.50 USD to EUR"
            )

            assert result is not None
            assert result["from_currency"] == "USD"


class TestHandleCurrencyRequest:
    """Test currency request handling."""

    @pytest.mark.asyncio
    async def test_handle_currency_request_with_amount(self):
        """Test handling currency request with amount."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100.0,
                "request_type": "conversion",
            }

            with patch.object(
                currency_conversion_service.currency_service, "convert_currency", new=AsyncMock()
            ) as mock_convert:
                mock_convert.return_value = {
                    "original": {"amount": 100.0, "currency": "USD"},
                    "converted": {"amount": 85.0, "currency": "EUR"},
                    "rate": 0.85,
                }

                result = await currency_conversion_service.handle_currency_request(
                    "convert $100 USD to EUR"
                )

                assert result["success"] is True
                assert result["request_type"] == "conversion"
                assert "data" in result

    @pytest.mark.asyncio
    async def test_handle_currency_request_without_amount(self):
        """Test handling currency request without amount."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "request_type": "rate",
            }

            with patch.object(
                currency_conversion_service, "get_pair_exchange_rate", new=AsyncMock()
            ) as mock_rate:
                mock_rate.return_value = {
                    "base_currency": "USD",
                    "target_currency": "EUR",
                    "rate": 0.85,
                }

                result = await currency_conversion_service.handle_currency_request(
                    "USD to EUR rate"
                )

                assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_currency_request_missing_currencies(self):
        """Test handling currency request with missing currencies."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = None

            result = await currency_conversion_service.handle_currency_request("convert currency")

            assert result["success"] is False
            assert "Could not parse currency request" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_unsupported_from_currency(self):
        """Test handling currency request with unsupported from currency."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "INVALID",
                "to_currency": "EUR",
                "amount": 100.0,
                "request_type": "conversion",
            }

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 INVALID to EUR"
            )

            assert result["success"] is False
            assert "Unsupported currency" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_unsupported_to_currency(self):
        """Test handling currency request with unsupported to currency."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "USD",
                "to_currency": "INVALID",
                "amount": 100.0,
                "request_type": "conversion",
            }

            result = await currency_conversion_service.handle_currency_request(
                "convert 100 USD to INVALID"
            )

            assert result["success"] is False
            assert "Unsupported currency" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_no_exchange_rate(self):
        """Test handling currency request when no exchange rate is available."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100.0,
                "request_type": "conversion",
            }

            with patch.object(
                currency_conversion_service, "convert_currency", new=AsyncMock()
            ) as mock_convert:
                mock_convert.return_value = None

                result = await currency_conversion_service.handle_currency_request(
                    "convert $100 USD to EUR"
                )

                assert result["success"] is False
                assert "Exchange rate not available" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_no_rate_in_response(self):
        """Test handling currency request when rate is missing from response."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100.0,
                "request_type": "conversion",
            }

            with patch.object(
                currency_conversion_service, "convert_currency", new=AsyncMock()
            ) as mock_convert:
                mock_convert.return_value = {
                    "original": {"amount": 100.0, "currency": "USD"},
                    "converted": {"amount": 85.0, "currency": "EUR"},
                    # Missing rate
                }

                result = await currency_conversion_service.handle_currency_request(
                    "convert $100 USD to EUR"
                )

                assert result["success"] is False
                assert "Invalid response format" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_parse_failure(self):
        """Test handling currency request when parsing fails."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = None

            result = await currency_conversion_service.handle_currency_request(
                "invalid currency request"
            )

            assert result["success"] is False
            assert "Could not parse currency request" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_exception(self):
        """Test handling currency request when an exception occurs."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.side_effect = Exception("Parse error")

            result = await currency_conversion_service.handle_currency_request(
                "convert $100 USD to EUR"
            )

            assert result["success"] is False
            assert "Error processing currency request" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_with_decimal_amount(self):
        """Test handling currency request with decimal amount."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100.50,
                "request_type": "conversion",
            }

            with patch.object(
                currency_conversion_service.currency_service, "convert_currency", new=AsyncMock()
            ) as mock_convert:
                mock_convert.return_value = {
                    "original": {"amount": 100.50, "currency": "USD"},
                    "converted": {"amount": 85.43, "currency": "EUR"},
                    "rate": 0.85,
                }

                result = await currency_conversion_service.handle_currency_request(
                    "convert $100.50 USD to EUR"
                )

                assert result["success"] is True
                assert result["data"]["original"]["amount"] == 100.50

    @pytest.mark.asyncio
    async def test_handle_currency_request_with_negative_amount(self):
        """Test handling currency request with negative amount."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": -100.0,
                "request_type": "conversion",
            }

            with patch.object(
                currency_conversion_service, "convert_currency", new=AsyncMock()
            ) as mock_convert:
                mock_convert.return_value = {
                    "original": {"amount": -100.0, "currency": "USD"},
                    "converted": {"amount": -85.0, "currency": "EUR"},
                    "rate": 0.85,
                }

                result = await currency_conversion_service.handle_currency_request(
                    "convert -$100 USD to EUR"
                )

                assert result["success"] is True
                assert result["data"]["original"]["amount"] == -100.0

    @pytest.mark.asyncio
    async def test_handle_currency_request_generic_exception(self):
        """Test handling currency request with generic exception."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100.0,
                "request_type": "conversion",
            }

            with patch.object(
                currency_conversion_service, "convert_currency", new=AsyncMock()
            ) as mock_convert:
                mock_convert.side_effect = Exception("Generic error")

                result = await currency_conversion_service.handle_currency_request(
                    "convert $100 USD to EUR"
                )

                assert result["success"] is False
                assert "Error processing currency request" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_duplicate_validation(self):
        """Test handling currency request with duplicate validation."""
        with patch.object(
            currency_conversion_service, "parse_currency_request", new=AsyncMock()
        ) as mock_parse:
            mock_parse.return_value = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100.0,
                "request_type": "conversion",
            }

            with patch.object(
                currency_conversion_service.currency_service, "convert_currency", new=AsyncMock()
            ) as mock_convert:
                mock_convert.return_value = {
                    "original": {"amount": 100.0, "currency": "USD"},
                    "converted": {"amount": 85.0, "currency": "EUR"},
                    "rate": 0.85,
                }

                result = await currency_conversion_service.handle_currency_request(
                    "convert $100 USD to EUR"
                )

                assert result["success"] is True
                assert result["data"]["original"]["currency"] == "USD"
                assert result["data"]["converted"]["currency"] == "EUR"


class TestHelperMethods:
    """Test helper methods."""

    def test_clean_parsed_data(self):
        """Test cleaning parsed data."""
        raw_data = {
            "from_currency": " USD ",
            "to_currency": " EUR ",
            "amount": "100.50",
            "request_type": " CONVERSION ",
        }

        cleaned = currency_conversion_service._clean_parsed_data(raw_data)

        assert cleaned["from_currency"] == "USD"
        assert cleaned["to_currency"] == "EUR"
        assert cleaned["amount"] == 100.50
        assert cleaned["request_type"] == "conversion"

    def test_extract_json_from_text(self):
        """Test extracting JSON from text."""
        text_with_json = 'Here is the result: {"key": "value"} and more text'
        json_text = currency_conversion_service._extract_json_from_text(text_with_json)
        assert json_text == '{"key": "value"}'

        text_without_json = "No JSON here"
        json_text = currency_conversion_service._extract_json_from_text(text_without_json)
        assert json_text == ""
