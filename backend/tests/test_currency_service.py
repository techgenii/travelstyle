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

"""Tests for currency service."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest
from app.services.currency.formatter import CurrencyFormatter
from app.services.currency_service import CurrencyService


class MockAsyncResponse:
    """Mock async response for testing."""

    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.content = str(data).encode()
        self.raise_for_status = MagicMock()

    def json(self):
        return self._data


@pytest.fixture
def currency_service():
    """Create a currency service instance for testing."""
    return CurrencyService()


@pytest.fixture
def currency_formatter():
    """Create a currency formatter instance for testing."""
    return CurrencyFormatter()


class TestCurrencyFormatter:
    """Test CurrencyFormatter class."""

    def test_formatter_initialization(self, currency_formatter):
        """Test CurrencyFormatter initialization."""
        assert currency_formatter is not None

    def test_format_currency_response_success(self, currency_formatter):
        """Test successful currency response formatting."""
        result = currency_formatter.format_currency_response(
            from_currency="USD", to_currency="EUR", amount=100.0, rate=0.85, converted_amount=85.0
        )

        assert "💱 **Currency Conversion**" in result
        assert "**100.00 USD** = **85.00 EUR**" in result
        assert "📊 **Exchange Rate:** 1 USD = 0.8500 EUR" in result
        assert "💡 *Rates are updated in real-time" in result

    def test_format_currency_response_with_large_numbers(self, currency_formatter):
        """Test currency response formatting with large numbers."""
        result = currency_formatter.format_currency_response(
            from_currency="USD",
            to_currency="JPY",
            amount=1000000.0,
            rate=150.0,
            converted_amount=150000000.0,
        )

        assert "**1,000,000.00 USD** = **150,000,000.00 JPY**" in result
        assert "📊 **Exchange Rate:** 1 USD = 150.0000 JPY" in result

    def test_format_currency_response_with_small_numbers(self, currency_formatter):
        """Test currency response formatting with small numbers."""
        result = currency_formatter.format_currency_response(
            from_currency="EUR", to_currency="USD", amount=0.01, rate=1.1, converted_amount=0.011
        )

        assert "**0.01 EUR** = **0.01 USD**" in result
        assert "📊 **Exchange Rate:** 1 EUR = 1.1000 USD" in result

    def test_format_currency_response_exception(self, currency_formatter):
        """Test currency response formatting with exception."""

        # Create a custom object that raises an exception when converted to string
        class BadString:
            def __str__(self):
                raise Exception("Test error")

        result = currency_formatter.format_currency_response(
            from_currency=BadString(),
            to_currency="EUR",
            amount=100.0,
            rate=0.85,
            converted_amount=85.0,
        )
        # Should return error message
        assert "Sorry, I encountered an error" in result

    def test_format_exchange_rate_response_success(self, currency_formatter):
        """Test successful exchange rate response formatting."""
        result = currency_formatter.format_exchange_rate_response(
            from_currency="USD", to_currency="EUR", rate=0.85
        )

        assert "📊 **Exchange Rate**" in result
        assert "**1 USD** = **0.8500 EUR**" in result
        assert "💡 *Rates are updated in real-time" in result

    def test_format_exchange_rate_response_with_last_updated(self, currency_formatter):
        """Test exchange rate response formatting with last updated timestamp."""
        result = currency_formatter.format_exchange_rate_response(
            from_currency="USD", to_currency="EUR", rate=0.85, last_updated="2024-01-15 10:30:00"
        )

        assert "📊 **Exchange Rate**" in result
        assert "**1 USD** = **0.8500 EUR**" in result
        assert "🕒 *Last updated: 2024-01-15 10:30:00*" in result
        assert "💡 *Rates are updated in real-time" in result

    def test_format_exchange_rate_response_exception(self, currency_formatter):
        """Test exchange rate response formatting with exception."""

        # Create a custom object that raises an exception when converted to string
        class BadString:
            def __str__(self):
                raise Exception("Test error")

        result = currency_formatter.format_exchange_rate_response(
            from_currency=BadString(), to_currency="EUR", rate=0.85
        )
        # Should return error message
        assert "Sorry, I encountered an error" in result

    def test_format_currency_help_response(self, currency_formatter):
        """Test currency help response formatting."""
        result = currency_formatter.format_currency_help_response()

        assert "💱 **Currency Converter Help**" in result
        assert "I can help you with currency conversions and exchange rates!" in result
        assert "**Examples:**" in result
        assert "• Convert 100 USD to EUR" in result
        assert "• 50 EUR to USD" in result
        assert "• Exchange rate USD EUR" in result
        assert "• 1000 JPY to GBP" in result
        assert "**Supported Currencies:**" in result
        assert "I support all major world currencies" in result
        assert "**Tips:**" in result
        assert "• Use 3-letter currency codes" in result
        assert "• Include the amount you want to convert" in result
        assert "• Ask for exchange rates without amounts" in result
        assert "💡 *Rates are updated in real-time from reliable sources.*" in result

    def test_format_error_response_default(self, currency_formatter):
        """Test error response formatting with default message."""
        result = currency_formatter.format_error_response()

        assert "❌ **Currency Conversion Error**" in result
        assert "Sorry, I couldn't process your currency request: Unknown error" in result
        assert "Please try again with a different format" in result

    def test_format_error_response_custom_message(self, currency_formatter):
        """Test error response formatting with custom message."""
        result = currency_formatter.format_error_response("Invalid currency code")

        assert "❌ **Currency Conversion Error**" in result
        assert "Sorry, I couldn't process your currency request: Invalid currency code" in result
        assert "Please try again with a different format" in result

    def test_format_error_response_with_special_characters(self, currency_formatter):
        """Test error response formatting with special characters."""
        result = currency_formatter.format_error_response("Error: 'USD' is not a valid currency")

        assert "❌ **Currency Conversion Error**" in result
        assert (
            "Sorry, I couldn't process your currency request: Error: 'USD' is not a valid currency"
            in result
        )


@pytest.mark.asyncio
async def test_get_exchange_rates_json_parse_error(currency_service):
    """Test get_exchange_rates when JSON parsing fails."""
    with (
        patch(
            "app.services.supabase.supabase_cache.supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(return_value=MockAsyncResponse("invalid json")),
        ),
    ):
        result = await currency_service.get_exchange_rates("USD")
        assert result is None


@pytest.mark.asyncio
async def test_get_exchange_rates_json_parse_exception(currency_service):
    """Test get_exchange_rates when JSON parsing raises exception."""
    mock_response = Mock()
    mock_response.content = b"invalid json content"
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.raise_for_status = MagicMock()

    with (
        patch(
            "app.services.supabase.supabase_cache.supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(return_value=mock_response),
        ),
    ):
        result = await currency_service.get_exchange_rates("USD")
        assert result is None


@pytest.mark.asyncio
async def test_get_exchange_rates_non_dict_response(currency_service):
    """Test get_exchange_rates when response is not a dict."""
    with (
        patch(
            "app.services.supabase.supabase_cache.supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(return_value=MockAsyncResponse("not a dict")),
        ),
    ):
        result = await currency_service.get_exchange_rates("USD")
        assert result is None


@pytest.mark.asyncio
async def test_get_exchange_rates_http_status_error(currency_service):
    """Test get_exchange_rates when HTTP status error occurs."""
    mock_request = Mock()
    mock_response = Mock()
    with (
        patch(
            "app.services.supabase.supabase_cache.supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "404", request=mock_request, response=mock_response
                )
            ),
        ),
    ):
        result = await currency_service.get_exchange_rates("USD")
        assert result is None


@pytest.mark.asyncio
async def test_get_exchange_rates_timeout_error(currency_service):
    """Test get_exchange_rates when timeout error occurs."""
    with (
        patch(
            "app.services.supabase.supabase_cache.supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(side_effect=httpx.TimeoutException("timeout")),
        ),
    ):
        result = await currency_service.get_exchange_rates("USD")
        assert result is None


@pytest.mark.asyncio
async def test_get_exchange_rates_value_error(currency_service):
    """Test get_exchange_rates when ValueError occurs."""
    with (
        patch(
            "app.services.supabase.supabase_cache.supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(side_effect=ValueError("invalid value")),
        ),
    ):
        result = await currency_service.get_exchange_rates("USD")
        assert result is None


@pytest.mark.asyncio
async def test_get_exchange_rates_currency_normalization(currency_service):
    """Test get_exchange_rates with currency normalization (whitespace, case)."""
    with (
        patch(
            "app.services.supabase.supabase_cache.supabase_cache.get_currency_cache",
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
        patch("app.services.supabase.supabase_cache.supabase_cache.set_currency_cache", new=AsyncMock()),
    ):
        # Test with lowercase and whitespace
        rates = await currency_service.get_exchange_rates(" usd ")
        assert rates is not None
        assert rates["base_code"] == "USD"


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_json_parse_error(currency_service):
    """Test get_pair_exchange_rate when JSON parsing fails."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=MockAsyncResponse("invalid json")),
    ):
        result = await currency_service.get_pair_exchange_rate("USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_json_parse_exception(currency_service):
    """Test get_pair_exchange_rate when JSON parsing raises exception."""
    mock_response = Mock()
    mock_response.content = b"invalid json content"
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.raise_for_status = MagicMock()

    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=mock_response),
    ):
        result = await currency_service.get_pair_exchange_rate("USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_non_success_result(currency_service):
    """Test get_pair_exchange_rate when API returns non-success result."""
    from app.services.currency.exceptions import CurrencyValidationError

    with pytest.raises(CurrencyValidationError, match="Unsupported currency code: INVALID"):
        await currency_service.get_pair_exchange_rate("USD", "INVALID")


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_non_dict_response(currency_service):
    """Test get_pair_exchange_rate when response is not a dict."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=MockAsyncResponse("not a dict")),
    ):
        result = await currency_service.get_pair_exchange_rate("USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_currency_normalization(currency_service):
    """Test get_pair_exchange_rate with currency normalization."""
    with patch(
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
    ):
        # Test with lowercase and whitespace
        result = await currency_service.get_pair_exchange_rate(" usd ", " eur ")
        assert result is not None
        assert result["base_code"] == "USD"
        assert result["target_code"] == "EUR"


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_http_error(currency_service):
    """Test get_pair_exchange_rate when HTTP error occurs."""
    mock_request = Mock()
    mock_response = Mock()
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=mock_request, response=mock_response)
        ),
    ):
        result = await currency_service.get_pair_exchange_rate("USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_request_error(currency_service):
    """Test get_pair_exchange_rate when request error occurs."""
    mock_request = Mock()
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(side_effect=httpx.RequestError("connection failed", request=mock_request)),
    ):
        result = await currency_service.get_pair_exchange_rate("USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_generic_exception(currency_service):
    """Test get_pair_exchange_rate when generic exception occurs."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(side_effect=Exception("unknown error")),
    ):
        result = await currency_service.get_pair_exchange_rate("USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_convert_currency_with_get_pair_exchange_rate_failure(currency_service):
    """Test convert_currency when API returns error."""
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(side_effect=httpx.HTTPStatusError("404", request=None, response=None)),
    ):
        result = await currency_service.convert_currency(100, "USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_convert_currency_amount_rounding(currency_service):
    """Test convert_currency with proper amount rounding."""
    mock_response = MockAsyncResponse(
        {
            "base_code": "USD",
            "conversion_rates": {"EUR": 0.123456789},
            "time_last_update_unix": 1234567890,
            "time_last_update_utc": "2024-01-01T12:00:00Z",
        }
    )

    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=mock_response),
    ):
        result = await currency_service.convert_currency(100, "USD", "EUR")
        assert result is not None
        assert result["converted"]["amount"] == 12.3456789  # Calculated result
        assert result["rate"] == 0.123456789


@pytest.mark.asyncio
async def test_convert_currency_zero_amount(currency_service):
    """Test convert_currency with zero amount (should be rejected by validation)."""
    from app.services.currency.exceptions import CurrencyValidationError

    with pytest.raises(CurrencyValidationError, match="Invalid amount: 0"):
        await currency_service.convert_currency(0, "USD", "EUR")


@pytest.mark.asyncio
async def test_convert_currency_negative_amount(currency_service):
    """Test convert_currency with negative amount (should be rejected by validation)."""
    from app.services.currency.exceptions import CurrencyValidationError

    with pytest.raises(CurrencyValidationError, match="Invalid amount: -100"):
        await currency_service.convert_currency(-100, "USD", "EUR")


def test_currency_service_initialization():
    """Test CurrencyService initialization."""
    service = CurrencyService()
    assert service.api is not None
    assert service.parser is not None
    assert service.formatter is not None
