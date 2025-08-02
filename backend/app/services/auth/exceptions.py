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
Authentication exceptions for TravelStyle AI application.
Defines custom exceptions for authentication operations.
"""


class AuthServiceError(Exception):
    """Base exception for authentication service errors."""

    pass


class AuthenticationError(AuthServiceError):
    """Exception raised for authentication failures."""

    pass


class ClientInitializationError(AuthServiceError):
    """Exception raised when Supabase client fails to initialize."""

    pass


class RateLimitError(AuthServiceError):
    """Exception raised when rate limits are exceeded."""

    pass


class UserProfileError(AuthServiceError):
    """Exception raised for user profile operation failures."""

    pass


class TokenError(AuthServiceError):
    """Exception raised for token-related operation failures."""

    pass


class RegistrationError(AuthServiceError):
    """Exception raised for user registration failures."""

    pass
