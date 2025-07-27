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

"""Tests for currency API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from app.api.v1.currency import (
    convert_currency,
    get_supported_currencies,
    parse_currency_message,
    validate_currency_code,
)
from app.models.responses import ChatResponse
from fastapi import HTTPException


class TestConvertCurrency:
    """Test cases for the convert_currency endpoint."""

    @pytest.mark.asyncio
    async def test_convert_currency_success_with_amount(self):
        """Test successful currency conversion with amount."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 USD to EUR"}

        mock_result = {
            "type": "currency_rate",
            "message": "100.00 USD = 85.00 EUR (Rate: 0.8500)",
            "amount": 100.0,
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "converted_amount": 85.0,
            "last_updated": "2024-01-01T12:00:00Z",
        }

        with patch(
            "app.api.v1.currency.currency_conversion_service.handle_currency_request",
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
            "type": "currency_rate",
            "message": "The current exchange rate from USD to EUR is 0.8500",
            "amount": 0.0,
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "converted_amount": 0.0,
            "last_updated": "2024-01-01T12:00:00Z",
        }

        with patch(
            "app.api.v1.currency.currency_conversion_service.handle_currency_request",
            new=AsyncMock(return_value=mock_result),
        ):
            response = await convert_currency(request, mock_user)

        assert isinstance(response, ChatResponse)
        assert response.message == "The current exchange rate from USD to EUR is 0.8500"
        assert response.confidence_score == 0.9
        assert len(response.quick_replies) == 2
        assert not any(qr.text == "Show rate only" for qr in response.quick_replies)
        assert any(qr.text == "Convert different amount" for qr in response.quick_replies)
        assert any(qr.text == "Other currencies" for qr in response.quick_replies)

    @pytest.mark.asyncio
    async def test_convert_currency_error_response(self):
        """Test currency conversion with error response."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"message": "convert 100 USD to INVALID"}

        mock_result = {
            "type": "currency_error",
            "message": "Sorry, I don't support the currency 'INVALID'.",
        }

        with patch(
            "app.api.v1.currency.currency_conversion_service.handle_currency_request",
            new=AsyncMock(return_value=mock_result),
        ):
            response = await convert_currency(request, mock_user)

        assert isinstance(response, ChatResponse)
        assert response.message == "Sorry, I don't support the currency 'INVALID'."
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
            "app.api.v1.currency.currency_conversion_service.handle_currency_request",
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
            "app.api.v1.currency.currency_conversion_service.get_supported_currencies",
            return_value=mock_currencies,
        ):
            response = await get_supported_currencies(mock_user)

        assert response == {"currencies": mock_currencies}

    @pytest.mark.asyncio
    async def test_get_supported_currencies_service_exception(self):
        """Test get_supported_currencies when service raises an exception."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}

        with patch(
            "app.api.v1.currency.currency_conversion_service.get_supported_currencies",
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

        with patch(
            "app.api.v1.currency.currency_conversion_service.validate_currency_code",
            return_value=True,
        ):
            response = await validate_currency_code(request, mock_user)

        assert response == {"currency_code": "USD", "is_valid": True, "supported": True}

    @pytest.mark.asyncio
    async def test_validate_currency_code_invalid(self):
        """Test validation of an invalid currency code."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": "INVALID"}

        with patch(
            "app.api.v1.currency.currency_conversion_service.validate_currency_code",
            return_value=False,
        ):
            response = await validate_currency_code(request, mock_user)

        assert response == {"currency_code": "INVALID", "is_valid": False, "supported": False}

    @pytest.mark.asyncio
    async def test_validate_currency_code_lowercase(self):
        """Test validation of a lowercase currency code (should be converted to uppercase)."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": "usd"}

        with patch(
            "app.api.v1.currency.currency_conversion_service.validate_currency_code",
            return_value=True,
        ):
            response = await validate_currency_code(request, mock_user)

        assert response == {"currency_code": "USD", "is_valid": True, "supported": True}

    @pytest.mark.asyncio
    async def test_validate_currency_code_missing(self):
        """Test validation with missing currency code."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {}

        with pytest.raises(HTTPException) as exc_info:
            await validate_currency_code(request, mock_user)

        assert exc_info.value.status_code == 500  # HTTPException is caught and re-raised as 500
        assert exc_info.value.detail == "Failed to validate currency"

    @pytest.mark.asyncio
    async def test_validate_currency_code_empty(self):
        """Test validation with empty currency code."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": ""}

        with pytest.raises(HTTPException) as exc_info:
            await validate_currency_code(request, mock_user)

        assert exc_info.value.status_code == 500  # HTTPException is caught and re-raised as 500
        assert exc_info.value.detail == "Failed to validate currency"

    @pytest.mark.asyncio
    async def test_validate_currency_code_service_exception(self):
        """Test validation when service raises an exception."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        request = {"currency_code": "USD"}

        with patch(
            "app.api.v1.currency.currency_conversion_service.validate_currency_code",
            side_effect=Exception("Service error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await validate_currency_code(request, mock_user)

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
                "app.api.v1.currency.currency_conversion_service.parse_currency_request",
                new=AsyncMock(return_value=mock_parsed_data),
            ),
            patch(
                "app.api.v1.currency.currency_conversion_service.validate_currency_code",
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
                "app.api.v1.currency.currency_conversion_service.parse_currency_request",
                new=AsyncMock(return_value=mock_parsed_data),
            ),
            patch(
                "app.api.v1.currency.currency_conversion_service.validate_currency_code",
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
                "app.api.v1.currency.currency_conversion_service.parse_currency_request",
                new=AsyncMock(return_value=mock_parsed_data),
            ),
            patch(
                "app.api.v1.currency.currency_conversion_service.validate_currency_code",
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
            "app.api.v1.currency.currency_conversion_service.parse_currency_request",
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
            "type": "currency_rate",
            "message": "50.00 USD = 42.50 EUR (Rate: 0.8500) (updated 2024-01-01T12:00:00Z)",
            "amount": 50.0,
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "converted_amount": 42.5,
            "last_updated": "2024-01-01T12:00:00Z",
        }

        with patch(
            "app.api.v1.currency.currency_conversion_service.handle_currency_request",
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
        with patch(
            "app.api.v1.currency.currency_conversion_service.validate_currency_code",
            return_value=True,
        ):
            response = await validate_currency_code(request_valid, mock_user)
            assert response["is_valid"] is True
            assert response["supported"] is True

        # Test with invalid currency
        request_invalid = {"currency_code": "INVALID"}
        with patch(
            "app.api.v1.currency.currency_conversion_service.validate_currency_code",
            return_value=False,
        ):
            response = await validate_currency_code(request_invalid, mock_user)
            assert response["is_valid"] is False
            assert response["supported"] is False

    @pytest.mark.asyncio
    async def test_get_supported_currencies_integration(self):
        """Test getting supported currencies with realistic service behavior."""
        mock_user = {"id": "test-user-123", "email": "test@example.com"}
        expected_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"]

        with patch(
            "app.api.v1.currency.currency_conversion_service.get_supported_currencies",
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
            "app.api.v1.currency.currency_conversion_service.handle_currency_request",
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
            "app.api.v1.currency.currency_conversion_service.handle_currency_request",
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

        with patch(
            "app.api.v1.currency.currency_conversion_service.validate_currency_code",
            return_value=False,
        ):
            response = await validate_currency_code(request, mock_user)

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
                "app.api.v1.currency.currency_conversion_service.parse_currency_request",
                new=AsyncMock(return_value=mock_parsed_data),
            ),
            patch(
                "app.api.v1.currency.currency_conversion_service.validate_currency_code",
                return_value=True,
            ),
        ):
            response = await parse_currency_message(request, mock_user)

        assert response["parsed_data"] == mock_parsed_data
        assert response["is_valid"] is True
