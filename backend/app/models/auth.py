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
Authentication-related models for TravelStyle AI application.
Defines Pydantic models for login, logout, and password reset operations.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request model"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class LoginResponse(BaseModel):
    """Login response model"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: dict = Field(..., description="User information")


class LogoutRequest(BaseModel):
    """Logout request model"""

    refresh_token: str | None = Field(None, description="Refresh token to revoke")


class LogoutResponse(BaseModel):
    """Logout response model"""

    message: str = Field(..., description="Logout confirmation message")
    success: bool = Field(..., description="Logout success status")


class ForgotPasswordRequest(BaseModel):
    """Forgot password request model"""

    email: EmailStr = Field(..., description="Email address for password reset")


class ForgotPasswordResponse(BaseModel):
    """Forgot password response model"""

    message: str = Field(..., description="Password reset confirmation message")
    success: bool = Field(..., description="Password reset request success status")


class ResetPasswordRequest(BaseModel):
    """Reset password request model"""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=6, description="New password")


class ResetPasswordResponse(BaseModel):
    """Reset password response model"""

    message: str = Field(..., description="Password reset confirmation message")
    success: bool = Field(..., description="Password reset success status")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""

    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """Refresh token response model"""

    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RegisterRequest(BaseModel):
    """User registration request model"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")
    first_name: str | None = Field(None, description="User first name")
    last_name: str | None = Field(None, description="User last name")


class RegisterResponse(BaseModel):
    """User registration response model"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    message: str = Field(..., description="Registration confirmation message")
    user_id: str = Field(..., description="New user ID")
    success: bool = Field(..., description="Registration success status")
    user: dict = Field(..., description="User information")
