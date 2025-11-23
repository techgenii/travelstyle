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

"""Tests for currency API endpoints and service modules."""

from unittest.mock import AsyncMock, patch

import pytest
from app.api.v1.currency import (
    convert_currency,
    get_supported_currencies,
    parse_currency_message,
    validate_currency_code,
)
from app.models.responses import ChatResponse
from app.services.currency.exceptions import CurrencyValidationError
from app.services.currency.formatter import CurrencyFormatter
from app.services.currency.helpers import CurrencyService
from app.services.currency.parser import CurrencyParser
from app.services.currency.validators import (
    normalize_currency_code,
    validate_amount,
    validate_currency_request,
)
from app.services.currency.validators import (
    validate_currency_code as validate_currency_code_boolean,
)
from fastapi import HTTPException, status


class TestConvertCurrency:
    """Test cases for the convert_currency endpoint."""

    @pytest.mark.asyncio
    async def test_convert_currency_success_with_amount(self):
        """Test successful currency conversion with amount."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 USD to EUR"}

        mock_result = {
            "success": True,
            "request_type": "conversion",
            "data": {
                "original": {"amount": 100.0, "currency": "USD"},
                "converted": {"amount": 85.0, "currency": "EUR"},
                "rate": 0.85,
                "last_updated_unix": 1640995200,
                "last_updated_utc": "2022-01-01T00:00:00Z",
            },
        }

        with patch(
            "app.api.v1.currency.currency_service.handle_currency_request",
            new=AsyncMock(return_value=mock_result),
        ):
            response = await convert_currency(request, mock_user)

        assert isinstance(response, ChatResponse)
        assert response.message == "100.00 USD = 85.00 EUR (Rate: 0.8500)"
        assert response.confidence_score == 0.9
        assert len(response.quick_replies) == 3
        assert any(qr.text == "Show rate only" for qr in response.quick_replies)
        assert any(qr.text == "Convert different amount" for qr in response.quick_replies)
        assert any(qr.text == "Other currencies" for qr in response.quick_replies)

    @pytest.mark.asyncio
    async def test_convert_currency_success_without_amount(self):
        """Test successful currency conversion without amount (rate only)."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "what's the exchange rate from USD to EUR"}

        mock_result = {
            "success": True,
            "request_type": "rate",
            "data": {
                "base_code": "USD",
                "target_code": "EUR",
                "rate": 0.85,
                "last_updated_unix": 1640995200,
                "last_updated_utc": "2022-01-01T00:00:00Z",
            },
        }

        with patch(
            "app.api.v1.currency.currency_service.handle_currency_request",
            new=AsyncMock(return_value=mock_result),
        ):
            response = await convert_currency(request, mock_user)

        assert isinstance(response, ChatResponse)
        assert response.message == "Exchange rate: 1 USD = 0.8500 EUR"
        assert response.confidence_score == 0.9
        assert len(response.quick_replies) == 2
        assert any(qr.text == "Convert amount" for qr in response.quick_replies)
        assert any(qr.text == "Other currencies" for qr in response.quick_replies)

    @pytest.mark.asyncio
    async def test_convert_currency_error_response(self):
        """Test currency conversion with error response."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 USD to INVALID"}

        mock_result = None

        with patch(
            "app.api.v1.currency.currency_service.handle_currency_request",
            new=AsyncMock(return_value=mock_result),
        ):
            response = await convert_currency(request, mock_user)

        assert isinstance(response, ChatResponse)
        assert response.message == "Sorry, I couldn't process that currency conversion request."
        assert response.confidence_score == 0.0
        assert response.quick_replies == []  # ChatResponse defaults to empty list

    @pytest.mark.asyncio
    async def test_convert_currency_missing_message(self):
        """Test currency conversion with missing message."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {}

        with pytest.raises(HTTPException) as exc_info:
            await convert_currency(request, mock_user)

        assert exc_info.value.status_code == 500  # HTTPException is caught and re-raised as 500
        assert exc_info.value.detail == "Failed to process currency request"

    @pytest.mark.asyncio
    async def test_convert_currency_empty_message(self):
        """Test currency conversion with empty message."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": ""}

        with pytest.raises(HTTPException) as exc_info:
            await convert_currency(request, mock_user)

        assert exc_info.value.status_code == 500  # HTTPException is caught and re-raised as 500
        assert exc_info.value.detail == "Failed to process currency request"

    @pytest.mark.asyncio
    async def test_convert_currency_service_exception(self):
        """Test currency conversion when service raises an exception."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 USD to EUR"}

        with patch(
            "app.api.v1.currency.currency_service.handle_currency_request",
            new=AsyncMock(side_effect=Exception("Service error")),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await convert_currency(request, mock_user)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to process currency request"


class TestGetSupportedCurrencies:
    """Test cases for the get_supported_currencies endpoint."""

    @pytest.mark.asyncio
    async def test_get_supported_currencies_success(self):
        """Test successful retrieval of supported currencies."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        mock_currencies = ["USD", "EUR", "GBP", "JPY", "CAD"]

        with patch(
            "app.api.v1.currency.currency_service.get_supported_currencies",
            return_value=mock_currencies,
        ):
            response = await get_supported_currencies(mock_user)

        assert response == {"currencies": mock_currencies}

    @pytest.mark.asyncio
    async def test_get_supported_currencies_service_exception(self):
        """Test get_supported_currencies when service raises an exception."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}

        with patch(
            "app.api.v1.currency.currency_service.get_supported_currencies",
            side_effect=Exception("Service error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_supported_currencies(mock_user)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to get supported currencies"


class TestValidateCurrencyCode:
    """Test cases for the validate_currency_code endpoint."""

    @pytest.mark.asyncio
    async def test_validate_currency_code_valid(self):
        """Test validation of a valid currency code."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": "USD"}

        with (
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=True,
            ),
            patch(
                "app.api.deps.get_current_user",
                new_callable=AsyncMock,
                return_value=mock_user,
            ),
        ):
            response = await validate_currency_code(request)

        assert response == {"currency_code": "USD", "is_valid": True, "supported": True}

    @pytest.mark.asyncio
    async def test_validate_currency_code_invalid(self):
        """Test validation of an invalid currency code."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": "INVALID"}

        with (
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=False,
            ),
            patch(
                "app.api.deps.get_current_user",
                new_callable=AsyncMock,
                return_value=mock_user,
            ),
        ):
            response = await validate_currency_code(request)

        assert response == {"currency_code": "INVALID", "is_valid": False, "supported": False}

    @pytest.mark.asyncio
    async def test_validate_currency_code_lowercase(self):
        """Test validation of a lowercase currency code (should be converted to uppercase)."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": "usd"}

        with (
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=True,
            ),
            patch(
                "app.api.deps.get_current_user",
                new_callable=AsyncMock,
                return_value=mock_user,
            ),
        ):
            response = await validate_currency_code(request)

        assert response == {"currency_code": "USD", "is_valid": True, "supported": True}

    @pytest.mark.asyncio
    async def test_validate_currency_code_missing(self):
        """Test validation with missing currency code."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {}

        with pytest.raises(HTTPException) as exc_info:
            with patch(
                "app.api.deps.get_current_user",
                new_callable=AsyncMock,
                return_value=mock_user,
            ):
                await validate_currency_code(request)

        assert exc_info.value.status_code == 500  # HTTPException is caught and re-raised as 500
        assert exc_info.value.detail == "Failed to validate currency"

    @pytest.mark.asyncio
    async def test_validate_currency_code_empty(self):
        """Test validation with empty currency code."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": ""}

        with pytest.raises(HTTPException) as exc_info:
            with patch(
                "app.api.deps.get_current_user",
                new_callable=AsyncMock,
                return_value=mock_user,
            ):
                await validate_currency_code(request)

        assert exc_info.value.status_code == 500  # HTTPException is caught and re-raised as 500
        assert exc_info.value.detail == "Failed to validate currency"

    @pytest.mark.asyncio
    async def test_validate_currency_code_service_exception(self):
        """Test validation when service raises an exception."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": "USD"}

        with (
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                side_effect=Exception("Service error"),
            ),
            patch(
                "app.api.deps.get_current_user",
                new_callable=AsyncMock,
                return_value=mock_user,
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await validate_currency_code(request)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to validate currency"


class TestParseCurrencyMessage:
    """Test cases for the parse_currency_message endpoint."""

    @pytest.mark.asyncio
    async def test_parse_currency_message_success(self):
        """Test successful parsing of currency message."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 USD to EUR"}

        mock_parsed_data = {"first_country": "USD", "second_country": "EUR", "amount": 100.0}

        with (
            patch(
                "app.api.v1.currency.currency_service.parse_currency_request",
                new=AsyncMock(return_value=mock_parsed_data),
            ),
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=True,
            ),
        ):
            response = await parse_currency_message(request, mock_user)

        assert response == {"parsed_data": mock_parsed_data, "is_valid": True}

    @pytest.mark.asyncio
    async def test_parse_currency_message_invalid_currencies(self):
        """Test parsing with invalid currency codes."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 INVALID to ALSO_INVALID"}

        mock_parsed_data = {
            "first_country": "INVALID",
            "second_country": "ALSO_INVALID",
            "amount": 100.0,
        }

        with (
            patch(
                "app.api.v1.currency.currency_service.parse_currency_request",
                new=AsyncMock(return_value=mock_parsed_data),
            ),
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=False,
            ),
        ):
            response = await parse_currency_message(request, mock_user)

        assert response == {"parsed_data": mock_parsed_data, "is_valid": False}

    @pytest.mark.asyncio
    async def test_parse_currency_message_missing_currencies(self):
        """Test parsing with missing currency codes."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 to EUR"}

        mock_parsed_data = {"first_country": "", "second_country": "EUR", "amount": 100.0}

        with (
            patch(
                "app.api.v1.currency.currency_service.parse_currency_request",
                new=AsyncMock(return_value=mock_parsed_data),
            ),
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=True,
            ),
        ):
            response = await parse_currency_message(request, mock_user)

        assert response == {"parsed_data": mock_parsed_data, "is_valid": False}

    @pytest.mark.asyncio
    async def test_parse_currency_message_missing_message(self):
        """Test parsing with missing message."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {}

        with pytest.raises(HTTPException) as exc_info:
            await parse_currency_message(request, mock_user)

        assert exc_info.value.status_code == 500  # HTTPException is caught and re-raised as 500
        assert exc_info.value.detail == "Failed to parse currency message"

    @pytest.mark.asyncio
    async def test_parse_currency_message_empty_message(self):
        """Test parsing with empty message."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": ""}

        with pytest.raises(HTTPException) as exc_info:
            await parse_currency_message(request, mock_user)

        assert exc_info.value.status_code == 500  # HTTPException is caught and re-raised as 500
        assert exc_info.value.detail == "Failed to parse currency message"

    @pytest.mark.asyncio
    async def test_parse_currency_message_service_exception(self):
        """Test parsing when service raises an exception."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 USD to EUR"}

        with patch(
            "app.api.v1.currency.currency_service.parse_currency_request",
            new=AsyncMock(side_effect=Exception("Service error")),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await parse_currency_message(request, mock_user)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to parse currency message"


class TestCurrencyAPIIntegration:
    """Integration tests for currency API endpoints."""

    @pytest.mark.asyncio
    async def test_convert_currency_integration_with_real_service(self):
        """Test currency conversion with mocked but realistic service responses."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 50 USD to EUR"}

        # Mock the service to return a realistic response
        mock_result = {
            "success": True,
            "request_type": "conversion",
            "data": {
                "original": {"amount": 50.0, "currency": "USD"},
                "converted": {"amount": 42.5, "currency": "EUR"},
                "rate": 0.85,
                "last_updated_unix": 1640995200,
                "last_updated_utc": "2022-01-01T00:00:00Z",
            },
        }

        with patch(
            "app.api.v1.currency.currency_service.handle_currency_request",
            new=AsyncMock(return_value=mock_result),
        ):
            response = await convert_currency(request, mock_user)

        assert isinstance(response, ChatResponse)
        assert "50.00 USD = 42.50 EUR" in response.message
        assert response.confidence_score == 0.9
        assert len(response.quick_replies) == 3

    @pytest.mark.asyncio
    async def test_validate_currency_code_integration(self):
        """Test currency validation with realistic service behavior."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}

        # Test with valid currency
        request_valid = {"currency_code": "USD"}
        with (
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=True,
            ),
            patch(
                "app.api.deps.get_current_user",
                new_callable=AsyncMock,
                return_value=mock_user,
            ),
        ):
            response = await validate_currency_code(request_valid)
            assert response["is_valid"] is True
            assert response["supported"] is True

        # Test with invalid currency
        request_invalid = {"currency_code": "INVALID"}
        with (
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=False,
            ),
            patch(
                "app.api.deps.get_current_user",
                new_callable=AsyncMock,
                return_value=mock_user,
            ),
        ):
            response = await validate_currency_code(request_invalid)
            assert response["is_valid"] is False
            assert response["supported"] is False

    @pytest.mark.asyncio
    async def test_get_supported_currencies_integration(self):
        """Test getting supported currencies with realistic service behavior."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        expected_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"]

        with patch(
            "app.api.v1.currency.currency_service.get_supported_currencies",
            return_value=expected_currencies,
        ):
            response = await get_supported_currencies(mock_user)

        assert response["currencies"] == expected_currencies
        assert len(response["currencies"]) > 0
        assert "USD" in response["currencies"]
        assert "EUR" in response["currencies"]


class TestCurrencyAPIErrorHandling:
    """Test error handling scenarios for currency API endpoints."""

    @pytest.mark.asyncio
    async def test_convert_currency_network_error(self):
        """Test currency conversion when network error occurs."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 USD to EUR"}

        with patch(
            "app.api.v1.currency.currency_service.handle_currency_request",
            new=AsyncMock(side_effect=ConnectionError("Network error")),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await convert_currency(request, mock_user)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to process currency request"

    @pytest.mark.asyncio
    async def test_convert_currency_timeout_error(self):
        """Test currency conversion when timeout error occurs."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 USD to EUR"}

        with patch(
            "app.api.v1.currency.currency_service.handle_currency_request",
            new=AsyncMock(side_effect=TimeoutError("Request timeout")),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await convert_currency(request, mock_user)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to process currency request"

    @pytest.mark.asyncio
    async def test_validate_currency_code_with_special_characters(self):
        """Test currency validation with special characters."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": "USD$"}

        with (
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=False,
            ),
            patch(
                "app.api.deps.get_current_user",
                new_callable=AsyncMock,
                return_value=mock_user,
            ),
        ):
            response = await validate_currency_code(request)

        assert response["currency_code"] == "USD$"
        assert response["is_valid"] is False
        assert response["supported"] is False

    @pytest.mark.asyncio
    async def test_parse_currency_message_with_complex_input(self):
        """Test parsing with complex user input."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "I need to convert 1,234.56 US dollars to euros for my trip to Paris"}

        mock_parsed_data = {"first_country": "USD", "second_country": "EUR", "amount": 1234.56}

        with (
            patch(
                "app.api.v1.currency.currency_service.parse_currency_request",
                new=AsyncMock(return_value=mock_parsed_data),
            ),
            patch(
                "app.api.v1.currency.currency_service.validate_currency_code",
                return_value=True,
            ),
        ):
            response = await parse_currency_message(request, mock_user)

        assert response["parsed_data"] == mock_parsed_data
        assert response["is_valid"] is True


# ---- Currency Service Module Tests ----


class TestCurrencyFormatter:
    """Test cases for the CurrencyFormatter class."""

    def test_format_currency_response_success(self):
        """Test successful currency response formatting."""
        formatter = CurrencyFormatter()
        response = formatter.format_currency_response("USD", "EUR", 100.0, 0.85, 85.0)

        assert "100.00 USD" in response
        assert "85.00 EUR" in response
        assert "0.8500" in response
        assert "💱 **Currency Conversion**" in response

    def test_format_currency_response_with_zero_amount(self):
        """Test currency response formatting with zero amount."""
        formatter = CurrencyFormatter()
        response = formatter.format_currency_response("USD", "EUR", 0.0, 0.85, 0.0)

        assert "0.00 USD" in response
        assert "0.00 EUR" in response

    def test_format_currency_response_with_large_amount(self):
        """Test currency response formatting with large amount."""
        formatter = CurrencyFormatter()
        response = formatter.format_currency_response("USD", "EUR", 1000000.0, 0.85, 850000.0)

        assert "1,000,000.00 USD" in response
        assert "850,000.00 EUR" in response

    def test_format_exchange_rate_response_success(self):
        """Test successful exchange rate response formatting."""
        formatter = CurrencyFormatter()
        response = formatter.format_exchange_rate_response("USD", "EUR", 0.85)

        assert "1 USD" in response
        assert "0.8500 EUR" in response
        assert "📊 **Exchange Rate**" in response

    def test_format_exchange_rate_response_with_timestamp(self):
        """Test exchange rate response formatting with timestamp."""
        formatter = CurrencyFormatter()
        response = formatter.format_exchange_rate_response(
            "USD", "EUR", 0.85, "2024-01-01T12:00:00Z"
        )

        assert "1 USD" in response
        assert "0.8500 EUR" in response
        assert "2024-01-01T12:00:00Z" in response

    def test_format_currency_help_response(self):
        """Test currency help response formatting."""
        formatter = CurrencyFormatter()
        response = formatter.format_currency_help_response()

        assert "💱 **Currency Converter Help**" in response
        assert "Convert 100 USD to EUR" in response
        assert "Supported Currencies" in response

    def test_format_error_response_default(self):
        """Test error response formatting with default message."""
        formatter = CurrencyFormatter()
        response = formatter.format_error_response()

        assert "❌ **Currency Conversion Error**" in response
        assert "Unknown error" in response

    def test_format_error_response_custom(self):
        """Test error response formatting with custom message."""
        formatter = CurrencyFormatter()
        response = formatter.format_error_response("Invalid currency code")

        assert "❌ **Currency Conversion Error**" in response
        assert "Invalid currency code" in response

    def test_format_currency_response_exception_handling(self):
        """Test currency response formatting with exception handling."""
        formatter = CurrencyFormatter()

        # Test with invalid data that would cause an exception in the formatting logic
        # This tests the actual exception handling within the method
        response = formatter.format_currency_response(
            "USD", "EUR", float("inf"), 0.85, float("inf")
        )
        # The method should handle the infinity values gracefully and return a proper response
        assert "Sorry, I encountered an error" in response

    def test_format_exchange_rate_response_exception_handling(self):
        """Test exchange rate response formatting with exception handling."""
        formatter = CurrencyFormatter()

        # Test with invalid data that would cause an exception in the formatting logic
        # This tests the actual exception handling within the method
        response = formatter.format_exchange_rate_response("USD", "EUR", float("inf"))
        # The method should handle the infinity values gracefully and return a proper response
        assert "Sorry, I encountered an error" in response


class TestCurrencyValidators:
    """Test cases for the currency validation functions."""

    def test_validate_currency_code_valid(self):
        """Test validation of valid currency codes."""
        assert validate_currency_code_boolean("USD") is True
        assert validate_currency_code_boolean("EUR") is True
        assert validate_currency_code_boolean("GBP") is True
        assert validate_currency_code_boolean("JPY") is True

    def test_validate_currency_code_invalid(self):
        """Test validation of invalid currency codes."""
        assert validate_currency_code_boolean("INVALID") is False
        assert validate_currency_code_boolean("XYZ") is False
        assert validate_currency_code_boolean("123") is False

    def test_validate_currency_code_case_insensitive(self):
        """Test validation of currency codes with different cases."""
        assert validate_currency_code_boolean("usd") is True
        assert validate_currency_code_boolean("Usd") is True
        assert validate_currency_code_boolean("USD") is True

    def test_validate_currency_code_with_whitespace(self):
        """Test validation of currency codes with whitespace."""
        assert validate_currency_code_boolean(" USD ") is True
        assert validate_currency_code_boolean("  EUR  ") is True

    def test_validate_currency_code_empty_or_none(self):
        """Test validation of empty or None currency codes."""
        assert validate_currency_code_boolean("") is False
        assert validate_currency_code_boolean(None) is False

    def test_validate_currency_code_non_string(self):
        """Test validation of non-string currency codes."""
        assert validate_currency_code_boolean(123) is False
        assert validate_currency_code_boolean(True) is False
        assert validate_currency_code_boolean([]) is False

    def test_validate_amount_valid(self):
        """Test validation of valid amounts."""
        assert validate_amount(100.0) is True
        assert validate_amount(50) is True
        assert validate_amount(0.01) is True
        assert validate_amount(1000000) is True

    def test_validate_amount_invalid(self):
        """Test validation of invalid amounts."""
        assert validate_amount(0) is False
        assert validate_amount(-100) is False
        assert validate_amount("100") is False
        assert validate_amount(None) is False
        assert validate_amount([]) is False

    def test_validate_currency_request_success(self):
        """Test successful validation of currency request."""
        assert validate_currency_request("USD", "EUR", 100.0) is True
        assert validate_currency_request("GBP", "JPY", 50) is True

    def test_validate_currency_request_invalid_from_currency(self):
        """Test validation failure with invalid from currency."""
        with pytest.raises(CurrencyValidationError, match="Invalid from_currency"):
            validate_currency_request("INVALID", "EUR", 100.0)

    def test_validate_currency_request_invalid_to_currency(self):
        """Test validation failure with invalid to currency."""
        with pytest.raises(CurrencyValidationError, match="Invalid to_currency"):
            validate_currency_request("USD", "INVALID", 100.0)

    def test_validate_currency_request_invalid_amount(self):
        """Test validation failure with invalid amount."""
        with pytest.raises(CurrencyValidationError, match="Invalid amount"):
            validate_currency_request("USD", "EUR", -100)

    def test_normalize_currency_code_success(self):
        """Test successful normalization of currency codes."""
        assert normalize_currency_code("usd") == "USD"
        assert normalize_currency_code(" USD ") == "USD"
        assert normalize_currency_code("Eur") == "EUR"

    def test_normalize_currency_code_empty(self):
        """Test normalization failure with empty currency code."""
        with pytest.raises(CurrencyValidationError, match="Currency code cannot be empty"):
            normalize_currency_code("")

    def test_normalize_currency_code_unsupported(self):
        """Test normalization failure with unsupported currency code."""
        with pytest.raises(CurrencyValidationError, match="Unsupported currency code"):
            normalize_currency_code("INVALID")


class TestCurrencyParser:
    """Test cases for the CurrencyParser class."""

    def test_is_currency_request_convert_keywords(self):
        """Test detection of currency requests with convert keywords."""
        parser = CurrencyParser()

        assert parser.is_currency_request("convert 100 USD to EUR") is True
        assert parser.is_currency_request("exchange 50 EUR for USD") is True
        assert parser.is_currency_request("what's the rate for USD to EUR") is True

    def test_is_currency_request_currency_codes(self):
        """Test detection of currency requests with currency codes."""
        parser = CurrencyParser()

        assert parser.is_currency_request("100 USD to EUR") is True
        assert parser.is_currency_request("USD EUR rate") is True
        assert parser.is_currency_request("50 GBP to JPY") is True

    def test_is_currency_request_country_names(self):
        """Test detection of currency requests with country names."""
        parser = CurrencyParser()

        assert parser.is_currency_request("convert 100 dollars to euros") is True
        assert parser.is_currency_request("50 pounds to yen") is True
        assert parser.is_currency_request("US to European rate") is True

    def test_is_currency_request_conversion_indicators(self):
        """Test detection of currency requests with conversion indicators."""
        parser = CurrencyParser()

        assert parser.is_currency_request("100 USD = EUR") is True
        assert parser.is_currency_request("USD into EUR") is True
        assert parser.is_currency_request("50 USD equals EUR") is True

    def test_is_currency_request_with_amounts(self):
        """Test detection of currency requests with amounts."""
        parser = CurrencyParser()

        assert parser.is_currency_request("100 USD to EUR") is True
        assert parser.is_currency_request("1,234.56 GBP to JPY") is True
        assert parser.is_currency_request("0.50 EUR to USD") is True

    def test_is_currency_request_not_currency(self):
        """Test detection of non-currency requests."""
        parser = CurrencyParser()

        assert parser.is_currency_request("Hello, how are you?") is False
        assert parser.is_currency_request("What's the weather like?") is False
        assert parser.is_currency_request("") is False
        assert parser.is_currency_request(None) is False

    def test_get_supported_currencies(self):
        """Test getting supported currencies."""
        parser = CurrencyParser()
        currencies = parser.get_supported_currencies()

        assert isinstance(currencies, list)
        assert len(currencies) > 0
        assert "USD" in currencies
        assert "EUR" in currencies
        assert "GBP" in currencies
        assert currencies == sorted(currencies)

    def test_extract_json_from_text_success(self):
        """Test successful JSON extraction from text."""
        parser = CurrencyParser()

        text = 'Here is some text {"key": "value"} and more text'
        json_text = parser._extract_json_from_text(text)

        assert json_text == '{"key": "value"}'

    def test_extract_json_from_text_no_json(self):
        """Test JSON extraction when no JSON is present."""
        parser = CurrencyParser()

        text = "Here is some text without JSON"
        json_text = parser._extract_json_from_text(text)

        assert json_text == ""

    def test_extract_json_from_text_multiple_braces(self):
        """Test JSON extraction with multiple brace patterns."""
        parser = CurrencyParser()

        text = 'Text {not json} and {"key": "value"} more text'
        json_text = parser._extract_json_from_text(text)

        assert json_text == '{"key": "value"}'

    def test_clean_parsed_data_success(self):
        """Test successful cleaning of parsed data."""
        parser = CurrencyParser()

        data = {
            "from_currency": " usd ",
            "to_currency": " eur ",
            "amount": "100.50",
            "request_type": " conversion ",
        }

        cleaned = parser._clean_parsed_data(data)

        assert cleaned["from_currency"] == "USD"
        assert cleaned["to_currency"] == "EUR"
        assert cleaned["amount"] == 100.50
        assert cleaned["request_type"] == "conversion"

    def test_clean_parsed_data_invalid_amount(self):
        """Test cleaning of parsed data with invalid amount."""
        parser = CurrencyParser()

        data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "amount": "invalid",
            "request_type": "conversion",
        }

        cleaned = parser._clean_parsed_data(data)
        assert cleaned is None

    def test_clean_parsed_data_missing_fields(self):
        """Test cleaning of parsed data with missing fields."""
        parser = CurrencyParser()

        data = {"from_currency": "USD"}
        cleaned = parser._clean_parsed_data(data)

        assert cleaned["from_currency"] == "USD"
        assert "to_currency" not in cleaned
        assert "amount" not in cleaned

    @pytest.mark.asyncio
    async def test_parse_currency_request_success(self):
        """Test successful parsing of currency request."""
        parser = CurrencyParser()

        mock_response = '{"from_currency": "USD", "to_currency": "EUR", "amount": 100.0, "request_type": "conversion"}'

        with patch("app.services.currency.parser.openai_service.get_completion") as mock_openai:
            mock_openai.return_value = mock_response

            result = await parser.parse_currency_request("convert 100 USD to EUR")

            assert result is not None
            assert result["from_currency"] == "USD"
            assert result["to_currency"] == "EUR"
            assert result["amount"] == 100.0
            assert result["request_type"] == "conversion"

    @pytest.mark.asyncio
    async def test_parse_currency_request_no_openai_response(self):
        """Test parsing when OpenAI returns no response."""
        parser = CurrencyParser()

        with patch("app.services.currency.parser.openai_service.get_completion") as mock_openai:
            mock_openai.return_value = None

            result = await parser.parse_currency_request("convert 100 USD to EUR")
            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_invalid_json(self):
        """Test parsing when OpenAI returns invalid JSON."""
        parser = CurrencyParser()

        mock_response = "This is not JSON"

        with patch("app.services.currency.parser.openai_service.get_completion") as mock_openai:
            mock_openai.return_value = mock_response

            result = await parser.parse_currency_request("convert 100 USD to EUR")
            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_invalid_currency_codes(self):
        """Test parsing when OpenAI returns invalid currency codes."""
        parser = CurrencyParser()

        mock_response = '{"from_currency": "INVALID", "to_currency": "EUR", "amount": 100.0, "request_type": "conversion"}'

        with patch("app.services.currency.parser.openai_service.get_completion") as mock_openai:
            mock_openai.return_value = mock_response

            result = await parser.parse_currency_request("convert 100 INVALID to EUR")
            assert result is None

    @pytest.mark.asyncio
    async def test_parse_currency_request_missing_required_fields(self):
        """Test parsing when OpenAI returns missing required fields."""
        parser = CurrencyParser()

        mock_response = '{"from_currency": "USD", "request_type": "conversion"}'

        with patch("app.services.currency.parser.openai_service.get_completion") as mock_openai:
            mock_openai.return_value = mock_response

            result = await parser.parse_currency_request("convert 100 USD to EUR")
            assert result is None


class TestCurrencyService:
    """Test cases for the CurrencyService class."""

    def test_currency_service_initialization(self):
        """Test CurrencyService initialization."""
        service = CurrencyService()

        assert hasattr(service, "api")
        assert hasattr(service, "parser")
        assert hasattr(service, "formatter")

    def test_is_currency_request_delegation(self):
        """Test that is_currency_request delegates to parser."""
        service = CurrencyService()

        with patch.object(service.parser, "is_currency_request") as mock_parser:
            mock_parser.return_value = True
            result = service.is_currency_request("convert 100 USD to EUR")

            assert result is True
            mock_parser.assert_called_once_with("convert 100 USD to EUR")

    def test_get_supported_currencies_delegation(self):
        """Test that get_supported_currencies delegates to parser."""
        service = CurrencyService()

        with patch.object(service.parser, "get_supported_currencies") as mock_parser:
            mock_parser.return_value = ["USD", "EUR", "GBP"]
            result = service.get_supported_currencies()

            assert result == ["USD", "EUR", "GBP"]
            mock_parser.assert_called_once()

    def test_validate_currency_code_backward_compatibility(self):
        """Test backward compatibility of validate_currency_code method."""
        service = CurrencyService()

        assert service.validate_currency_code("USD") is True
        assert service.validate_currency_code("INVALID") is False

    def test_format_currency_response_backward_compatibility(self):
        """Test backward compatibility of format_currency_response method."""
        service = CurrencyService()

        original_data = {"currency": "USD", "amount": 100.0}
        converted_data = {"currency": "EUR", "amount": 85.0}

        response = service.format_currency_response(original_data, converted_data, 0.85)

        assert "100.00 USD = 85.00 EUR" in response
        assert "Rate: 0.8500" in response

    def test_format_currency_response_exception_handling(self):
        """Test exception handling in format_currency_response."""
        service = CurrencyService()

        # Test with invalid data that would cause an exception
        original_data = {"currency": "USD", "amount": "invalid"}
        converted_data = {"currency": "EUR", "amount": 85.0}

        response = service.format_currency_response(original_data, converted_data, 0.85)

        assert "Sorry, I encountered an error" in response

    def test_format_exchange_rate_response_delegation(self):
        """Test that format_exchange_rate_response delegates to formatter."""
        service = CurrencyService()

        with patch.object(service.formatter, "format_exchange_rate_response") as mock_formatter:
            mock_formatter.return_value = "Formatted response"
            result = service.format_exchange_rate_response("USD", "EUR", 0.85)

            assert result == "Formatted response"
            mock_formatter.assert_called_once_with("USD", "EUR", 0.85, None)

    def test_format_currency_help_response_delegation(self):
        """Test that format_currency_help_response delegates to formatter."""
        service = CurrencyService()

        with patch.object(service.formatter, "format_currency_help_response") as mock_formatter:
            mock_formatter.return_value = "Help response"
            result = service.format_currency_help_response()

            assert result == "Help response"
            mock_formatter.assert_called_once()

    def test_format_error_response_delegation(self):
        """Test that format_error_response delegates to formatter."""
        service = CurrencyService()

        with patch.object(service.formatter, "format_error_response") as mock_formatter:
            mock_formatter.return_value = "Error response"
            result = service.format_error_response("Test error")

            assert result == "Error response"
            mock_formatter.assert_called_once_with("Test error")

    @pytest.mark.asyncio
    async def test_handle_currency_request_help_type(self):
        """Test handling of help request type."""
        service = CurrencyService()

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.return_value = {"request_type": "help"}

            result = await service.handle_currency_request("help with currency")

            assert result["success"] is True
            assert result["request_type"] == "help"
            assert "Currency Converter Help" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_rate_type_success(self):
        """Test handling of rate request type with success."""
        service = CurrencyService()

        mock_parsed_data = {"request_type": "rate", "from_currency": "USD", "to_currency": "EUR"}

        mock_rate_data = {
            "base_code": "USD",
            "target_code": "EUR",
            "rate": 0.85,
            "last_updated_utc": "2024-01-01T12:00:00Z",
        }

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.return_value = mock_parsed_data

            with patch.object(service, "get_pair_exchange_rate") as mock_get_rate:
                mock_get_rate.return_value = mock_rate_data

                result = await service.handle_currency_request("USD to EUR rate")

                assert result["success"] is True
                assert result["request_type"] == "rate"
                assert "1 USD" in result["message"]
                assert "0.8500 EUR" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_rate_type_missing_currencies(self):
        """Test handling of rate request type with missing currencies."""
        service = CurrencyService()

        mock_parsed_data = {"request_type": "rate", "from_currency": "", "to_currency": "EUR"}

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.return_value = mock_parsed_data

            result = await service.handle_currency_request("to EUR rate")

            assert result["success"] is False
            assert "Missing currency codes" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_rate_type_no_rate_data(self):
        """Test handling of rate request type when no rate data is returned."""
        service = CurrencyService()

        mock_parsed_data = {"request_type": "rate", "from_currency": "USD", "to_currency": "EUR"}

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.return_value = mock_parsed_data

            with patch.object(service, "get_pair_exchange_rate") as mock_get_rate:
                mock_get_rate.return_value = None

                result = await service.handle_currency_request("USD to EUR rate")

                assert result["success"] is False
                assert "Could not fetch exchange rate" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_conversion_type_success(self):
        """Test handling of conversion request type with success."""
        service = CurrencyService()

        mock_parsed_data = {
            "request_type": "conversion",
            "from_currency": "USD",
            "to_currency": "EUR",
            "amount": 100.0,
        }

        mock_conversion_data = {
            "original": {"currency": "USD", "amount": 100.0},
            "converted": {"currency": "EUR", "amount": 85.0},
            "rate": 0.85,
        }

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.return_value = mock_parsed_data

            with patch.object(service, "convert_currency") as mock_convert:
                mock_convert.return_value = mock_conversion_data

                result = await service.handle_currency_request("convert 100 USD to EUR")

                assert result["success"] is True
                assert result["request_type"] == "conversion"
                assert "100.00 USD = 85.00 EUR" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_conversion_type_missing_data(self):
        """Test handling of conversion request type with missing data."""
        service = CurrencyService()

        mock_parsed_data = {
            "request_type": "conversion",
            "from_currency": "USD",
            "to_currency": "",
            "amount": 100.0,
        }

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.return_value = mock_parsed_data

            result = await service.handle_currency_request("convert 100 USD to")

            assert result["success"] is False
            assert "Missing required conversion data" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_conversion_type_no_conversion_data(self):
        """Test handling of conversion request type when no conversion data is returned."""
        service = CurrencyService()

        mock_parsed_data = {
            "request_type": "conversion",
            "from_currency": "USD",
            "to_currency": "EUR",
            "amount": 100.0,
        }

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.return_value = mock_parsed_data

            with patch.object(service, "convert_currency") as mock_convert:
                mock_convert.return_value = None

                result = await service.handle_currency_request("convert 100 USD to EUR")

                assert result["success"] is False
                assert "Exchange rate not available" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_unknown_type(self):
        """Test handling of unknown request type."""
        service = CurrencyService()

        mock_parsed_data = {"request_type": "unknown", "from_currency": "USD", "to_currency": "EUR"}

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.return_value = mock_parsed_data

            result = await service.handle_currency_request("unknown request")

            assert result["success"] is False
            assert "Unknown request type" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_parser_returns_none(self):
        """Test handling when parser returns None."""
        service = CurrencyService()

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.return_value = None

            result = await service.handle_currency_request("invalid request")

            assert result["success"] is False
            assert "Could not parse currency request" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_request_exception_handling(self):
        """Test exception handling in handle_currency_request."""
        service = CurrencyService()

        with patch.object(service.parser, "parse_currency_request") as mock_parser:
            mock_parser.side_effect = Exception("Test exception")

            result = await service.handle_currency_request("test request")

            assert result["success"] is False
            assert "Error processing currency request" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_currency_help_request_success(self):
        """Test successful handling of currency help request."""
        service = CurrencyService()

        result = await service.handle_currency_help_request("help with currency")

        assert result["success"] is True
        assert result["request_type"] == "help"
        assert "Currency Converter Help" in result["response"]

    @pytest.mark.asyncio
    async def test_handle_currency_help_request_no_help(self):
        """Test handling of non-help currency request."""
        service = CurrencyService()

        result = await service.handle_currency_help_request("convert 100 USD to EUR")

        assert result is None

    def test_clean_parsed_data_backward_compatibility(self):
        """Test backward compatibility of _clean_parsed_data method."""
        service = CurrencyService()

        data = {"first_country": "USD", "second_country": "EUR", "amount": 100.0}

        with patch.object(service.parser, "_clean_parsed_data") as mock_clean:
            mock_clean.return_value = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100.0,
            }

            result = service._clean_parsed_data(data)

            assert result == {"from_currency": "USD", "to_currency": "EUR", "amount": 100.0}
            mock_clean.assert_called_once_with(data)

    def test_extract_json_from_text_backward_compatibility(self):
        """Test backward compatibility of _extract_json_from_text method."""
        service = CurrencyService()

        text = 'Text {"key": "value"} more text'

        with patch.object(service.parser, "_extract_json_from_text") as mock_extract:
            mock_extract.return_value = '{"key": "value"}'

            result = service._extract_json_from_text(text)

            assert result == '{"key": "value"}'
            mock_extract.assert_called_once_with(text)


# ---- Integration Tests with Authenticated Client ----


class TestCurrencyEndpoints:
    """Test currency API endpoints with authenticated client."""

    def test_exchange_rates_success(self, authenticated_client):
        """Test successful exchange rates retrieval."""
        with patch("app.services.currency.CurrencyService.get_exchange_rates") as mock_get_rates:
            mock_get_rates.return_value = {
                "base_code": "USD",
                "conversion_rates": {"EUR": 0.85, "GBP": 0.73, "JPY": 110.50},
                "last_updated_unix": 1234567890,
                "last_updated_utc": "2024-01-01T12:00:00Z",
            }
            response = authenticated_client.get("/api/v1/currency/rates/USD")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "base_code" in data
            assert "conversion_rates" in data
            assert "EUR" in data["conversion_rates"]

    def test_exchange_rates_not_found(self, authenticated_client):
        """Test exchange rates when not available."""
        with patch("app.services.currency.CurrencyService.get_exchange_rates") as mock_get_rates:
            mock_get_rates.return_value = None
            response = authenticated_client.get("/api/v1/currency/rates/INVALID")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Exchange rates not available" in response.json()["detail"]

    def test_exchange_rates_service_exception(self, authenticated_client):
        """Test exchange rates when service raises exception (500)."""
        with patch("app.services.currency.CurrencyService.get_exchange_rates") as mock_get_rates:
            mock_get_rates.side_effect = Exception("Service error")
            response = authenticated_client.get("/api/v1/currency/rates/USD")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve exchange rates" in response.json()["detail"]

    def test_currency_conversion_amount_success(self, authenticated_client):
        """Test successful currency conversion."""
        with patch("app.services.currency.CurrencyService.convert_currency") as mock_convert:
            mock_convert.return_value = {
                "original": {"amount": 100.0, "currency": "USD"},
                "converted": {"amount": 85.0, "currency": "EUR"},
                "rate": 0.85,
                "last_updated_unix": 1234567890,
                "last_updated_utc": "2024-01-01T12:00:00Z",
            }
            response = authenticated_client.post(
                "/api/v1/currency/convert-amount",
                json={"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "original" in data
            assert "converted" in data
            assert data["original"]["currency"] == "USD"
            assert data["converted"]["currency"] == "EUR"

    def test_currency_conversion_amount_failure(self, authenticated_client):
        """Test currency conversion when it fails."""
        with patch("app.services.currency.CurrencyService.convert_currency") as mock_convert:
            mock_convert.return_value = None
            response = authenticated_client.post(
                "/api/v1/currency/convert-amount",
                json={"amount": 100.0, "from_currency": "INVALID", "to_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Currency conversion failed" in response.json()["detail"]

    def test_currency_conversion_amount_service_exception(self, authenticated_client):
        """Test currency conversion when service raises exception (500)."""
        with patch("app.services.currency.CurrencyService.convert_currency") as mock_convert:
            mock_convert.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/currency/convert-amount",
                json={"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to convert currency" in response.json()["detail"]

    def test_pair_exchange_rate_success(self, authenticated_client):
        """Test successful pair exchange rate retrieval."""
        with patch("app.services.currency.CurrencyService.get_pair_exchange_rate") as mock_get_pair:
            mock_get_pair.return_value = {
                "base_code": "USD",
                "target_code": "EUR",
                "rate": 0.85,
                "last_updated_unix": 1234567890,
                "last_updated_utc": "2024-01-01T12:00:00Z",
            }
            response = authenticated_client.post(
                "/api/v1/currency/pair",
                json={"base_currency": "USD", "target_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["base_code"] == "USD"
            assert data["target_code"] == "EUR"
            assert data["rate"] == 0.85

    def test_pair_exchange_rate_not_found(self, authenticated_client):
        """Test pair exchange rate when not available."""
        with patch("app.services.currency.CurrencyService.get_pair_exchange_rate") as mock_get_pair:
            mock_get_pair.return_value = None
            response = authenticated_client.post(
                "/api/v1/currency/pair",
                json={"base_currency": "USD", "target_currency": "INVALID"},
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Exchange rate not available" in response.json()["detail"]

    def test_pair_exchange_rate_service_exception(self, authenticated_client):
        """Test pair exchange rate when service raises exception (500)."""
        with patch("app.services.currency.CurrencyService.get_pair_exchange_rate") as mock_get_pair:
            mock_get_pair.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/currency/pair",
                json={"base_currency": "USD", "target_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve pair exchange rate" in response.json()["detail"]

    def test_currency_convert_chat_success(self, authenticated_client):
        """Test successful currency conversion via chat endpoint."""
        with patch("app.services.currency.CurrencyService.handle_currency_request") as mock_handle:
            mock_handle.return_value = {
                "success": True,
                "request_type": "conversion",
                "data": {
                    "original": {"amount": 100.0, "currency": "USD"},
                    "converted": {"amount": 85.0, "currency": "EUR"},
                    "rate": 0.85,
                },
            }
            response = authenticated_client.post(
                "/api/v1/currency/convert",
                json={"message": "convert 100 USD to EUR"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
            assert "100.00 USD = 85.00 EUR" in data["message"]

    def test_currency_convert_chat_failure(self, authenticated_client):
        """Test currency conversion via chat endpoint when it fails."""
        with patch("app.services.currency.CurrencyService.handle_currency_request") as mock_handle:
            mock_handle.return_value = {"success": False, "message": "Invalid currencies"}
            response = authenticated_client.post(
                "/api/v1/currency/convert",
                json={"message": "convert 100 INVALID to EUR"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
            assert "Invalid currencies" in data["message"]

    def test_get_supported_currencies(self, authenticated_client):
        """Test getting supported currencies."""
        response = authenticated_client.get("/api/v1/currency/supported")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "currencies" in data
        assert len(data["currencies"]) > 0

    def test_validate_currency_code_valid(self, authenticated_client):
        """Test validating a valid currency code."""
        response = authenticated_client.post(
            "/api/v1/currency/validate", json={"currency_code": "USD"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_valid"] is True
        assert data["currency_code"] == "USD"

    def test_validate_currency_code_invalid(self, authenticated_client):
        """Test validating an invalid currency code."""
        response = authenticated_client.post(
            "/api/v1/currency/validate", json={"currency_code": "INVALID"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_valid"] is False
        assert data["currency_code"] == "INVALID"

    def test_parse_currency_message(self, authenticated_client):
        """Test parsing currency message."""
        response = authenticated_client.post(
            "/api/v1/currency/parse",
            json={"message": "convert 100 USD to EUR"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "parsed_data" in data
        assert "is_valid" in data
        parsed_data = data["parsed_data"]
        assert "amount" in parsed_data
        assert "from_currency" in parsed_data
        assert "to_currency" in parsed_data
        assert parsed_data["amount"] == 100.0
        assert parsed_data["from_currency"] == "USD"
        assert parsed_data["to_currency"] == "EUR"

    def test_currency_no_auth(self, client):
        """Test currency endpoints without authentication."""
        # Test exchange rates endpoint
        response = client.get("/api/v1/currency/rates/USD")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test currency conversion endpoint
        response = client.post(
            "/api/v1/currency/convert-amount",
            json={"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test pair exchange rate endpoint
        response = client.post(
            "/api/v1/currency/pair",
            json={"base_currency": "USD", "target_currency": "EUR"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test chat conversion endpoint
        response = client.post(
            "/api/v1/currency/convert",
            json={"message": "convert 100 USD to EUR"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test supported currencies endpoint
        response = client.get("/api/v1/currency/supported")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test validate currency endpoint
        response = client.post("/api/v1/currency/validate", json={"currency_code": "USD"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test parse message endpoint
        response = client.post(
            "/api/v1/currency/parse",
            json={"message": "convert 100 USD to EUR"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
