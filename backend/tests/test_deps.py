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

from unittest.mock import Mock, patch

import pytest
from app.api.deps import get_current_active_user, get_current_user
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


@pytest.fixture
def mock_credentials():
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = "valid.jwt.token"
    return credentials


@pytest.mark.asyncio
async def test_get_current_user_valid_token(mock_credentials):
    with patch("app.api.deps.supabase_auth.verify_jwt_token") as mock_verify:
        mock_verify.return_value = {
            "id": "user-123",
            "email": "test@example.com",
            "is_active": True,
        }
        result = await get_current_user(mock_credentials)
        assert result["id"] == "user-123"
        assert result["email"] == "test@example.com"
        mock_verify.assert_called_once_with("valid.jwt.token")


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_credentials):
    with patch("app.api.deps.supabase_auth.verify_jwt_token") as mock_verify:
        mock_verify.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_exception(mock_credentials):
    with patch("app.api.deps.supabase_auth.verify_jwt_token") as mock_verify:
        mock_verify.side_effect = Exception("Token verification failed")
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_missing_credentials():
    # Create a mock credentials object with None credentials
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = None
    with patch("app.api.deps.supabase_auth.verify_jwt_token") as mock_verify:
        mock_verify.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_active_user_active():
    active_user = {"id": "user-123", "email": "test@example.com", "is_active": True}
    result = await get_current_active_user(active_user)
    assert result == active_user


@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    inactive_user = {"id": "user-123", "email": "test@example.com", "is_active": False}
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(inactive_user)
    assert exc_info.value.status_code == 400
    assert "Inactive user" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_active_user_missing_is_active():
    user_without_active = {
        "id": "user-123",
        "email": "test@example.com",
        # Missing "is_active" field
    }
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(user_without_active)
    assert exc_info.value.status_code == 400
    assert "Inactive user" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_active_user_none_is_active():
    user_with_none_active = {"id": "user-123", "email": "test@example.com", "is_active": None}
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(user_with_none_active)
    assert exc_info.value.status_code == 400
    assert "Inactive user" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_empty_credentials():
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = ""
    with patch("app.api.deps.supabase_auth.verify_jwt_token") as mock_verify:
        mock_verify.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_none_credentials():
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = None
    with patch("app.api.deps.supabase_auth.verify_jwt_token") as mock_verify:
        mock_verify.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
