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
Authentication helpers for TravelStyle AI application.
Contains the core AuthService class and utility functions.
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.models.auth import (
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshTokenResponse,
    RegisterResponse,
    ResetPasswordResponse,
)
from app.services.auth.constants import (
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
    REGISTRATION_FAILED_MSG,
    UPDATED_AT_FIELD,
    USER_ID_FIELD,
    USER_PREFERENCES_TABLE,
    USER_PROFILE_VIEW,
)
from app.services.auth.exceptions import (
    AuthenticationError,
    ClientInitializationError,
    RateLimitError,
    RegistrationError,
    TokenError,
)
from app.services.auth.validators import validate_auth_request, validate_registration_data
from app.services.rate_limiter import db_rate_limiter
from app.services.supabase import get_supabase_client
from app.utils.user_utils import extract_user_profile
from supabase import Client

logger = logging.getLogger(__name__)


class AuthService:
    """Supabase authentication service for user management."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client | None = None
        self._init_client()

    def _init_client(self):
        """Initialize Supabase client."""
        try:
            # Use the shared client for better connection pooling
            self.client = get_supabase_client()
            logger.info("Supabase client initialized successfully")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to initialize Supabase client: %s - %s", type(e).__name__, str(e))
            # Log more details for debugging
            if hasattr(e, "__cause__") and e.__cause__:
                logger.error("Caused by: %s - %s", type(e.__cause__).__name__, str(e.__cause__))
            raise ClientInitializationError(f"Failed to initialize client: {e}") from e

    def _check_client(self):
        """Check if client is initialized."""
        if not self.client:
            raise ClientInitializationError(CLIENT_NOT_INITIALIZED_MSG)

    async def _check_rate_limit(self, operation: str) -> bool:
        """Check rate limit for auth operations."""
        if not await db_rate_limiter.acquire(AUTH_RATE_LIMIT_KEY):
            logger.warning("Rate limited: %s", operation)
            raise RateLimitError(RATE_LIMITED_MSG)
        return True

    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """Authenticate user with email and password."""
        self._check_client()
        await self._check_rate_limit("login")

        # Validate input
        validate_auth_request(login_data.email, login_data.password)

        try:
            response = await asyncio.to_thread(
                lambda: self.client.auth.sign_in_with_password(
                    {"email": login_data.email, "password": login_data.password}
                )
            )

            if not response.user:
                raise AuthenticationError(INVALID_CREDENTIALS_MSG)
            if not response.session:
                raise AuthenticationError(NO_SESSION_MSG)

            # Update last_login field
            user_id = response.user.id
            try:
                current_time = datetime.now(UTC).isoformat()
                logger.info(
                    f"Attempting to update last_login for user {user_id} with time: {current_time}"
                )

                # Try updating users table directly first to test
                update_data = {LAST_LOGIN_FIELD: current_time}
                logger.info(f"Update data: {update_data}")

                # First try the view
                try:
                    response_update = await asyncio.to_thread(
                        lambda: self.client.table(USER_PROFILE_VIEW)
                        .update(update_data)
                        .eq(ID_FIELD, user_id)
                        .execute()
                    )
                    logger.info(f"Successfully updated last_login via view for user {user_id}")
                except Exception as view_error:
                    logger.warning(f"View update failed, trying users table directly: {view_error}")
                    # Fallback to users table
                    response_update = await asyncio.to_thread(
                        lambda: self.client.table("users")
                        .update(update_data)
                        .eq(ID_FIELD, user_id)
                        .execute()
                    )
                    logger.info(
                        f"Successfully updated last_login via users table for user {user_id}"
                    )

            except Exception as e:
                logger.warning(f"Failed to update last_login for user {user_id}: {e}")
                # Log more details about the error
                if hasattr(e, "response"):
                    logger.warning(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
                    logger.warning(f"Response text: {getattr(e.response, 'text', 'N/A')}")
                if hasattr(e, "message"):
                    logger.warning(f"Error message: {e.message}")
                if hasattr(e, "details"):
                    logger.warning(f"Error details: {e.details}")

            # Get complete user profile from user_profile_view
            try:
                user_profile = await self.get_complete_user_profile(user_id)
                if not user_profile:
                    # Fallback to extracted profile if view doesn't have data yet
                    user_profile = extract_user_profile(response.user) or {}
            except Exception as e:
                logger.warning(f"Failed to get user profile from view for user {user_id}: {e}")
                # Fallback to extracted profile
                user_profile = extract_user_profile(response.user) or {}
            return LoginResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type=DEFAULT_TOKEN_TYPE,
                expires_in=response.session.expires_in,
                user=user_profile,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Login failed for email %s: %s - %s", login_data.email, type(e).__name__, str(e)
            )
            # Log more details for debugging
            if hasattr(e, "__cause__") and e.__cause__:
                logger.error("Caused by: %s - %s", type(e.__cause__).__name__, str(e.__cause__))
            raise AuthenticationError(INVALID_CREDENTIALS_MSG) from e

    async def logout(self, refresh_token: str | None = None) -> LogoutResponse:
        """Logout user and revoke tokens."""
        self._check_client()
        await self._check_rate_limit("logout")

        try:
            if refresh_token:
                await asyncio.to_thread(lambda: self.client.auth.admin.sign_out(refresh_token))
            else:
                await asyncio.to_thread(lambda: self.client.auth.sign_out())
            return LogoutResponse(message="Successfully logged out", success=True)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Logout failed: %s", type(e).__name__)
            return LogoutResponse(message="Logged out successfully", success=True)

    async def forgot_password(self, email: str) -> ForgotPasswordResponse:
        """Send password reset email."""
        self._check_client()
        await self._check_rate_limit("forgot_password")

        try:
            await asyncio.to_thread(lambda: self.client.auth.reset_password_email(email))
            return ForgotPasswordResponse(
                message="Password reset email sent successfully", success=True
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Password reset email failed: %s", type(e).__name__)
            return ForgotPasswordResponse(
                message="If the email exists, a password reset link has been sent", success=True
            )

    async def reset_password(self, token: str, new_password: str) -> ResetPasswordResponse:
        """Reset password using reset token."""
        # token argument is required for interface compatibility
        # pylint: disable=unused-argument
        self._check_client()
        await self._check_rate_limit("reset_password")

        try:
            await asyncio.to_thread(
                lambda: self.client.auth.update_user({"password": new_password})
            )
            return ResetPasswordResponse(message="Password reset successfully", success=True)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Password reset failed: %s", type(e).__name__)
            raise TokenError(INVALID_TOKEN_MSG) from e

    async def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        """Refresh access token using refresh token."""
        self._check_client()
        await self._check_rate_limit("refresh_token")

        try:
            response = await asyncio.to_thread(
                lambda: self.client.auth.refresh_session(refresh_token)
            )
            if not response.session:
                raise TokenError(NO_SESSION_MSG)
            return RefreshTokenResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type=DEFAULT_TOKEN_TYPE,
                expires_in=response.session.expires_in,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Token refresh failed: %s", type(e).__name__)
            raise TokenError(INVALID_REFRESH_TOKEN_MSG) from e

    async def register(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> RegisterResponse:
        """Register new user."""
        self._check_client()
        await self._check_rate_limit("register")

        # Validate input
        validate_registration_data(email, password, first_name, last_name)

        try:
            response = await asyncio.to_thread(
                lambda: self.client.auth.sign_up(
                    {
                        "email": email,
                        "password": password,
                        "options": {
                            "data": {
                                FIRST_NAME_FIELD: first_name,
                                LAST_NAME_FIELD: last_name,
                            }
                        },
                    }
                )
            )
            if not response.user:
                raise RegistrationError(FAILED_CREATE_USER_MSG)

            # Immediately sign in to get token after registration
            login_response = await asyncio.to_thread(
                lambda: self.client.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
            )
            if not login_response.session:
                raise RegistrationError(NO_SESSION_AFTER_REGISTRATION_MSG)

            # Create user preferences record to ensure profile is available
            user_id = response.user.id
            try:
                await asyncio.to_thread(
                    lambda: self.client.table(USER_PREFERENCES_TABLE)
                    .insert(
                        {
                            "user_id": user_id,
                            "style_preferences": {},
                            "size_info": {},
                            "travel_patterns": {},
                            "quick_reply_preferences": {},
                            "packing_methods": {},
                            "currency_preferences": {},
                        }
                    )
                    .execute()
                )
                logger.info(f"Created user preferences for user {user_id}")
            except Exception as e:
                # If preferences already exist, that's fine
                logger.info(f"User preferences creation for {user_id}: {e}")

            # Get complete user profile from user_profile_view
            try:
                user_profile = await self.get_complete_user_profile(user_id)
                if not user_profile:
                    # Fallback to extracted profile if view doesn't have data yet
                    user_profile = extract_user_profile(login_response.user) or {}
            except Exception as e:
                logger.warning(f"Failed to get user profile from view for user {user_id}: {e}")
                # Fallback to extracted profile
                user_profile = extract_user_profile(login_response.user) or {}
            return RegisterResponse(
                access_token=login_response.session.access_token,
                token_type=DEFAULT_TOKEN_TYPE,
                expires_in=login_response.session.expires_in,
                message="Registration successful",
                user_id=user_profile.get("id", ""),
                success=True,
                user=user_profile,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("User registration failed: %s", type(e).__name__)
            raise RegistrationError(REGISTRATION_FAILED_MSG) from e

    async def get_user_profile(self, user_id: str) -> dict[str, Any] | None:
        """Get user profile information from user_profile_view."""
        self._check_client()

        # Apply rate limiting for read operations
        if not await db_rate_limiter.acquire("read"):
            logger.warning("Rate limited: get_user_profile")
            return None

        try:
            # Use the user_profile_view instead of auth admin
            response = await asyncio.to_thread(
                lambda: (
                    self.client.table(USER_PROFILE_VIEW).select("*").eq(ID_FIELD, user_id).execute()
                )
            )
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get user profile for %s: %s", user_id, type(e).__name__)
            return None

    async def get_complete_user_profile(self, user_id: str) -> dict[str, Any] | None:
        """Get complete user profile with all related data from user_profile_view."""
        self._check_client()

        # Apply rate limiting for read operations
        if not await db_rate_limiter.acquire("read"):
            logger.warning("Rate limited: get_complete_user_profile")
            return None

        try:
            # Get complete profile from user_profile_view which includes:
            # - User auth data (email, metadata, etc.)
            # - User preferences (style, size, travel patterns, etc.)
            # - Saved destinations
            # - Currency preferences
            # - Packing templates
            # - And other related data
            response = await asyncio.to_thread(
                lambda: (
                    self.client.table(USER_PROFILE_VIEW)
                    .select("*")
                    .eq(ID_FIELD, user_id)
                    .single()
                    .execute()
                )
            )

            if response.data:
                logger.info(f"Retrieved complete profile for user {user_id}")
                return response.data
            else:
                logger.warning(f"No profile data found for user {user_id}")
                return None

        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Failed to get complete user profile for %s: %s", user_id, type(e).__name__
            )
            return None

    async def update_user_profile(
        self, user_id: str, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update user profile information."""
        self._check_client()

        # Apply rate limiting for write operations
        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: update_user_profile")
            return None

        try:
            response = await asyncio.to_thread(
                lambda: self.client.auth.admin.update_user_by_id(
                    user_id, {"user_metadata": updates}
                )
            )
            if response.user:
                return extract_user_profile(response.user)
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to update user profile for %s: %s", user_id, type(e).__name__)
            return None

    async def update_user_profile_sync(
        self, user_id: str, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update user profile and sync across all tables using user_profile_view."""
        self._check_client()

        # Apply rate limiting for write operations
        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: update_user_profile_sync")
            return None

        try:
            # Update Supabase auth user metadata
            auth_response = await asyncio.to_thread(
                lambda: self.client.auth.admin.update_user_by_id(
                    user_id, {"user_metadata": updates}
                )
            )

            if not auth_response.user:
                logger.error("Failed to update auth user for %s", user_id)
                return None

            # Update profile_completed status if name fields are being updated
            if FIRST_NAME_FIELD in updates or LAST_NAME_FIELD in updates:
                first_name = updates.get(FIRST_NAME_FIELD) or auth_response.user.user_metadata.get(
                    FIRST_NAME_FIELD
                )
                last_name = updates.get(LAST_NAME_FIELD) or auth_response.user.user_metadata.get(
                    LAST_NAME_FIELD
                )
                updates[PROFILE_COMPLETED_FIELD] = bool(first_name and last_name)

            # Update the view directly - triggers will handle updating underlying tables
            response = await asyncio.to_thread(
                lambda: (
                    self.client.table(USER_PROFILE_VIEW)
                    .update(updates)
                    .eq(ID_FIELD, user_id)
                    .execute()
                )
            )

            if not response.data or len(response.data) == 0:
                logger.error("Failed to update user profile for %s: no data returned", user_id)
                return None

            logger.info("User profile updated successfully for %s via view", user_id)
            return response.data[0]

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to update user profile for %s: %s", user_id, type(e).__name__)
            return None

    async def update_user_preferences(self, user_id: str, preferences: dict[str, Any]) -> bool:
        """Update user preferences in the database."""
        self._check_client()

        # Apply rate limiting for write operations
        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: update_user_preferences")
            return False

        try:
            # Update user_preferences table
            await asyncio.to_thread(
                lambda: (
                    self.client.table(USER_PREFERENCES_TABLE)
                    .update({**preferences, UPDATED_AT_FIELD: "now()"})
                    .eq(USER_ID_FIELD, user_id)
                    .execute()
                )
            )

            logger.info("User preferences updated successfully for %s", user_id)
            return True

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to update user preferences for %s: %s", user_id, type(e).__name__)
            return False
