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
Authentication service for TravelStyle AI application.
Handles Supabase authentication operations including login, logout, password reset,
and user registration.

This module is maintained for backward compatibility.
For new code, use the modular structure in app.services.auth.*
"""

# Import everything from the new modular structure
from app.services.auth import (
    AUTH_RATE_LIMIT_KEY,
    CLIENT_NOT_INITIALIZED_MSG,
    DEFAULT_TOKEN_TYPE,
    FAILED_CREATE_USER_MSG,
    FIRST_NAME_FIELD,
    ID_FIELD,
    INVALID_CREDENTIALS_MSG,
    INVALID_REFRESH_TOKEN_MSG,
    INVALID_TOKEN_MSG,
    LAST_LOGIN_FIELD,
    LAST_NAME_FIELD,
    NO_SESSION_AFTER_REGISTRATION_MSG,
    NO_SESSION_MSG,
    PROFILE_COMPLETED_FIELD,
    RATE_LIMITED_MSG,
    READ_RATE_LIMIT_KEY,
    REGISTRATION_FAILED_MSG,
    UPDATED_AT_FIELD,
    USER_ID_FIELD,
    USER_PREFERENCES_TABLE,
    USER_PROFILE_VIEW,
    USERS_TABLE,
    WRITE_RATE_LIMIT_KEY,
    AuthenticationError,
    AuthService,
    AuthServiceError,
    ClientInitializationError,
    RateLimitError,
    RegistrationError,
    TokenError,
    UserProfileError,
    validate_auth_request,
    validate_email,
    validate_password,
    validate_registration_data,
    validate_token,
    validate_user_id,
    validate_user_metadata,
)

# Re-export for backward compatibility
__all__ = [
    "AuthService",
    "AuthServiceError",
    "AuthenticationError",
    "ClientInitializationError",
    "RateLimitError",
    "RegistrationError",
    "TokenError",
    "UserProfileError",
    "validate_auth_request",
    "validate_email",
    "validate_password",
    "validate_registration_data",
    "validate_token",
    "validate_user_id",
    "validate_user_metadata",
    # Constants
    "AUTH_RATE_LIMIT_KEY",
    "CLIENT_NOT_INITIALIZED_MSG",
    "DEFAULT_TOKEN_TYPE",
    "FAILED_CREATE_USER_MSG",
    "FIRST_NAME_FIELD",
    "ID_FIELD",
    "INVALID_CREDENTIALS_MSG",
    "INVALID_REFRESH_TOKEN_MSG",
    "INVALID_TOKEN_MSG",
    "LAST_LOGIN_FIELD",
    "LAST_NAME_FIELD",
    "NO_SESSION_AFTER_REGISTRATION_MSG",
    "NO_SESSION_MSG",
    "PROFILE_COMPLETED_FIELD",
    "RATE_LIMITED_MSG",
    "READ_RATE_LIMIT_KEY",
    "REGISTRATION_FAILED_MSG",
    "UPDATED_AT_FIELD",
    "USER_ID_FIELD",
    "USER_PREFERENCES_TABLE",
    "USER_PROFILE_VIEW",
    "USERS_TABLE",
    "WRITE_RATE_LIMIT_KEY",
]

# Create a singleton instance for backward compatibility
auth_service = AuthService()
