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
from app.utils.rate_limiter import rate_limit, rate_limit_storage
from fastapi import HTTPException, Request
from jwt import PyJWTError as JWTError


@pytest.fixture
def mock_request():
    request = Mock(spec=Request)
    request.client = Mock()
    request.client.host = "127.0.0.1"
    request.headers = {}
    return request


@pytest.fixture
def mock_request_with_auth():
    request = Mock(spec=Request)
    request.client = Mock()
    request.client.host = "127.0.0.1"
    request.headers = {"authorization": "Bearer valid.jwt.token"}
    return request


@pytest.fixture
def clear_rate_limit_storage():
    """Clear rate limit storage before and after each test"""
    rate_limit_storage.clear()
    yield
    rate_limit_storage.clear()


@patch("app.utils.rate_limiter.time.time")
@pytest.mark.asyncio
async def test_rate_limit_first_call(mock_time, mock_request, clear_rate_limit_storage):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0

    @rate_limit(calls=5, period=60)
    async def test_function(request):
        return "success"

    result = await test_function(mock_request)
    assert result == "success"
    assert len(rate_limit_storage) == 1
    key = "test_function:127.0.0.1"
    assert rate_limit_storage[key] == (1000.0, 1)


@patch("app.utils.rate_limiter.time.time")
@pytest.mark.asyncio
async def test_rate_limit_within_limit(mock_time, mock_request, clear_rate_limit_storage):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0

    @rate_limit(calls=3, period=60)
    async def test_function(request):
        return "success"

    # Make 3 calls within limit
    for i in range(3):
        result = await test_function(mock_request)
        assert result == "success"

    key = "test_function:127.0.0.1"
    assert rate_limit_storage[key] == (1000.0, 3)


@patch("app.utils.rate_limiter.time.time")
@pytest.mark.asyncio
async def test_rate_limit_exceeded(mock_time, mock_request, clear_rate_limit_storage):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0

    @rate_limit(calls=2, period=60)
    async def test_function(request):
        return "success"

    # Make 2 calls within limit
    await test_function(mock_request)
    await test_function(mock_request)

    # Third call should be rate limited
    with pytest.raises(HTTPException) as exc_info:
        await test_function(mock_request)

    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in exc_info.value.detail


@patch("app.utils.rate_limiter.time.time")
@pytest.mark.asyncio
async def test_rate_limit_reset_after_period(mock_time, mock_request, clear_rate_limit_storage):
    @rate_limit(calls=2, period=60)
    async def test_function(request):
        return "success"

    # First call
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0
    result = await test_function(mock_request)
    assert result == "success"

    # Second call within period
    mock_time.return_value = 1050.0  # 50 seconds later
    result = await test_function(mock_request)
    assert result == "success"

    # Third call should be rate limited
    with pytest.raises(HTTPException):
        await test_function(mock_request)

    # Call after period reset
    mock_time.return_value = 1070.0  # 70 seconds later (period passed)
    result = await test_function(mock_request)
    assert result == "success"

    key = "test_function:127.0.0.1"
    assert rate_limit_storage[key] == (1070.0, 1)


@patch("app.utils.rate_limiter.time.time")
@patch("app.utils.rate_limiter.jwt.decode")
@pytest.mark.asyncio
async def test_rate_limit_with_jwt_token(
    mock_jwt_decode, mock_time, mock_request_with_auth, clear_rate_limit_storage
):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0
    mock_jwt_decode.return_value = {"sub": "user-123"}

    @rate_limit(calls=5, period=60)
    async def test_function(request):
        return "success"

    result = await test_function(mock_request_with_auth)
    assert result == "success"

    key = "test_function:user-123"
    assert rate_limit_storage[key] == (1000.0, 1)


@patch("app.utils.rate_limiter.time.time")
@patch("app.utils.rate_limiter.jwt.decode")
@pytest.mark.asyncio
async def test_rate_limit_jwt_decode_failure(
    mock_jwt_decode, mock_time, mock_request_with_auth, clear_rate_limit_storage
):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0
    mock_jwt_decode.side_effect = JWTError("Invalid token")

    @rate_limit(calls=5, period=60)
    async def test_function(request):
        return "success"

    result = await test_function(mock_request_with_auth)
    assert result == "success"

    # Should fall back to IP address
    key = "test_function:127.0.0.1"
    assert rate_limit_storage[key] == (1000.0, 1)


@patch("app.utils.rate_limiter.time.time")
@pytest.mark.asyncio
async def test_rate_limit_no_request_object(mock_time, clear_rate_limit_storage):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0

    @rate_limit(calls=5, period=60)
    async def test_function(arg1, arg2):
        return f"success: {arg1} {arg2}"

    # Function without request object should skip rate limiting
    result = await test_function("hello", "world")
    assert result == "success: hello world"
    assert len(rate_limit_storage) == 0


@patch("app.utils.rate_limiter.time.time")
@pytest.mark.asyncio
async def test_rate_limit_request_without_client(mock_time, clear_rate_limit_storage):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0

    request = Mock(spec=Request)
    request.client = None
    request.headers = {}

    @rate_limit(calls=5, period=60)
    async def test_function(request):
        return "success"

    result = await test_function(request)
    assert result == "success"

    key = "test_function:unknown"
    assert rate_limit_storage[key] == (1000.0, 1)


# Removed cleanup tests as cleanup functionality was removed from rate limiter
# The new implementation doesn't include automatic cleanup


@patch("app.utils.rate_limiter.time.time")
@patch("app.utils.rate_limiter.jwt.decode")
@pytest.mark.asyncio
async def test_rate_limit_jwt_missing_sub(
    mock_jwt_decode, mock_time, mock_request_with_auth, clear_rate_limit_storage
):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0
    mock_jwt_decode.return_value = {"email": "test@example.com"}  # No "sub" field

    @rate_limit(calls=5, period=60)
    async def test_function(request):
        return "success"

    result = await test_function(mock_request_with_auth)
    assert result == "success"

    # Should fall back to IP address
    key = "test_function:127.0.0.1"
    assert rate_limit_storage[key] == (1000.0, 1)


@patch("app.utils.rate_limiter.time.time")
@patch("app.utils.rate_limiter.jwt.decode")
@pytest.mark.asyncio
async def test_rate_limit_jwt_value_error(
    mock_jwt_decode, mock_time, mock_request_with_auth, clear_rate_limit_storage
):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0
    mock_jwt_decode.side_effect = ValueError("Invalid token")

    @rate_limit(calls=5, period=60)
    async def test_function(request):
        return "success"

    result = await test_function(mock_request_with_auth)
    assert result == "success"

    # Should fall back to IP address
    key = "test_function:127.0.0.1"
    assert rate_limit_storage[key] == (1000.0, 1)


@patch("app.utils.rate_limiter.time.time")
@patch("app.utils.rate_limiter.jwt.decode")
@pytest.mark.asyncio
async def test_rate_limit_jwt_key_error(
    mock_jwt_decode, mock_time, mock_request_with_auth, clear_rate_limit_storage
):
    _ = clear_rate_limit_storage  # Mark fixture as used
    mock_time.return_value = 1000.0
    mock_jwt_decode.side_effect = KeyError("Missing key")

    @rate_limit(calls=5, period=60)
    async def test_function(request):
        return "success"

    result = await test_function(mock_request_with_auth)
    assert result == "success"

    # Should fall back to IP address
    key = "test_function:127.0.0.1"
    assert rate_limit_storage[key] == (1000.0, 1)
