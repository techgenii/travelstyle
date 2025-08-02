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
Tests for currency API endpoints.
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from app.services.currency_conversion_service import CurrencyConversionService
from app.services.currency_service import CurrencyService
from fastapi import status


class MockAsyncResponse:
    def __init__(self, data):
        self.data = data
        self.status_code = 200

    def json(self):
        return self.data

    def raise_for_status(self):
        # Make this synchronous to avoid coroutine warnings
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("HTTP error", request=None, response=self)
        return self


class TestCurrencyEndpoints:
    """Test currency API endpoints."""

    def test_exchange_rates_success(self, authenticated_client):
        """Test successful exchange rates retrieval."""
        with patch(
            "app.services.currency_service.currency_service.get_exchange_rates"
        ) as mock_get_rates:
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
        with patch(
            "app.services.currency_service.currency_service.get_exchange_rates"
        ) as mock_get_rates:
            mock_get_rates.return_value = None
            response = authenticated_client.get("/api/v1/currency/rates/INVALID")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Exchange rates not available" in response.json()["detail"]

    def test_exchange_rates_service_exception(self, authenticated_client):
        """Test exchange rates when service raises exception (500)."""
        with patch(
            "app.services.currency_service.currency_service.get_exchange_rates"
        ) as mock_get_rates:
            mock_get_rates.side_effect = Exception("Service error")
            response = authenticated_client.get("/api/v1/currency/rates/USD")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve exchange rates" in response.json()["detail"]

    def test_currency_conversion_amount_success(self, authenticated_client):
        """Test successful currency conversion."""
        with patch(
            "app.services.currency_service.currency_service.convert_currency"
        ) as mock_convert:
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
        with patch(
            "app.services.currency_service.currency_service.convert_currency"
        ) as mock_convert:
            mock_convert.return_value = None
            response = authenticated_client.post(
                "/api/v1/currency/convert-amount",
                json={"amount": 100.0, "from_currency": "INVALID", "to_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Currency conversion failed" in response.json()["detail"]

    def test_currency_conversion_amount_service_exception(self, authenticated_client):
        """Test currency conversion when service raises exception (500)."""
        with patch(
            "app.services.currency_service.currency_service.convert_currency"
        ) as mock_convert:
            mock_convert.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/currency/convert-amount",
                json={"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to convert currency" in response.json()["detail"]

    def test_pair_exchange_rate_success(self, authenticated_client):
        """Test successful pair exchange rate retrieval."""
        with patch(
            "app.services.currency_service.currency_service.get_pair_exchange_rate"
        ) as mock_get_pair:
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
        with patch(
            "app.services.currency_service.currency_service.get_pair_exchange_rate"
        ) as mock_get_pair:
            mock_get_pair.return_value = None
            response = authenticated_client.post(
                "/api/v1/currency/pair",
                json={"base_currency": "USD", "target_currency": "INVALID"},
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Exchange rate not available" in response.json()["detail"]

    def test_pair_exchange_rate_service_exception(self, authenticated_client):
        """Test pair exchange rate when service raises exception (500)."""
        with patch(
            "app.services.currency_service.currency_service.get_pair_exchange_rate"
        ) as mock_get_pair:
            mock_get_pair.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/currency/pair",
                json={"base_currency": "USD", "target_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve pair exchange rate" in response.json()["detail"]

    def test_currency_convert_chat_success(self, authenticated_client):
        """Test successful currency conversion via chat endpoint."""
        with patch(
            "app.services.currency_conversion_service.currency_conversion_service.handle_currency_request"
        ) as mock_handle:
            mock_handle.return_value = {
                "original": {"amount": 100.0, "currency": "USD"},
                "converted": {"amount": 85.0, "currency": "EUR"},
                "rate": 0.85,
                "last_updated_unix": 1640995200,
                "last_updated_utc": "2022-01-01T00:00:00Z",
            }
            response = authenticated_client.post(
                "/api/v1/currency/convert",
                json={"message": "Convert 100 USD to EUR"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
            assert "100.00 USD = 85.00 EUR" in data["message"]
            assert "Rate: 0.8500" in data["message"]

    def test_currency_convert_chat_failure(self, authenticated_client):
        """Test currency conversion via chat endpoint when it fails."""
        with patch(
            "app.services.currency_conversion_service.currency_conversion_service.handle_currency_request"
        ) as mock_handle:
            mock_handle.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/currency/convert",
                json={"message": "Convert 100 USD to INVALID"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to process currency request" in response.json()["detail"]

    def test_get_supported_currencies(self, authenticated_client):
        """Test getting supported currencies."""
        response = authenticated_client.get("/api/v1/currency/supported")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "currencies" in data
        assert isinstance(data["currencies"], list)
        assert len(data["currencies"]) > 0

    def test_validate_currency_code_valid(self, authenticated_client):
        """Test currency code validation with valid code."""
        response = authenticated_client.post(
            "/api/v1/currency/validate",
            json={"currency_code": "USD"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["currency_code"] == "USD"
        assert data["is_valid"] is True
        assert data["supported"] is True

    def test_validate_currency_code_invalid(self, authenticated_client):
        """Test currency code validation with invalid code."""
        response = authenticated_client.post(
            "/api/v1/currency/validate",
            json={"currency_code": "INVALID"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["currency_code"] == "INVALID"
        assert data["is_valid"] is False
        assert data["supported"] is False

    def test_parse_currency_message(self, authenticated_client):
        """Test parsing currency message."""
        with patch(
            "app.services.currency_conversion_service.currency_conversion_service.parse_currency_request"
        ) as mock_parse:
            mock_parse.return_value = {
                "first_country": "USD",
                "second_country": "EUR",
                "amount": 100.0,
            }
            response = authenticated_client.post(
                "/api/v1/currency/parse",
                json={"message": "Convert 100 USD to EUR"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "parsed_data" in data
            assert "is_valid" in data

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

        # Test currency convert chat endpoint
        response = client.post(
            "/api/v1/currency/convert",
            json={"message": "Convert 100 USD to EUR"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test supported currencies endpoint
        response = client.get("/api/v1/currency/supported")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test currency validation endpoint
        response = client.post(
            "/api/v1/currency/validate",
            json={"currency_code": "USD"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test currency parse endpoint
        response = client.post(
            "/api/v1/currency/parse",
            json={"message": "Convert 100 USD to EUR"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_exchange_rates_success():
    """Test successful exchange rates retrieval from service."""
    service = CurrencyService()
    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(
                return_value=MockAsyncResponse(
                    {
                        "base_code": "USD",
                        "conversion_rates": {"EUR": 0.85, "GBP": 0.73},
                        "time_last_update_unix": 1234567890,
                        "time_last_update_utc": "2024-01-01T12:00:00Z",
                    }
                )
            ),
        ),
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.set_currency_cache",
            new=AsyncMock(),
        ),
    ):
        rates = await service.get_exchange_rates("USD")
        assert rates is not None
        assert rates["base_code"] == "USD"
        assert "EUR" in rates["conversion_rates"]


@pytest.mark.asyncio
async def test_get_exchange_rates_cache():
    """Test exchange rates retrieval from cache."""
    service = CurrencyService()
    with patch(
        "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_currency_cache",
        new=AsyncMock(return_value={"cached": True}),
    ):
        rates = await service.get_exchange_rates("USD")
        assert rates is not None
        assert rates["cached"] is True


@pytest.mark.asyncio
async def test_get_exchange_rates_error():
    """Test exchange rates retrieval error handling."""
    service = CurrencyService()
    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(side_effect=httpx.RequestError("API error", request=None)),
        ),
    ):
        result = await service.get_exchange_rates("USD")
        assert result is None


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_success():
    """Test successful pair exchange rate retrieval."""
    service = CurrencyService()
    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_currency_cache",
            return_value=None,
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(
                return_value=MockAsyncResponse(
                    {
                        "base_code": "USD",
                        "conversion_rates": {"EUR": 0.85},
                        "time_last_update_unix": 1234567890,
                        "time_last_update_utc": "2024-01-01T12:00:00Z",
                    }
                )
            ),
        ),
    ):
        result = await service.get_pair_exchange_rate("USD", "EUR")
        assert result is not None
        assert result["base_code"] == "USD"
        assert result["target_code"] == "EUR"
        assert result["rate"] == 0.85


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_error():
    """Test pair exchange rate error handling."""
    service = CurrencyService()
    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_currency_cache",
            return_value=None,
        ),
        patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=Exception("API error"))),
    ):
        result = await service.get_pair_exchange_rate("USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_convert_currency_success():
    """Test successful currency conversion."""
    service = CurrencyService()
    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_currency_cache",
            return_value=None,
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(
                return_value=MockAsyncResponse(
                    {
                        "base_code": "USD",
                        "conversion_rates": {"EUR": 0.85},
                        "time_last_update_unix": 1234567890,
                        "time_last_update_utc": "2024-01-01T12:00:00Z",
                    }
                )
            ),
        ),
    ):
        result = await service.convert_currency(100.0, "USD", "EUR")
        assert result is not None
        assert result["original"]["amount"] == 100.0
        assert result["original"]["currency"] == "USD"
        assert result["converted"]["amount"] == 85.0
        assert result["converted"]["currency"] == "EUR"
        assert result["rate"] == 0.85


@pytest.mark.asyncio
async def test_convert_currency_error():
    """Test currency conversion error handling."""
    service = CurrencyService()
    with (
        patch(
            "app.services.supabase.supabase_cache_v2.enhanced_supabase_cache.get_currency_cache",
            return_value=None,
        ),
        patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=Exception("API error"))),
    ):
        result = await service.convert_currency(100.0, "USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_currency_conversion_service_is_currency_request():
    """Test currency request detection."""
    service = CurrencyConversionService()

    # Test currency conversion request
    assert service.is_currency_request("Convert 100 USD to EUR") is True
    assert service.is_currency_request("What's the exchange rate for USD to EUR?") is True

    # Test non-currency request
    assert service.is_currency_request("What should I pack for Paris?") is False
    assert service.is_currency_request("Tell me about the weather in Tokyo") is False


@pytest.mark.asyncio
async def test_currency_conversion_service_validate_currency_code():
    """Test currency code validation."""
    service = CurrencyConversionService()

    # Test valid currency codes
    assert service.validate_currency_code("USD") is True
    assert service.validate_currency_code("EUR") is True
    assert service.validate_currency_code("GBP") is True

    # Test invalid currency codes
    assert service.validate_currency_code("INVALID") is False
    assert service.validate_currency_code("XYZ") is False
    assert service.validate_currency_code("") is False


@pytest.mark.asyncio
async def test_currency_conversion_service_get_supported_currencies():
    """Test getting supported currencies."""
    service = CurrencyConversionService()
    currencies = service.get_supported_currencies()

    assert isinstance(currencies, list)
    assert len(currencies) > 0
    assert "USD" in currencies
    assert "EUR" in currencies
    assert "GBP" in currencies
