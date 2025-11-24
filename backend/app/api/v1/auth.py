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

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.config import settings
from app.models.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.services.auth.exceptions import AuthenticationError, RegistrationError, TokenError
from app.services.auth_service import auth_service
from app.utils.cookies import (
    clear_auth_cookies,
    get_refresh_token_from_cookie,
    set_auth_cookies,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# pylint: disable=line-too-long
@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(login_data: LoginRequest, request: Request, response: Response):
    """
    Authenticate user with email and password.

    Sets HttpOnly cookies for access and refresh tokens.
    Does not return tokens in response body.
    """
    try:
        login_response, token_pair = await auth_service.login(login_data)

        # Set secure cookies (use HTTPS detection for secure flag)
        set_auth_cookies(
            response=response,
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            access_ttl=token_pair.expires_in,
            secure=request.url.scheme == "https",
            same_site=settings.COOKIE_SAME_SITE,
        )

        return login_response
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
async def logout(request: Request, response: Response):
    """
    Logout user and revoke authentication tokens.

    Clears cookies and optionally revokes refresh token server-side.
    """
    try:
        refresh_token_value = get_refresh_token_from_cookie(request)

        # Revoke token server-side if present
        if refresh_token_value:
            await auth_service.logout(refresh_token_value)

        # Clear cookies
        clear_auth_cookies(response)

        return LogoutResponse(message="Successfully logged out", success=True)
    except Exception as e:  # pylint: disable=broad-except
        # Clear cookies even if logout fails
        clear_auth_cookies(response)
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
async def refresh_token(request: Request, response: Response):
    """
    Refresh access token using refresh token from cookie.

    Rotates both access and refresh tokens.
    """
    try:
        refresh_token_value = get_refresh_token_from_cookie(request)

        if not refresh_token_value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found",
            )

        refresh_response, token_pair = await auth_service.refresh_token(refresh_token_value)

        # Rotate cookies with new tokens (use HTTPS detection for secure flag)
        set_auth_cookies(
            response=response,
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            access_ttl=token_pair.expires_in,
            secure=request.url.scheme == "https",
            same_site=settings.COOKIE_SAME_SITE,
        )

        logger.info("Token refreshed successfully")
        return refresh_response
    except HTTPException:
        # Re-raise HTTPException so FastAPI can handle it properly
        raise
    except TokenError as e:
        # Clear cookies on refresh failure
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},  # pylint: disable=line-too-long
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest, request: Request, response: Response):
    """
    Register new user account.

    Optionally signs in after registration and sets cookies.
    """
    try:
        register_response, token_pair = await auth_service.register(
            email=register_data.email,
            password=register_data.password,
            first_name=register_data.first_name,
            last_name=register_data.last_name,
        )

        # Set secure cookies after registration (use HTTPS detection for secure flag)
        set_auth_cookies(
            response=response,
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            access_ttl=token_pair.expires_in,
            secure=request.url.scheme == "https",
            same_site=settings.COOKIE_SAME_SITE,
        )

        return register_response
    except RegistrationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from e
