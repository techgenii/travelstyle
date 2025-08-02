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
Authentication constants for TravelStyle AI application.
Defines rate limiting keys and other auth-related constants.
"""

# Rate limiting keys for different auth operations
AUTH_RATE_LIMIT_KEY = "auth"
READ_RATE_LIMIT_KEY = "read"
WRITE_RATE_LIMIT_KEY = "write"

# Default token type
DEFAULT_TOKEN_TYPE = "bearer"

# User metadata fields
FIRST_NAME_FIELD = "first_name"
LAST_NAME_FIELD = "last_name"
PROFILE_COMPLETED_FIELD = "profile_completed"

# Database table names
USERS_TABLE = "users"
USER_PROFILE_VIEW = "user_profile_view"
USER_PREFERENCES_TABLE = "user_preferences"

# Database field names
LAST_LOGIN_FIELD = "last_login"
UPDATED_AT_FIELD = "updated_at"
USER_ID_FIELD = "user_id"
ID_FIELD = "id"

# Error messages
INVALID_CREDENTIALS_MSG = "Invalid credentials"
NO_SESSION_MSG = "No session created"
RATE_LIMITED_MSG = "Too many attempts. Please try again later."
CLIENT_NOT_INITIALIZED_MSG = "Supabase client not initialized"
REGISTRATION_FAILED_MSG = "Registration failed. Email may already be in use."
INVALID_TOKEN_MSG = "Invalid or expired reset token"
INVALID_REFRESH_TOKEN_MSG = "Invalid refresh token"
FAILED_CREATE_USER_MSG = "Failed to create user"
NO_SESSION_AFTER_REGISTRATION_MSG = "No session created after registration"
