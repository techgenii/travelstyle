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
Authentication validators for TravelStyle AI application.
Defines validation functions for authentication data.
"""

import re
from typing import Any

from app.services.auth.exceptions import AuthenticationError


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False

    # Basic email validation pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if not password or not isinstance(password, str):
        return False

    # Minimum length check
    if len(password) < 6:
        return False

    return True


def validate_user_id(user_id: str) -> bool:
    """Validate user ID format."""
    if not user_id or not isinstance(user_id, str):
        return False

    # UUID-like format validation (basic)
    pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    return bool(re.match(pattern, user_id))


def validate_token(token: str) -> bool:
    """Validate token format."""
    if not token or not isinstance(token, str):
        return False

    # Basic token validation (JWT-like)
    if len(token) < 10:
        return False

    return True


def validate_user_metadata(metadata: dict[str, Any]) -> bool:
    """Validate user metadata structure."""
    if not isinstance(metadata, dict):
        return False

    # Check for required fields if present
    for key, value in metadata.items():
        if not isinstance(key, str):
            return False
        if value is not None and not isinstance(value, (str, int, bool, float)):
            return False

    return True


def validate_auth_request(email: str, password: str) -> None:
    """Validate authentication request data."""
    if not validate_email(email):
        raise AuthenticationError("Invalid email format")

    if not validate_password(password):
        raise AuthenticationError("Invalid password format")


def validate_registration_data(
    email: str, password: str, first_name: str | None = None, last_name: str | None = None
) -> None:
    """Validate user registration data."""
    validate_auth_request(email, password)

    if first_name is not None and not isinstance(first_name, str):
        raise AuthenticationError("Invalid first name format")

    if last_name is not None and not isinstance(last_name, str):
        raise AuthenticationError("Invalid last name format")
