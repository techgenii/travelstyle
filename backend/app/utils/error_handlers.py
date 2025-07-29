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
Error handling utilities for TravelStyle AI application.
Provides centralized error handling and logging patterns.
"""

import functools
import logging
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


async def custom_http_exception_handler(request, exc):
    """Custom HTTP exception handler for FastAPI."""
    from fastapi.responses import JSONResponse

    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "status_code": exc.status_code},
        )
    else:
        # Handle non-HTTP exceptions (like ValueError, etc.)
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error", "status_code": 500}
        )


def handle_api_errors(error_message: str, status_code: int = 500):
    """
    Decorator to standardize error handling across API endpoints.

    Args:
        error_message: The error message to return to the client
        status_code: HTTP status code (default: 500)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except Exception as e:
                logger.error("%s error: %s", func.__name__, type(e).__name__)
                raise HTTPException(status_code=status_code, detail=error_message) from e

        return wrapper

    return decorator


def validate_user_id(current_user: dict) -> str:
    """
    Validate and extract user ID from current_user dict.

    Args:
        current_user: The current user dictionary from authentication

    Returns:
        The validated user ID

    Raises:
        HTTPException: If user ID is invalid or missing
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    return user_id


def validate_required_fields(data: dict, required_fields: list[str]) -> None:
    """
    Validate that required fields are present in request data.

    Args:
        data: The request data dictionary
        required_fields: List of required field names

    Raises:
        HTTPException: If any required fields are missing
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {', '.join(missing_fields)}",
        )


def validate_data_not_empty(data: dict, field_name: str = "data") -> None:
    """
    Validate that request data is not empty.

    Args:
        data: The request data dictionary
        field_name: Name of the field for error message

    Raises:
        HTTPException: If data is empty
    """
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name.title()} is required"
        )
