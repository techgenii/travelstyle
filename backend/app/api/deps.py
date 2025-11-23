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
Dependency injection utilities for TravelStyle AI application.
Provides authentication and user management dependencies.
"""

import logging

from fastapi import Depends, HTTPException, Request, status

from app.core.security import supabase_auth
from app.utils.cookies import get_access_token_from_cookie, get_refresh_token_from_cookie

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> dict:
    """
    Validate Supabase JWT token from cookie and return current user.

    Optionally attempts to refresh token if access token is expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to get access token from cookie
    access_token = get_access_token_from_cookie(request)

    if not access_token:
        raise credentials_exception

    try:
        # Verify the JWT token
        user_data = supabase_auth.verify_jwt_token(access_token)

        if not user_data:
            # Token might be expired, try to refresh
            refresh_token = get_refresh_token_from_cookie(request)
            if refresh_token:
                # Optionally auto-refresh here, or let client handle it
                # For now, raise exception and let client call /refresh
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired. Please refresh.",
                )
            raise credentials_exception

        return user_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication error: %s", type(e).__name__)
        raise credentials_exception from e


current_user_dependency = Depends(get_current_user)


async def get_current_active_user(current_user: dict = current_user_dependency) -> dict:
    """
    Ensure user is active
    """
    if not current_user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
