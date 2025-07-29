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

import asyncio
from collections import namedtuple
from types import SimpleNamespace
from unittest.mock import patch

from app.utils.error_handlers import (
    custom_http_exception_handler,
    handle_api_errors,
    validate_data_not_empty,
    validate_required_fields,
    validate_user_id,
)
from app.utils.user_utils import extract_user_profile
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class DummyUser:
    def __init__(
        self,
        id=None,
        email=None,
        user_metadata=None,
        created_at=None,
        updated_at=None,
        email_confirmed_at=None,
        last_sign_in_at=None,
    ):
        self.id = id
        self.email = email
        self.user_metadata = user_metadata
        self.created_at = created_at
        self.updated_at = updated_at
        self.email_confirmed_at = email_confirmed_at
        self.last_sign_in_at = last_sign_in_at


def test_extract_user_profile_with_dict_metadata():
    DummyUser = namedtuple(
        "DummyUser",
        [
            "id",
            "email",
            "user_metadata",
            "created_at",
            "updated_at",
            "email_confirmed_at",
            "last_sign_in_at",
        ],
    )
    user = DummyUser(
        id="u1",
        email="test@example.com",
        user_metadata={
            "first_name": "Alice",
            "last_name": "Smith",
            "selected_style_names": ["Bohemian", "Minimalist"],
        },
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z",
        email_confirmed_at="2023-01-01T01:00:00Z",
        last_sign_in_at="2023-01-03T00:00:00Z",
    )
    profile = extract_user_profile(user)
    assert profile is not None
    assert profile["id"] == "u1"
    assert profile["email"] == "test@example.com"
    assert profile["first_name"] == "Alice"
    assert profile["last_name"] == "Smith"
    assert profile["created_at"] == "2023-01-01T00:00:00Z"
    assert profile["updated_at"] == "2023-01-02T00:00:00Z"
    assert profile["email_confirmed_at"] == "2023-01-01T01:00:00Z"
    assert profile["last_sign_in_at"] == "2023-01-03T00:00:00Z"
    assert profile["selected_style_names"] == ["Bohemian", "Minimalist"]


def test_extract_user_profile_with_object_metadata():
    metadata = SimpleNamespace(first_name="Bob", last_name="Jones")
    user = DummyUser(
        id="u2",
        email="bob@example.com",
        user_metadata=metadata,
        created_at=None,
        updated_at=None,
        email_confirmed_at=None,
        last_sign_in_at=None,
    )
    profile = extract_user_profile(user)
    assert profile is not None
    assert profile["id"] == "u2"
    assert profile["email"] == "bob@example.com"
    assert profile["first_name"] == "Bob"
    assert profile["last_name"] == "Jones"
    assert profile["created_at"] is None
    assert profile["updated_at"] is None
    assert profile["email_confirmed_at"] is None
    assert profile["last_sign_in_at"] is None


def test_extract_user_profile_with_no_metadata():
    user = DummyUser(id="u3", email="no.meta@example.com", user_metadata=None)
    profile = extract_user_profile(user)
    assert profile is not None
    assert profile["id"] == "u3"
    assert profile["email"] == "no.meta@example.com"
    assert profile["first_name"] is None
    assert profile["last_name"] is None


def test_extract_user_profile_with_missing_attributes():
    # User missing created_at, updated_at, etc.
    user = DummyUser(id="u4", email="missing@example.com", user_metadata={"first_name": "X"})
    profile = extract_user_profile(user)
    assert profile is not None
    assert profile["id"] == "u4"
    assert profile["email"] == "missing@example.com"
    assert profile["first_name"] == "X"
    assert profile["last_name"] is None
    assert profile["created_at"] is None
    assert profile["updated_at"] is None
    assert profile["email_confirmed_at"] is None
    assert profile["last_sign_in_at"] is None


def test_extract_user_profile_with_none_user():
    assert extract_user_profile(None) is None


class DummyRequest:
    url = "http://testserver/test"


def test_custom_http_exception_handler_non_http_exception():
    request = DummyRequest()
    exc = ValueError("Some error")
    response = asyncio.run(custom_http_exception_handler(request, exc))
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.body is not None
    assert b"Internal server error" in response.body


def test_custom_http_exception_handler_http_exception():
    """Test custom HTTP exception handler with HTTPException."""
    request = DummyRequest()
    exc = HTTPException(status_code=404, detail="Not found")
    response = asyncio.run(custom_http_exception_handler(request, exc))
    assert isinstance(response, JSONResponse)
    assert response.status_code == 404
    assert response.body is not None
    assert b"Not found" in response.body
    assert b"status_code" in response.body


def test_validate_user_id_success():
    """Test validate_user_id with valid user ID."""
    current_user = {"id": "user123", "email": "test@example.com"}
    user_id = validate_user_id(current_user)
    assert user_id == "user123"


def test_validate_user_id_missing_id():
    """Test validate_user_id with missing user ID."""
    current_user = {"email": "test@example.com"}  # No 'id' field
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            validate_user_id(current_user)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Invalid user ID"


def test_validate_user_id_empty_id():
    """Test validate_user_id with empty user ID."""
    current_user = {"id": "", "email": "test@example.com"}
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            validate_user_id(current_user)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Invalid user ID"


def test_validate_user_id_none_id():
    """Test validate_user_id with None user ID."""
    current_user = {"id": None, "email": "test@example.com"}
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            validate_user_id(current_user)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Invalid user ID"


def test_validate_required_fields_success():
    """Test validate_required_fields with all required fields present."""
    data = {"name": "John", "email": "john@example.com", "age": 30}
    required_fields = ["name", "email"]
    # Should not raise any exception
    validate_required_fields(data, required_fields)


def test_validate_required_fields_missing_single():
    """Test validate_required_fields with one missing field."""
    data = {"name": "John", "age": 30}  # Missing 'email'
    required_fields = ["name", "email"]
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            validate_required_fields(data, required_fields)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Missing required fields: email"


def test_validate_required_fields_missing_multiple():
    """Test validate_required_fields with multiple missing fields."""
    data = {"name": "John"}  # Missing 'email' and 'age'
    required_fields = ["name", "email", "age"]
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            validate_required_fields(data, required_fields)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Missing required fields: email, age"


def test_validate_required_fields_empty_data():
    """Test validate_required_fields with empty data."""
    data = {}
    required_fields = ["name", "email"]
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            validate_required_fields(data, required_fields)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Missing required fields: name, email"


def test_validate_required_fields_empty_required_list():
    """Test validate_required_fields with empty required fields list."""
    data = {"name": "John", "email": "john@example.com"}
    required_fields = []
    # Should not raise any exception
    validate_required_fields(data, required_fields)


def test_validate_data_not_empty_success():
    """Test validate_data_not_empty with non-empty data."""
    data = {"name": "John", "email": "john@example.com"}
    # Should not raise any exception
    validate_data_not_empty(data)


def test_validate_data_not_empty_empty_dict():
    """Test validate_data_not_empty with empty dictionary."""
    data = {}
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            validate_data_not_empty(data)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Data is required"


def test_validate_data_not_empty_none_data():
    """Test validate_data_not_empty with None data."""
    data = None
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            validate_data_not_empty(data)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Data is required"


def test_validate_data_not_empty_custom_field_name():
    """Test validate_data_not_empty with custom field name."""
    data = {}
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            validate_data_not_empty(data, field_name="request body")
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Request Body is required"  # title() capitalizes first letter


def test_handle_api_errors_success():
    """Test handle_api_errors decorator with successful function."""

    @handle_api_errors("Test error", 400)
    async def test_function():
        return {"success": True}

    result = asyncio.run(test_function())
    assert result == {"success": True}


def test_handle_api_errors_http_exception():
    """Test handle_api_errors decorator with HTTPException (should re-raise)."""

    @handle_api_errors("Test error", 400)
    async def test_function():
        raise HTTPException(status_code=404, detail="Not found")

    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            asyncio.run(test_function())
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == 404
            assert e.detail == "Not found"


def test_handle_api_errors_generic_exception():
    """Test handle_api_errors decorator with generic exception."""

    @handle_api_errors("Database error", 500)
    async def test_function():
        raise ValueError("Database connection failed")

    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            asyncio.run(test_function())
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == 500
            assert e.detail == "Database error"
            # Verify logging was called with format string
            mock_logger.error.assert_called_once_with("%s error: %s", "test_function", "ValueError")


def test_handle_api_errors_custom_status_code():
    """Test handle_api_errors decorator with custom status code."""

    @handle_api_errors("Validation error", 422)
    async def test_function():
        raise TypeError("Invalid data type")

    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            asyncio.run(test_function())
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == 422
            assert e.detail == "Validation error"
            # Verify logging was called with format string
            mock_logger.error.assert_called_once_with("%s error: %s", "test_function", "TypeError")


def test_handle_api_errors_with_parameters():
    """Test handle_api_errors decorator with function parameters."""

    @handle_api_errors("Processing error", 500)
    async def test_function(param1: str, param2: int):
        if param1 == "error":
            raise RuntimeError("Processing failed")
        return {"param1": param1, "param2": param2}

    # Test successful case
    result = asyncio.run(test_function("test", 42))
    assert result == {"param1": "test", "param2": 42}

    # Test error case
    with patch("app.utils.error_handlers.logger") as mock_logger:
        try:
            asyncio.run(test_function("error", 42))
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == 500
            assert e.detail == "Processing error"
            # Verify logging was called with format string
            mock_logger.error.assert_called_once_with(
                "%s error: %s", "test_function", "RuntimeError"
            )


def test_handle_api_errors_preserves_function_metadata():
    """Test that handle_api_errors preserves function metadata."""

    @handle_api_errors("Test error", 400)
    async def test_function():
        """Test function docstring."""
        return True

    # Check that function metadata is preserved
    assert test_function.__name__ == "test_function"
    assert test_function.__doc__ == "Test function docstring."
    assert callable(test_function)
