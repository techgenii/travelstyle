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

"""Tests for SupabaseClientManager and helpers in supabase_client.py."""

import time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from app.services.supabase.supabase_client import (
    SupabaseClientManager,
    SupabaseConnectionError,
    get_supabase_client,
    test_supabase_connection,
)


@pytest.fixture(autouse=True)
def reset_manager_state():
    """Reset singleton state before/after each test."""
    SupabaseClientManager.reset_client()
    yield
    SupabaseClientManager.reset_client()


@pytest.fixture
def mock_settings():
    """Patch settings for tests with valid values."""
    with patch("app.services.supabase.supabase_client.settings") as mock_settings:
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_KEY = "test-key"
        yield mock_settings


def _make_table_chain(success: bool = True, raise_msg: str | None = None):
    client = MagicMock()
    table = MagicMock()
    select = MagicMock()
    limit = MagicMock()

    client.table.return_value = table
    table.select.return_value = select
    select.limit.return_value = limit

    if success:
        limit.execute.return_value = SimpleNamespace(data=[])
    else:
        exc = Exception(raise_msg or "Some error")
        limit.execute.side_effect = exc

    return client


class TestInitialization:
    def test_get_client_initializes_once(self, mock_settings):
        with patch("app.services.supabase.supabase_client.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client

            c1 = SupabaseClientManager.get_client()
            c2 = SupabaseClientManager.get_client()

            assert c1 is mock_client
            assert c2 is mock_client
            assert SupabaseClientManager.is_initialized() is True
            mock_create.assert_called_once_with(
                mock_settings.SUPABASE_URL, mock_settings.SUPABASE_KEY
            )

    def test_create_client_missing_settings_raises(self):
        with patch("app.services.supabase.supabase_client.settings") as mock_settings:
            mock_settings.SUPABASE_URL = ""
            mock_settings.SUPABASE_KEY = ""
            with pytest.raises(SupabaseConnectionError):
                SupabaseClientManager._create_client()

    def test_create_client_wraps_exception(self, mock_settings):
        with patch(
            "app.services.supabase.supabase_client.create_client", side_effect=Exception("boom")
        ):
            with pytest.raises(SupabaseConnectionError):
                SupabaseClientManager._create_client()


class TestHealthCheck:
    def test_check_connection_health_success_updates_timestamp(self, mock_settings):
        with patch("app.services.supabase.supabase_client.create_client") as mock_create:
            mock_client = _make_table_chain(success=True)
            mock_create.return_value = mock_client
            SupabaseClientManager.get_client()

        # Force a health check to run by manipulating time
        with patch("time.time", return_value=time.time() + 400):
            last_before = SupabaseClientManager._last_health_check
            SupabaseClientManager._check_connection_health()
            assert SupabaseClientManager._last_health_check >= last_before

    def test_check_connection_health_missing_table_does_not_reset(self, mock_settings):
        with patch("app.services.supabase.supabase_client.create_client") as mock_create:
            mock_client = _make_table_chain(
                success=False, raise_msg='relation "users" does not exist'
            )
            mock_create.return_value = mock_client
            SupabaseClientManager.get_client()

        with patch("time.time", return_value=time.time() + 400):
            with patch.object(SupabaseClientManager, "reset_client") as mock_reset:
                SupabaseClientManager._check_connection_health()
                mock_reset.assert_not_called()

    def test_check_connection_health_other_error_resets(self, mock_settings):
        with patch("app.services.supabase.supabase_client.create_client") as mock_create:
            mock_client = _make_table_chain(success=False, raise_msg="network unreachable")
            mock_create.return_value = mock_client
            SupabaseClientManager.get_client()

        with patch("time.time", return_value=time.time() + 400):
            with patch.object(SupabaseClientManager, "reset_client") as mock_reset:
                SupabaseClientManager._check_connection_health()
                mock_reset.assert_called_once()


class TestConnectionHelpers:
    def test_test_connection_success(self, mock_settings):
        with patch("app.services.supabase.supabase_client.create_client") as mock_create:
            mock_client = _make_table_chain(success=True)
            mock_create.return_value = mock_client
            assert test_supabase_connection() is True

    def test_test_connection_missing_table(self, mock_settings):
        with patch("app.services.supabase.supabase_client.create_client") as mock_create:
            mock_client = _make_table_chain(
                success=False, raise_msg='relation "users" does not exist'
            )
            mock_create.return_value = mock_client
            assert test_supabase_connection() is False

    def test_test_connection_other_error(self, mock_settings):
        with patch("app.services.supabase.supabase_client.create_client") as mock_create:
            mock_client = _make_table_chain(success=False, raise_msg="timeout")
            mock_create.return_value = mock_client
            assert test_supabase_connection() is False

    def test_get_supabase_client_returns_client(self, mock_settings):
        with patch("app.services.supabase.supabase_client.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            client = get_supabase_client()
            assert client is mock_client
