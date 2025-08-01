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
from app.services.auth.exceptions import AuthenticationError, RegistrationError, TokenError
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
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
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
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
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
    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
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
    except RegistrationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e
