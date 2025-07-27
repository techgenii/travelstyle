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


def test_is_currency_request_true():
    """Test identifying currency requests."""
    assert currency_conversion_service.is_currency_request("What's the exchange rate?") is True
    assert currency_conversion_service.is_currency_request("Convert USD to EUR") is True
    assert (
        currency_conversion_service.is_currency_request("currency between US and Germany") is True
    )
    assert currency_conversion_service.is_currency_request("convert money") is True


def test_is_currency_request_false():
    """Test identifying non-currency requests."""
    assert currency_conversion_service.is_currency_request("Hello, how are you?") is False
    assert currency_conversion_service.is_currency_request("Tell me about the weather") is False


def test_validate_currency_code():
    """Test currency code validation."""
    assert currency_conversion_service.validate_currency_code("USD") is True
    assert currency_conversion_service.validate_currency_code("EUR") is True
    assert currency_conversion_service.validate_currency_code("INVALID") is False
    assert currency_conversion_service.validate_currency_code("usd") is True


def test_format_currency_response():
    """Test formatting currency conversion response."""
    response = currency_conversion_service.format_currency_response("USD", "EUR", 100.0, 0.85, 85.0)
    expected = "100.00 USD = 85.00 EUR (Rate: 0.8500)"
    assert response == expected


def test_get_supported_currencies():
    """Test getting supported currencies."""
    currencies = currency_conversion_service.get_supported_currencies()

    assert "USD" in currencies
    assert "EUR" in currencies
    assert "GBP" in currencies
    # The service supports 163 currencies, not 30
    assert len(currencies) == 163


@pytest.mark.asyncio
async def test_parse_currency_request_invalid_json():
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

        result = await currency_conversion_service.parse_currency_request("convert $50 USD to EUR")

        assert result is None


@pytest.mark.asyncio
async def test_handle_currency_request_missing_currencies():
    """Test currency request with missing currency information."""
    with patch(
        "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
        new_callable=AsyncMock,
    ) as mock_openai:
        # Create a proper mock response with missing currencies
        mock_choice = MagicMock()
        mock_choice.message.content = '{"first_country": "", "second_country": "", "amount": 100.0}'

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai.return_value = mock_response

        result = await currency_conversion_service.handle_currency_request("convert something")

        assert result is None


@pytest.mark.asyncio
async def test_parse_currency_request_valid_json():
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
async def test_parse_currency_request_json_decode_error():
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
async def test_parse_currency_request_openai_exception():
    """Test parsing currency request when OpenAI raises an exception."""
    with patch(
        "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
        new_callable=AsyncMock,
    ) as mock_create:
        # Make OpenAI raise an exception
        mock_create.side_effect = Exception("OpenAI API error")

        result = await currency_conversion_service.parse_currency_request("convert $100 USD to EUR")

        assert result is None


@pytest.mark.asyncio
async def test_handle_currency_request_unsupported_from_currency():
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

        result = await currency_conversion_service.handle_currency_request("convert 100 XXX to EUR")

        assert result is None


@pytest.mark.asyncio
async def test_handle_currency_request_unsupported_to_currency():
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

        result = await currency_conversion_service.handle_currency_request("convert 100 USD to YYY")

        assert result is None


@pytest.mark.asyncio
async def test_handle_currency_request_no_exchange_rate():
    """Test currency request when exchange rate service returns None."""
    with (
        patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_openai,
        patch(
            "app.services.currency_conversion_service.currency_service.get_pair_exchange_rate",
            new_callable=AsyncMock,
        ) as mock_rate,
    ):
        # Create a proper mock response with valid currencies
        mock_choice = MagicMock()
        mock_choice.message.content = (
            '{"first_country": "USD", "second_country": "EUR", "amount": 100.0}'
        )

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai.return_value = mock_response

        # Make exchange rate service return None
        mock_rate.return_value = None

        result = await currency_conversion_service.handle_currency_request("convert 100 USD to EUR")

        assert result is None


@pytest.mark.asyncio
async def test_handle_currency_request_with_amount():
    """Test currency request with valid amount and exchange rate."""
    with (
        patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_openai,
        patch(
            "app.services.currency_conversion_service.currency_service.get_pair_exchange_rate",
            new_callable=AsyncMock,
        ) as mock_rate,
    ):
        # Create a proper mock response with valid currencies and amount
        mock_choice = MagicMock()
        mock_choice.message.content = (
            '{"first_country": "USD", "second_country": "EUR", "amount": 100.0}'
        )

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai.return_value = mock_response

        # Mock exchange rate service response
        mock_rate.return_value = {
            "rate": 0.85,
            "last_updated_utc": "2024-01-01T12:00:00Z",
            "last_updated_unix": 1704110400,
        }

        result = await currency_conversion_service.handle_currency_request("convert 100 USD to EUR")

        assert result["original"]["amount"] == 100.0
        assert result["original"]["currency"] == "USD"
        assert result["converted"]["amount"] == 85.0
        assert result["converted"]["currency"] == "EUR"
        assert result["rate"] == 0.85
        assert result["last_updated_utc"] == "2024-01-01T12:00:00Z"


@pytest.mark.asyncio
async def test_handle_currency_request_without_amount():
    """Test currency request without amount (just exchange rate)."""
    with (
        patch(
            "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
            new_callable=AsyncMock,
        ) as mock_openai,
        patch(
            "app.services.currency_conversion_service.currency_service.get_pair_exchange_rate",
            new_callable=AsyncMock,
        ) as mock_rate,
    ):
        # Create a proper mock response with valid currencies but no amount
        mock_choice = MagicMock()
        mock_choice.message.content = (
            '{"first_country": "USD", "second_country": "EUR", "amount": 0.0}'
        )

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai.return_value = mock_response

        # Mock exchange rate service response
        mock_rate.return_value = {
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
async def test_handle_currency_request_exception():
    """Test currency request when an exception occurs."""
    with patch(
        "app.services.currency_conversion_service.openai_service.client.chat.completions.create",
        new_callable=AsyncMock,
    ) as mock_openai:
        # Make OpenAI raise an exception
        mock_openai.side_effect = Exception("Service error")

        result = await currency_conversion_service.handle_currency_request("convert 100 USD to EUR")

        assert result is None


@pytest.mark.asyncio
async def test_parse_currency_request_with_whitespace():
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

        result = await currency_conversion_service.parse_currency_request("convert $100 USD to EUR")

        assert result["first_country"] == "USD"  # Should be stripped and uppercased
        assert result["second_country"] == "EUR"  # Should be stripped and uppercased
        assert result["amount"] == 100.0


@pytest.mark.asyncio
async def test_parse_currency_request_with_missing_amount():
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
async def test_parse_currency_request_with_formatted_json():
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

        result = await currency_conversion_service.parse_currency_request("convert $100 USD to EUR")

        assert result["first_country"] == "USD"
        assert result["second_country"] == "EUR"
        assert result["amount"] == 100.0


@pytest.mark.asyncio
async def test_parse_currency_request_with_extra_text():
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

        result = await currency_conversion_service.parse_currency_request("convert $100 USD to EUR")

        assert result["first_country"] == "USD"
        assert result["second_country"] == "EUR"
        assert result["amount"] == 100.0


@pytest.mark.asyncio
async def test_parse_currency_request_with_amount_zero():
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
async def test_parse_currency_request_with_negative_amount():
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

        result = await currency_conversion_service.parse_currency_request("convert -$50 USD to EUR")

        assert result["first_country"] == "USD"
        assert result["second_country"] == "EUR"
        assert result["amount"] == -50.0
