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

from postgrest import APIError

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
    EMAIL_ALREADY_IN_USE_MSG,
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
    WEAK_PASSWORD_MSG,
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

                # Update profiles table directly for last_login (simpler and more reliable)
                await asyncio.to_thread(
                    lambda: self.client.table("profiles")
                    .update(update_data)
                    .eq(ID_FIELD, user_id)
                    .execute()
                )
                logger.info(
                    f"Successfully updated last_login via profiles table for user {user_id}"
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

                # Always ensure user preferences are included by fetching them separately
                try:
                    logger.info("Fetching user preferences separately to ensure they're included")
                    preferences_response = await asyncio.to_thread(
                        lambda: (
                            self.client.table("user_preferences")
                            .select("*")
                            .eq("user_id", user_id)
                            .single()
                            .execute()
                        )
                    )

                    if preferences_response.data:
                        logger.info(f"Retrieved user preferences: {preferences_response.data}")
                        # Merge preferences with user profile
                        user_profile.update(preferences_response.data)
                        logger.info(
                            f"Updated profile with preferences, final keys: {list(user_profile.keys())}"
                        )
                    else:
                        logger.info("No user preferences found in database, using defaults")
                        # Add default preference fields
                        default_preferences = {
                            "style_preferences": {},
                            "size_info": {},
                            "travel_patterns": {},
                            "quick_reply_preferences": {"enabled": True},
                            "packing_methods": {},
                            "currency_preferences": {},
                        }
                        user_profile.update(default_preferences)
                        logger.info("Added default preferences to profile")

                except Exception as pref_error:
                    logger.warning(f"Failed to fetch user preferences separately: {pref_error}")
                    # Add default preference fields as fallback
                    default_preferences = {
                        "style_preferences": {},
                        "size_info": {},
                        "travel_patterns": {},
                        "quick_reply_preferences": {"enabled": True},
                        "packing_methods": {},
                        "currency_preferences": {},
                    }
                    user_profile.update(default_preferences)
                    logger.info("Added default preferences to profile after error")

                # Ensure all preference fields exist
                preference_fields = [
                    "style_preferences",
                    "size_info",
                    "travel_patterns",
                    "quick_reply_preferences",
                    "packing_methods",
                    "currency_preferences",
                ]

                for field in preference_fields:
                    if field not in user_profile:
                        logger.info(f"Adding missing preference field: {field} with default value")
                        if field == "quick_reply_preferences":
                            user_profile[field] = {"enabled": True}
                        else:
                            user_profile[field] = {}

                logger.info(f"Final user profile for login response: {user_profile}")

            except Exception as e:
                logger.warning(f"Failed to get user profile from view for user {user_id}: {e}")
                # Fallback to extracted profile
                user_profile = extract_user_profile(response.user) or {}

                # Always try to fetch preferences even in fallback
                try:
                    logger.info("Attempting to fetch preferences in fallback mode")
                    preferences_response = await asyncio.to_thread(
                        lambda: (
                            self.client.table("user_preferences")
                            .select("*")
                            .eq("user_id", user_id)
                            .single()
                            .execute()
                        )
                    )

                    if preferences_response.data:
                        logger.info(
                            f"Retrieved user preferences in fallback: {preferences_response.data}"
                        )
                        user_profile.update(preferences_response.data)
                    else:
                        logger.info("No preferences found in fallback, using defaults")
                        default_preferences = {
                            "style_preferences": {},
                            "size_info": {},
                            "travel_patterns": {},
                            "quick_reply_preferences": {"enabled": True},
                            "packing_methods": {},
                            "currency_preferences": {},
                        }
                        user_profile.update(default_preferences)

                except Exception as pref_error:
                    logger.warning(f"Failed to fetch preferences in fallback: {pref_error}")
                    default_preferences = {
                        "style_preferences": {},
                        "size_info": {},
                        "travel_patterns": {},
                        "quick_reply_preferences": {"enabled": True},
                        "packing_methods": {},
                        "currency_preferences": {},
                    }
                    user_profile.update(default_preferences)

                # Ensure basic preference fields exist even in fallback
                preference_fields = [
                    "style_preferences",
                    "size_info",
                    "travel_patterns",
                    "quick_reply_preferences",
                    "packing_methods",
                    "currency_preferences",
                ]

                for field in preference_fields:
                    if field not in user_profile:
                        if field == "quick_reply_preferences":
                            user_profile[field] = {"enabled": True}
                        else:
                            user_profile[field] = {}

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

            # Clear any session that might have been set by sign_up to prevent
            # automatic token refresh attempts with invalid refresh tokens
            try:
                await asyncio.to_thread(lambda: self.client.auth.sign_out())
            except Exception as sign_out_error:
                # Log but don't fail if sign_out fails - it's just a cleanup step
                logger.debug(f"Sign out after registration (cleanup) failed: {sign_out_error}")

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
                refresh_token=login_response.session.refresh_token,
                token_type=DEFAULT_TOKEN_TYPE,
                expires_in=login_response.session.expires_in,
                message="Registration successful",
                user_id=user_profile.get("id", ""),
                success=True,
                user=user_profile,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("User registration failed: %s - %s", type(e).__name__, str(e))

            # Check for specific error types
            error_type_name = type(e).__name__
            error_message = str(e).lower()

            # Handle weak password error
            if (
                "weakpassword" in error_type_name.lower()
                or "weak password" in error_message
                or ("weak" in error_message and "password" in error_message)
            ):
                raise RegistrationError(WEAK_PASSWORD_MSG) from e

            # Handle email already in use
            if "email" in error_message and (
                "already" in error_message or "exists" in error_message or "taken" in error_message
            ):
                raise RegistrationError(EMAIL_ALREADY_IN_USE_MSG) from e

            # Generic fallback
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
            logger.info(f"Attempting to query user_profile_view for user {user_id}")
            logger.info(f"Using table: {USER_PROFILE_VIEW}, ID field: {ID_FIELD}")

            # First check if the user exists in the profiles table
            try:
                profile_check = await asyncio.to_thread(
                    lambda: (self.client.table("profiles").select("id").eq("id", user_id).execute())
                )
                if not profile_check.data or len(profile_check.data) == 0:
                    logger.warning(
                        f"User {user_id} not found in profiles table - attempting to create profile"
                    )
                    # Try to create a profile for this user
                    await self._ensure_user_profile_exists(user_id)
                    # Check again after creation attempt
                    profile_check = await asyncio.to_thread(
                        lambda: (
                            self.client.table("profiles").select("id").eq("id", user_id).execute()
                        )
                    )

                logger.info(
                    f"Profile check result: {profile_check.data if profile_check.data else 'No data'}"
                )
            except Exception as profile_check_error:
                logger.warning(
                    f"Failed to check profiles table for user {user_id}: {profile_check_error}"
                )

            # Try to get profile from the view first
            try:
                logger.info(f"Querying {USER_PROFILE_VIEW} for user {user_id}")
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
                    logger.info(f"Profile data keys: {list(response.data.keys())}")
                    # Check if user preferences are present
                    preference_fields = [
                        "style_preferences",
                        "size_info",
                        "travel_patterns",
                        "quick_reply_preferences",
                        "packing_methods",
                        "currency_preferences",
                    ]
                    for field in preference_fields:
                        if field in response.data:
                            logger.info(f"Found preference field '{field}': {response.data[field]}")
                        else:
                            logger.warning(f"Missing preference field '{field}' in profile data")
                    return response.data
                else:
                    logger.warning(f"No profile data found for user {user_id} in view")
                    # Log additional response info for debugging
                    if hasattr(response, "error") and response.error:
                        logger.warning(f"Response error: {response.error}")
                    if hasattr(response, "status") and response.status:
                        logger.warning(f"Response status: {response.status}")
            except Exception as view_error:
                logger.warning(f"Failed to get profile from view for user {user_id}: {view_error}")
                # Log more details about the view error
                if hasattr(view_error, "response") and view_error.response:
                    logger.warning(
                        f"View error response status: {getattr(view_error.response, 'status_code', 'N/A')}"
                    )
                    logger.warning(
                        f"View error response text: {getattr(view_error.response, 'text', 'N/A')}"
                    )
                # Log the specific error details for debugging
                if hasattr(view_error, "message"):
                    logger.warning(f"View error message: {view_error.message}")
                if hasattr(view_error, "details"):
                    logger.warning(f"View error details: {view_error.details}")
                if hasattr(view_error, "code"):
                    logger.warning(f"View error code: {view_error.code}")
                if hasattr(view_error, "hint"):
                    logger.warning(f"View error hint: {view_error.hint}")

            # Fallback to basic profile data if view fails
            try:
                logger.info("Attempting fallback to basic profile data")
                basic_profile = await asyncio.to_thread(
                    lambda: (
                        self.client.table("profiles")
                        .select("*")
                        .eq("id", user_id)
                        .single()
                        .execute()
                    )
                )
                if basic_profile.data:
                    logger.info(f"Retrieved basic profile for user {user_id} via fallback")
                    logger.info(f"Basic profile data keys: {list(basic_profile.data.keys())}")

                    # Try to manually fetch user preferences if they're not in the basic profile
                    try:
                        logger.info("Attempting to manually fetch user preferences")
                        preferences_response = await asyncio.to_thread(
                            lambda: (
                                self.client.table("user_preferences")
                                .select("*")
                                .eq("user_id", user_id)
                                .single()
                                .execute()
                            )
                        )

                        if preferences_response.data:
                            logger.info(f"Retrieved user preferences: {preferences_response.data}")
                            # Merge preferences with basic profile
                            basic_profile.data.update(preferences_response.data)
                            logger.info(
                                f"Updated profile with preferences, final keys: {list(basic_profile.data.keys())}"
                            )
                        else:
                            logger.info("No user preferences found, will use defaults")
                            # Add default preference fields
                            default_preferences = {
                                "style_preferences": {},
                                "size_info": {},
                                "travel_patterns": {},
                                "quick_reply_preferences": {"enabled": True},
                                "packing_methods": {},
                                "currency_preferences": {},
                            }
                            basic_profile.data.update(default_preferences)
                            logger.info("Added default preferences to profile")
                    except Exception as pref_error:
                        logger.warning(f"Failed to fetch user preferences manually: {pref_error}")
                        # Add default preference fields as fallback
                        default_preferences = {
                            "style_preferences": {},
                            "size_info": {},
                            "travel_patterns": {},
                            "quick_reply_preferences": {"enabled": True},
                            "packing_methods": {},
                            "currency_preferences": {},
                        }
                        basic_profile.data.update(default_preferences)
                        logger.info("Added default preferences to profile after error")

                    return basic_profile.data
                else:
                    logger.warning(f"No basic profile data found for user {user_id}")
                    return None
            except Exception as fallback_error:
                logger.error(f"Fallback profile retrieval also failed: {fallback_error}")
                return None

        except APIError as api_e:
            # Handle specific Supabase API errors
            logger.error(
                "Supabase API error getting complete user profile for %s: %s - %s",
                user_id,
                type(api_e).__name__,
                str(api_e),
            )
            if hasattr(api_e, "response") and api_e.response:
                logger.error(
                    f"API Response status: {getattr(api_e.response, 'status_code', 'N/A')}"
                )
                logger.error(f"API Response text: {getattr(api_e.response, 'text', 'N/A')}")
            if hasattr(api_e, "message"):
                logger.error(f"API Error message: {api_e.message}")
            if hasattr(api_e, "details"):
                logger.error(f"API Error details: {api_e.details}")
            if hasattr(api_e, "hint"):
                logger.error(f"API Error hint: {api_e.hint}")
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Failed to get complete user profile for %s: %s - %s",
                user_id,
                type(e).__name__,
                str(e),
            )
            # Log additional context for debugging
            if hasattr(e, "__cause__") and e.__cause__:
                logger.error("Caused by: %s - %s", type(e.__cause__).__name__, str(e.__cause__))

            # Log additional Supabase-specific error details
            if hasattr(e, "response") and e.response:
                logger.error(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
                logger.error(f"Response text: {getattr(e.response, 'text', 'N/A')}")
            if hasattr(e, "message"):
                logger.error(f"Error message: {e.message}")
            if hasattr(e, "details"):
                logger.error(f"Error details: {e.details}")
            if hasattr(e, "hint"):
                logger.error(f"Error hint: {e.hint}")

            return None

    async def _ensure_user_profile_exists(self, user_id: str) -> bool:
        """Ensure that a user profile exists in the profiles table."""
        try:
            # Try to get user data from auth.users (requires admin privileges)
            auth_user = await asyncio.to_thread(
                lambda: self.client.auth.admin.get_user_by_id(user_id)
            )

            if not auth_user.user:
                logger.error(f"User {user_id} not found in auth.users")
                return False

            # Create profile record
            profile_data = {
                "id": user_id,
                "email": auth_user.user.email,
                "first_name": auth_user.user.user_metadata.get("first_name")
                if auth_user.user.user_metadata
                else None,
                "last_name": auth_user.user.user_metadata.get("last_name")
                if auth_user.user.user_metadata
                else None,
                "profile_completed": bool(
                    auth_user.user.user_metadata
                    and auth_user.user.user_metadata.get("first_name")
                    and auth_user.user.user_metadata.get("last_name")
                ),
                "created_at": auth_user.user.created_at,
                "updated_at": auth_user.user.updated_at,
            }

            await asyncio.to_thread(
                lambda: self.client.table("profiles").insert(profile_data).execute()
            )

            # Create user preferences record
            await asyncio.to_thread(
                lambda: self.client.table(USER_PREFERENCES_TABLE)
                .insert(
                    {
                        "user_id": user_id,
                        "style_preferences": {},
                        "size_info": {},
                        "travel_patterns": {},
                        "quick_reply_preferences": {"enabled": True},
                        "packing_methods": {},
                        "currency_preferences": {},
                    }
                )
                .execute()
            )

            logger.info(f"Created profile and preferences for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create profile for user {user_id}: {e}")
            return False

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
            logger.error(
                "Failed to update user profile for %s: %s - %s", user_id, type(e).__name__, str(e)
            )
            if hasattr(e, "__cause__") and e.__cause__:
                logger.error("Caused by: %s - %s", type(e.__cause__).__name__, str(e.__cause__))
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
            logger.error(
                "Failed to update user profile for %s: %s - %s", user_id, type(e).__name__, str(e)
            )
            if hasattr(e, "__cause__") and e.__cause__:
                logger.error("Caused by: %s - %s", type(e.__cause__).__name__, str(e.__cause__))
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
