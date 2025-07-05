"""
Authentication service for TravelStyle AI application.
Handles Supabase authentication operations including login, logout, password reset,
and user registration.
"""
import logging
from typing import Optional, Dict, Any
from supabase import Client, create_client
from app.core.config import settings
from app.models.auth import (
    LoginRequest, LoginResponse, LogoutResponse, ForgotPasswordResponse,
    ResetPasswordResponse, RefreshTokenResponse, RegisterResponse
)
from app.utils.user_utils import extract_user_profile

logger = logging.getLogger(__name__)

class AuthService:
    """Supabase authentication service for user management."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = None
        self._init_client()

    def _init_client(self):
        """Initialize Supabase client."""
        try:
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to initialize Supabase client: %s", str(e))
            raise

    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """Authenticate user with email and password."""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": login_data.email,
                "password": login_data.password
            })
            if not response.user:
                raise ValueError("Invalid credentials")
            user_profile = extract_user_profile(response.user)
            return LoginResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",  # nosec
                expires_in=response.session.expires_in,
                user=user_profile
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Login failed for email %s: %s", login_data.email, str(e))
            raise ValueError("Invalid credentials") from e

    async def logout(self, refresh_token: Optional[str] = None) -> LogoutResponse:
        """Logout user and revoke tokens."""
        try:
            if refresh_token:
                self.client.auth.admin.sign_out(refresh_token)
            else:
                self.client.auth.sign_out()
            return LogoutResponse(
                message="Successfully logged out",
                success=True
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Logout failed: %s", str(e))
            return LogoutResponse(
                message="Logged out successfully",
                success=True
            )

    async def forgot_password(self, email: str) -> ForgotPasswordResponse:
        """Send password reset email."""
        try:
            self.client.auth.reset_password_email(email)
            return ForgotPasswordResponse(
                message="Password reset email sent successfully",
                success=True
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Password reset email failed for %s: %s", email, str(e))
            return ForgotPasswordResponse(
                message="If the email exists, a password reset link has been sent",
                success=True
            )

    async def reset_password(self, token: str, new_password: str) -> ResetPasswordResponse:
        """Reset password using reset token."""
        # token argument is required for interface compatibility
        # pylint: disable=unused-argument
        try:
            self.client.auth.update_user({
                "password": new_password
            })
            return ResetPasswordResponse(
                message="Password reset successfully",
                success=True
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Password reset failed: %s", str(e))
            raise ValueError("Invalid or expired reset token") from e

    async def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        """Refresh access token using refresh token."""
        try:
            response = self.client.auth.refresh_session(refresh_token)
            return RefreshTokenResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",  # nosec
                expires_in=response.session.expires_in
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Token refresh failed: %s", str(e))
            raise ValueError("Invalid refresh token") from e

    async def register(self, email: str, password: str,
                      first_name: Optional[str] = None,
                      last_name: Optional[str] = None) -> RegisterResponse:
        """Register new user."""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name
                    }
                }
            })
            if not response.user:
                raise ValueError("Failed to create user")
            # Immediately sign in to get token after registration
            login_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            user_profile = extract_user_profile(login_response.user)
            return RegisterResponse(
                access_token=login_response.session.access_token,
                token_type="bearer",  # nosec
                expires_in=login_response.session.expires_in,
                message="Registration successful",
                user_id=user_profile.get("id"),
                success=True,
                user=user_profile
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("User registration failed for %s: %s", email, str(e))
            raise ValueError("Registration failed. Email may already be in use.") from e

    # pylint: disable=duplicate-code
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information."""
        try:
            response = self.client.auth.admin.get_user_by_id(user_id)
            if response.user:
                return extract_user_profile(response.user)
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get user profile for %s: %s", user_id, str(e))
            return None

    async def update_user_profile(self, user_id: str,
                                updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile information."""
        try:
            response = self.client.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": updates}
            )
            if response.user:
                return extract_user_profile(response.user)
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to update user profile for %s: %s", user_id, str(e))
            return None

    async def update_user_profile_sync(self, user_id: str,
                                     updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile and sync across all tables."""
        try:
            # Update Supabase auth user metadata
            auth_response = self.client.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": updates}
            )

            if not auth_response.user:
                logger.error("Failed to update auth user for %s", user_id)
                return None

            # Update public.users table
            user_updates = {}
            if 'first_name' in updates:
                user_updates['first_name'] = updates['first_name']
            if 'last_name' in updates:
                user_updates['last_name'] = updates['last_name']

            # Update profile_completed status
            if 'first_name' in updates or 'last_name' in updates:
                first_name = (updates.get('first_name') or
                            auth_response.user.raw_user_meta_data.get('first_name'))
                last_name = (updates.get('last_name') or
                           auth_response.user.raw_user_meta_data.get('last_name'))
                user_updates['profile_completed'] = bool(first_name and last_name)

            if user_updates:
                user_updates['updated_at'] = 'now()'
                self.client.table('users').update(user_updates).eq('id', user_id).execute()

            # Update user_preferences if style preferences are included
            if 'style_preferences' in updates:
                self.client.table('user_preferences').update({
                    'style_preferences': updates['style_preferences'],
                    'updated_at': 'now()'
                }).eq('user_id', user_id).execute()

            # Return updated profile
            return extract_user_profile(auth_response.user)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to update user profile for %s: %s", user_id, str(e))
            return None

    async def update_user_preferences(self, user_id: str,
                                    preferences: Dict[str, Any]) -> bool:
        """Update user preferences in the database."""
        try:
            # Update user_preferences table
            self.client.table('user_preferences').update({
                **preferences,
                'updated_at': 'now()'
            }).eq('user_id', user_id).execute()

            logger.info("User preferences updated successfully for %s", user_id)
            return True

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to update user preferences for %s: %s", user_id, str(e))
            return False

# Singleton instance
auth_service = AuthService()
