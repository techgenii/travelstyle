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

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from app.services.supabase_cache import SupabaseCacheService


@pytest.fixture
def mock_supabase_client():
    with patch("app.services.supabase_cache.create_client") as mock_create:
        mock_client = Mock()
        mock_create.return_value = mock_client
        yield mock_client


@pytest.fixture
def cache_service(mock_supabase_client):
    # Create service after mocking the client
    return SupabaseCacheService()


@pytest.mark.asyncio
async def test_get_weather_cache_success(cache_service, mock_supabase_client):
    # Mock the chain: table().select().eq().single().execute()
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_single = Mock()

    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.single.return_value = mock_single
    mock_single.execute.return_value = Mock(
        data={
            "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
            "data": {
                "temperature": 20,
                "description": "sunny",
            },  # Changed from "weather_data" to "data"
        }
    )

    result = await cache_service.get_weather_cache("Paris")
    assert result == {"temperature": 20, "description": "sunny"}


@pytest.mark.asyncio
async def test_get_weather_cache_expired(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_select = Mock()
    mock_eq1 = Mock()
    mock_eq2 = Mock()
    mock_single = Mock()

    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq1
    mock_eq1.eq.return_value = mock_eq2
    mock_eq2.single.return_value = mock_single
    mock_single.execute.return_value = Mock(
        data={
            "expires_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
            "data": {"temperature": 20},
        }
    )

    result = await cache_service.get_weather_cache("Paris")
    assert result is None


@pytest.mark.asyncio
async def test_get_weather_cache_not_found(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_select = Mock()
    mock_eq1 = Mock()
    mock_eq2 = Mock()
    mock_single = Mock()
    mock_single.execute.side_effect = Exception("Not found")

    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq1
    mock_eq1.eq.return_value = mock_eq2
    mock_eq2.single.return_value = mock_single

    result = await cache_service.get_weather_cache("Paris")
    assert result is None


@pytest.mark.asyncio
async def test_set_weather_cache_success(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_upsert = Mock()
    mock_execute = Mock()

    mock_supabase_client.table.return_value = mock_table
    mock_table.upsert.return_value = mock_upsert
    mock_upsert.execute.return_value = mock_execute

    result = await cache_service.set_weather_cache("Paris", {"temp": 20}, 2)
    assert result is True
    mock_table.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_set_weather_cache_error(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_upsert = Mock()
    mock_upsert.execute.side_effect = Exception("DB error")

    mock_supabase_client.table.return_value = mock_table
    mock_table.upsert.return_value = mock_upsert

    result = await cache_service.set_weather_cache("Paris", {"temp": 20})
    assert result is False


@pytest.mark.asyncio
async def test_get_cultural_cache_success(cache_service, mock_supabase_client):
    mock_execute = Mock()
    mock_execute.data = {
        "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        "data": {
            "customs": "formal",
            "dress_code": "business",
            "_context": "business",
        },
    }

    # Chain mocks for: .table().select().eq().eq().eq().single().execute()
    mock_table = mock_supabase_client.table.return_value
    mock_select = mock_table.select.return_value
    mock_eq1 = mock_select.eq.return_value
    mock_eq2 = mock_eq1.eq.return_value
    mock_eq3 = mock_eq2.eq.return_value
    mock_single = mock_eq3.single.return_value
    mock_single.execute.return_value = mock_execute

    result = await cache_service.get_cultural_cache("Tokyo", "business")
    assert result == {"customs": "formal", "dress_code": "business", "_context": "business"}


@pytest.mark.asyncio
async def test_get_cultural_cache_expired(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_select = Mock()
    mock_eq1 = Mock()
    mock_eq2 = Mock()
    mock_eq3 = Mock()
    mock_single = Mock()

    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq1
    mock_eq1.eq.return_value = mock_eq2
    mock_eq2.eq.return_value = mock_eq3
    mock_eq3.single.return_value = mock_single
    mock_single.execute.return_value = Mock(
        data={
            "expires_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
            "data": {"customs": "formal"},
        }
    )

    result = await cache_service.get_cultural_cache("Tokyo")
    assert result is None


@pytest.mark.asyncio
async def test_set_cultural_cache_success(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_upsert = Mock()

    mock_supabase_client.table.return_value = mock_table
    mock_table.upsert.return_value = mock_upsert
    mock_upsert.execute.return_value = Mock()

    result = await cache_service.set_cultural_cache("Tokyo", "leisure", {"customs": "casual"}, 48)
    assert result is True
    mock_table.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_get_currency_cache_success(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.execute.return_value = mock_execute
    mock_execute.data = [{"rates_data": {"USD": 1.0, "EUR": 0.85}}]

    result = await cache_service.get_currency_cache("USD")
    assert result == {"USD": 1.0, "EUR": 0.85}


@pytest.mark.asyncio
async def test_get_currency_cache_empty(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.execute.return_value = mock_execute
    mock_execute.data = []

    result = await cache_service.get_currency_cache("USD")
    assert result is None


@pytest.mark.asyncio
async def test_set_currency_cache_success(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_upsert = Mock()

    mock_supabase_client.table.return_value = mock_table
    mock_table.upsert.return_value = mock_upsert
    mock_upsert.execute.return_value = Mock()

    result = await cache_service.set_currency_cache("USD", {"EUR": 0.85}, 2)
    assert result is True
    mock_table.upsert.assert_called_once()


def test_is_expired_future(cache_service):
    future_time = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    assert not cache_service._is_expired(future_time)


def test_is_expired_past(cache_service):
    past_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    assert cache_service._is_expired(past_time)


def test_is_expired_invalid_format(cache_service):
    assert cache_service._is_expired("invalid-date")


def test_is_expired_with_z_suffix(cache_service):
    future_time = (datetime.now(UTC) + timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    assert not cache_service._is_expired(future_time)


@pytest.mark.asyncio
async def test_get_weather_cache_no_expires_at(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_select = Mock()
    mock_eq1 = Mock()
    mock_eq2 = Mock()
    mock_single = Mock()

    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq1
    mock_eq1.eq.return_value = mock_eq2
    mock_eq2.single.return_value = mock_single
    mock_single.execute.return_value = Mock(
        data={
            "data": {"temperature": 20}
            # No expires_at field
        }
    )

    result = await cache_service.get_weather_cache("Paris")
    assert result is None


@pytest.mark.asyncio
async def test_get_cultural_cache_error(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_select = Mock()
    mock_eq1 = Mock()
    mock_eq2 = Mock()
    mock_eq3 = Mock()
    mock_single = Mock()
    mock_single.execute.side_effect = Exception("DB error")

    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq1
    mock_eq1.eq.return_value = mock_eq2
    mock_eq2.eq.return_value = mock_eq3
    mock_eq3.single.return_value = mock_single

    result = await cache_service.get_cultural_cache("Tokyo")
    assert result is None


@pytest.mark.asyncio
async def test_set_cultural_cache_error(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_upsert = Mock()
    mock_upsert.execute.side_effect = Exception("DB error")

    mock_supabase_client.table.return_value = mock_table
    mock_table.upsert.return_value = mock_upsert

    result = await cache_service.set_cultural_cache("Tokyo", "leisure", {"customs": "casual"})
    assert result is False


@pytest.mark.asyncio
async def test_get_currency_cache_error(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_eq.execute.side_effect = Exception("DB error")

    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq

    result = await cache_service.get_currency_cache("USD")
    assert result is None


@pytest.mark.asyncio
async def test_set_currency_cache_error(cache_service, mock_supabase_client):
    mock_table = Mock()
    mock_upsert = Mock()
    mock_upsert.execute.side_effect = Exception("DB error")

    mock_supabase_client.table.return_value = mock_table
    mock_table.upsert.return_value = mock_upsert

    result = await cache_service.set_currency_cache("USD", {"EUR": 0.85})
    assert result is False
