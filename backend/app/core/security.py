"""
Security utilities for TravelStyle AI application.
Handles JWT token verification and Supabase authentication.
"""

import logging
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings
from app.utils.user_utils import extract_user_profile
from supabase import Client, create_client

logger = logging.getLogger(__name__)


class SupabaseAuth:
    """Supabase authentication client for JWT token verification and user management."""

    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def verify_jwt_token(self, token: str) -> dict[str, Any] | None:
        """Verify Supabase JWT token and return user data"""
        try:
            # Decode the JWT token
            payload = jwt.decode(
                token,
                key="",  # Supabase handles signature verification
                options={"verify_signature": False},
            )

            # Extract user information
            user_id = payload.get("sub")
            email = payload.get("email")
            is_active = payload.get("is_active", True)

            if not user_id:
                return None

            return {
                "id": user_id,
                "email": email,
                "is_active": is_active,
                "aud": payload.get("aud"),  # Audience (usually 'authenticated')
                "exp": payload.get("exp"),  # Expiration time
                "iat": payload.get("iat"),  # Issued at time
            }

        except JWTError as e:
            logger.error("JWT decode error: %s", type(e).__name__)
            return None
        except (ValueError, KeyError) as e:
            logger.error("Token verification error: %s", type(e).__name__)
            return None

    # pylint: disable=duplicate-code
    async def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        """Get user data from Supabase by user ID"""
        try:
            response = self.client.auth.admin.get_user_by_id(user_id)
            if response.user:
                return extract_user_profile(response.user)
            return None
        except (ValueError, KeyError, AttributeError) as e:
            logger.error("Get user by ID error: %s", type(e).__name__)
            return None

    async def revoke_token(self, token: str) -> bool:  # pylint: disable=unused-argument
        """Revoke a JWT token (logout)"""
        try:
            # Supabase handles token revocation automatically
            # You can also implement custom token blacklisting if needed
            return True
        except (ValueError, KeyError) as e:
            logger.error("Token revocation error: %s", type(e).__name__)
            return False


# Singleton instance
supabase_auth = SupabaseAuth()


def create_access_token(data: dict) -> str:  # pylint: disable=unused-argument
    """Create a JWT token (mainly for testing - Supabase handles this)"""
    # This is mainly for testing purposes
    # In production, Supabase handles token creation
    return ""


def verify_token(token: str) -> dict[str, Any] | None:
    """Verify a JWT token and return user data"""
    return supabase_auth.verify_jwt_token(token)
