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
"""

import logging
from typing import Any

from app.core.config import settings
from app.models.auth import (
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshTokenResponse,
    RegisterResponse,
    ResetPasswordResponse,
)
from app.utils.user_utils import extract_user_profile
from supabase import Client, create_client

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
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to initialize Supabase client: %s", type(e).__name__)
            raise

    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """Authenticate user with email and password."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": login_data.email, "password": login_data.password}
            )
            if not response.user:
                raise ValueError("Invalid credentials")
            if not response.session:
                raise ValueError("No session created")
            user_profile = extract_user_profile(response.user)
            if not user_profile:
                user_profile = {}
            return LoginResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",  # nosec
                expires_in=response.session.expires_in,
                user=user_profile,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Login failed for email %s: %s", login_data.email, type(e).__name__)
            raise ValueError("Invalid credentials") from e

    async def logout(self, refresh_token: str | None = None) -> LogoutResponse:
        """Logout user and revoke tokens."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            if refresh_token:
                self.client.auth.admin.sign_out(refresh_token)
            else:
                self.client.auth.sign_out()
            return LogoutResponse(message="Successfully logged out", success=True)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Logout failed: %s", type(e).__name__)
            return LogoutResponse(message="Logged out successfully", success=True)

    async def forgot_password(self, email: str) -> ForgotPasswordResponse:
        """Send password reset email."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            self.client.auth.reset_password_email(email)
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
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            self.client.auth.update_user({"password": new_password})
            return ResetPasswordResponse(message="Password reset successfully", success=True)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Password reset failed: %s", type(e).__name__)
            raise ValueError("Invalid or expired reset token") from e

    async def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        """Refresh access token using refresh token."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            response = self.client.auth.refresh_session(refresh_token)
            if not response.session:
                raise ValueError("No session created")
            return RefreshTokenResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",  # nosec
                expires_in=response.session.expires_in,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Token refresh failed: %s", type(e).__name__)
            raise ValueError("Invalid refresh token") from e

    async def register(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> RegisterResponse:
        """Register new user."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            response = self.client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "first_name": first_name,
                            "last_name": last_name,
                        }
                    },
                }
            )
            if not response.user:
                raise ValueError("Failed to create user")
            # Immediately sign in to get token after registration
            login_response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if not login_response.session:
                raise ValueError("No session created after registration")
            user_profile = extract_user_profile(login_response.user)
            if not user_profile:
                user_profile = {}
            return RegisterResponse(
                access_token=login_response.session.access_token,
                token_type="bearer",  # nosec
                expires_in=login_response.session.expires_in,
                message="Registration successful",
                user_id=user_profile.get("id", ""),
                success=True,
                user=user_profile,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("User registration failed: %s", type(e).__name__)
            raise ValueError("Registration failed. Email may already be in use.") from e

    # pylint: disable=duplicate-code
    async def get_user_profile(self, user_id: str) -> dict[str, Any] | None:
        """Get user profile information from user_profile_view."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            # Use the user_profile_view instead of auth admin
            response = (
                self.client.table("user_profile_view").select("*").eq("id", user_id).execute()
            )
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get user profile for %s: %s", user_id, type(e).__name__)
            return None

    async def update_user_profile(
        self, user_id: str, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update user profile information."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            response = self.client.auth.admin.update_user_by_id(user_id, {"user_metadata": updates})
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
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            # Update Supabase auth user metadata
            auth_response = self.client.auth.admin.update_user_by_id(
                user_id, {"user_metadata": updates}
            )

            if not auth_response.user:
                logger.error("Failed to update auth user for %s", user_id)
                return None

            # Update profile_completed status if name fields are being updated
            if "first_name" in updates or "last_name" in updates:
                first_name = updates.get("first_name") or auth_response.user.user_metadata.get(
                    "first_name"
                )
                last_name = updates.get("last_name") or auth_response.user.user_metadata.get(
                    "last_name"
                )
                updates["profile_completed"] = bool(first_name and last_name)

            # Update the view directly - triggers will handle updating underlying tables
            response = (
                self.client.table("user_profile_view").update(updates).eq("id", user_id).execute()
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
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        try:
            # Update user_preferences table
            self.client.table("user_preferences").update({**preferences, "updated_at": "now()"}).eq(
                "user_id", user_id
            ).execute()

            logger.info("User preferences updated successfully for %s", user_id)
            return True

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to update user preferences for %s: %s", user_id, type(e).__name__)
            return False


# Singleton instance
auth_service = AuthService()
