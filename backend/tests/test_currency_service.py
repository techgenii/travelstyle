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


@pytest.mark.asyncio
async def test_get_exchange_rates_json_parse_error(currency_service):
    """Test get_exchange_rates when JSON parsing fails."""
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_currency_cache",
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
            "app.services.supabase_cache.supabase_cache.get_currency_cache",
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
            "app.services.supabase_cache.supabase_cache.get_currency_cache",
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
            "app.services.supabase_cache.supabase_cache.get_currency_cache",
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
            "app.services.supabase_cache.supabase_cache.get_currency_cache",
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
            "app.services.supabase_cache.supabase_cache.get_currency_cache",
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
            "app.services.supabase_cache.supabase_cache.get_currency_cache",
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
        patch("app.services.supabase_cache.supabase_cache.set_currency_cache", new=AsyncMock()),
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
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(
            return_value=MockAsyncResponse(
                {
                    "result": "error",
                    "error-type": "invalid_currency",
                }
            )
        ),
    ):
        result = await currency_service.get_pair_exchange_rate("USD", "INVALID")
        assert result is None


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
                    "result": "success",
                    "base_code": "USD",
                    "target_code": "EUR",
                    "conversion_rate": 0.85,
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
            "result": "success",
            "documentation": "https://www.exchangerate-api.com/docs",
            "terms_of_use": "https://www.exchangerate-api.com/terms",
            "time_last_update_unix": 1234567890,
            "time_last_update_utc": "2024-01-01T12:00:00Z",
            "time_next_update_unix": 1234567890,
            "time_next_update_utc": "2024-01-01T12:00:00Z",
            "base_code": "USD",
            "target_code": "EUR",
            "conversion_rate": 0.123456789,  # Long decimal
            "conversion_result": 12.3456789,  # API calculated result
        }
    )

    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=mock_response),
    ):
        result = await currency_service.convert_currency(100, "USD", "EUR")
        assert result is not None
        assert result["converted"]["amount"] == 12.3456789  # API calculated result
        assert result["rate"] == 0.123456789


@pytest.mark.asyncio
async def test_convert_currency_zero_amount(currency_service):
    """Test convert_currency with zero amount."""
    mock_response = MockAsyncResponse(
        {
            "result": "success",
            "documentation": "https://www.exchangerate-api.com/docs",
            "terms_of_use": "https://www.exchangerate-api.com/terms",
            "time_last_update_unix": 1234567890,
            "time_last_update_utc": "2024-01-01T12:00:00Z",
            "time_next_update_unix": 1234567890,
            "time_next_update_utc": "2024-01-01T12:00:00Z",
            "base_code": "USD",
            "target_code": "EUR",
            "conversion_rate": 0.85,
            "conversion_result": 0.0,
        }
    )

    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=mock_response),
    ):
        result = await currency_service.convert_currency(0, "USD", "EUR")
        assert result is not None
        assert result["original"]["amount"] == 0
        assert result["converted"]["amount"] == 0.0


@pytest.mark.asyncio
async def test_convert_currency_negative_amount(currency_service):
    """Test convert_currency with negative amount."""
    mock_response = MockAsyncResponse(
        {
            "result": "success",
            "documentation": "https://www.exchangerate-api.com/docs",
            "terms_of_use": "https://www.exchangerate-api.com/terms",
            "time_last_update_unix": 1234567890,
            "time_last_update_utc": "2024-01-01T12:00:00Z",
            "time_next_update_unix": 1234567890,
            "time_next_update_utc": "2024-01-01T12:00:00Z",
            "base_code": "USD",
            "target_code": "EUR",
            "conversion_rate": 0.85,
            "conversion_result": -85.0,
        }
    )

    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(return_value=mock_response),
    ):
        result = await currency_service.convert_currency(-100, "USD", "EUR")
        assert result is not None
        assert result["original"]["amount"] == -100
        assert result["converted"]["amount"] == -85.0


def test_currency_service_initialization():
    """Test CurrencyService initialization."""
    service = CurrencyService()
    assert service.base_url is not None
    assert service.api_key is not None
    assert service.timeout == 10.0
