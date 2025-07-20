"""
Authentication router for TravelStyle AI application.
Provides endpoints for user authentication, registration, and password management.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.api.deps import get_current_user
from app.models.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.models.user import UserProfileResponse
from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Local dependency to avoid linter warnings
current_user_dependency = Depends(get_current_user)


# pylint: disable=line-too-long
@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(login_data: LoginRequest):
    """
    Authenticate user with email and password.

    Returns JWT access token and refresh token for authenticated requests.
    """
    try:
        response = await auth_service.login(login_data)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(
    logout_data: LogoutRequest | None = None, current_user: dict = current_user_dependency
):
    """
    Logout user and revoke authentication tokens.

    Requires valid JWT token in Authorization header.
    """
    try:
        refresh_token_value = logout_data.refresh_token if logout_data else None
        response = await auth_service.logout(refresh_token_value)
        return response
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Logout error: %s", type(e).__name__)
        return LogoutResponse(message="Logged out successfully", success=True)


@router.post(
    "/forgot-password", response_model=ForgotPasswordResponse, status_code=status.HTTP_200_OK
)
async def forgot_password(forgot_data: ForgotPasswordRequest):
    """
    Send password reset email to user.

    Sends a password reset link to the provided email address.
    """
    try:
        response = await auth_service.forgot_password(forgot_data.email)
        return response
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Forgot password error: %s", type(e).__name__)
        return ForgotPasswordResponse(
            message="If the email exists, a password reset link has been sent", success=True
        )


@router.post(
    "/reset-password", response_model=ResetPasswordResponse, status_code=status.HTTP_200_OK
)
async def reset_password(reset_data: ResetPasswordRequest):
    """
    Reset user password using reset token.

    Updates user password using the token received via email.
    """
    try:
        response = await auth_service.reset_password(reset_data.token, reset_data.new_password)
        logger.info("Password reset successful")
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token"
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token.

    Returns new access token and refresh token pair.
    """
    try:
        response = await auth_service.refresh_token(refresh_data.refresh_token)
        logger.info("Token refreshed successfully")
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},  # pylint: disable=line-too-long
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest):
    """
    Register new user account.

    Creates a new user account and sends email confirmation.
    """
    try:
        response = await auth_service.register(
            email=register_data.email,
            password=register_data.password,
            first_name=register_data.first_name,
            last_name=register_data.last_name,
        )
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def get_current_user_profile(current_user: dict = current_user_dependency):
    """
    Get current user profile information.

    Returns profile data for the authenticated user.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        profile = await auth_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        return profile
    except HTTPException:
        raise
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Get user profile error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e


@router.put("/me", status_code=status.HTTP_200_OK)
async def update_current_user_profile(updates: dict, current_user: dict = current_user_dependency):
    """
    Update current user profile information.

    Updates profile data for the authenticated user.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        # Only allow updating specific fields
        allowed_updates = {
            "first_name": updates.get("first_name"),
            "last_name": updates.get("last_name"),
        }

        # Remove None values
        allowed_updates = {k: v for k, v in allowed_updates.items() if v is not None}

        if not allowed_updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields to update"
            )

        profile = await auth_service.update_user_profile_sync(user_id, allowed_updates)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        return profile
    except HTTPException:
        raise
    except Exception as e:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e


@router.put("/me/preferences", status_code=status.HTTP_200_OK)
async def update_current_user_preferences(
    preferences: dict, current_user: dict = current_user_dependency
):
    """
    Update current user preferences.

    Updates preference data for the authenticated user.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        # Only allow updating specific preference fields
        allowed_preferences = {
            "style_preferences": preferences.get("style_preferences"),
            "size_info": preferences.get("size_info"),
            "travel_patterns": preferences.get("travel_patterns"),
            "quick_reply_preferences": preferences.get("quick_reply_preferences"),
            "packing_methods": preferences.get("packing_methods"),
            "currency_preferences": preferences.get("currency_preferences"),
        }

        # Remove None values
        allowed_preferences = {k: v for k, v in allowed_preferences.items() if v is not None}

        if not allowed_preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid preference fields to update",
            )

        success = await auth_service.update_user_preferences(user_id, allowed_preferences)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user preferences",
            )

        return {"message": "Preferences updated successfully", "success": True}
    except HTTPException:
        raise
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Update user preferences error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e
