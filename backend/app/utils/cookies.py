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
Cookie management utilities for secure authentication.
Handles setting, reading, and clearing HttpOnly cookies.
"""

import logging
from datetime import UTC, datetime, timedelta

from fastapi import Response

logger = logging.getLogger(__name__)

# Cookie names
ACCESS_TOKEN_COOKIE = "access"  # nosec B105
REFRESH_TOKEN_COOKIE = "refresh"  # nosec B105

# Token TTLs (in seconds)
ACCESS_TOKEN_TTL = 10 * 60  # 10 minutes
REFRESH_TOKEN_TTL = 60 * 24 * 60 * 60  # 60 days


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    access_ttl: int = ACCESS_TOKEN_TTL,
    refresh_ttl: int = REFRESH_TOKEN_TTL,
    secure: bool = True,
    same_site: str = "Strict",
) -> None:
    """
    Set secure HttpOnly cookies for access and refresh tokens.

    Args:
        response: FastAPI Response object
        access_token: JWT access token
        refresh_token: Refresh token
        access_ttl: Access token TTL in seconds (default: 10 minutes)
        refresh_ttl: Refresh token TTL in seconds (default: 60 days)
        secure: Whether to set Secure flag (default: True, use False for local dev)
        same_site: SameSite attribute (default: "Strict")
    """
    # Set access token cookie
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=access_ttl,
        httponly=True,
        secure=secure,
        samesite=same_site,
        path="/",
    )

    # Set refresh token cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=refresh_ttl,
        httponly=True,
        secure=secure,
        samesite=same_site,
        path="/",
    )

    logger.debug("Auth cookies set successfully")


def clear_auth_cookies(response: Response) -> None:
    """
    Clear authentication cookies by setting them to expire.

    Args:
        response: FastAPI Response object
    """
    # Clear access token cookie
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value="",
        max_age=0,
        httponly=True,
        secure=True,
        samesite="Strict",
        path="/",
        expires=datetime.now(UTC) - timedelta(days=1),
    )

    # Clear refresh token cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value="",
        max_age=0,
        httponly=True,
        secure=True,
        samesite="Strict",
        path="/",
        expires=datetime.now(UTC) - timedelta(days=1),
    )

    logger.debug("Auth cookies cleared successfully")


def get_access_token_from_cookie(request) -> str | None:
    """
    Extract access token from cookie.

    Args:
        request: FastAPI Request object

    Returns:
        Access token string or None if not found
    """
    return request.cookies.get(ACCESS_TOKEN_COOKIE)


def get_refresh_token_from_cookie(request) -> str | None:
    """
    Extract refresh token from cookie.

    Args:
        request: FastAPI Request object

    Returns:
        Refresh token string or None if not found
    """
    return request.cookies.get(REFRESH_TOKEN_COOKIE)
