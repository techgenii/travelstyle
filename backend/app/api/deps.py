"""
Dependency injection utilities for TravelStyle AI application.
Provides authentication and user management dependencies.
"""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import supabase_auth

logger = logging.getLogger(__name__)
security = HTTPBearer()
security_dependency = Depends(security)


async def get_current_user(credentials: HTTPAuthorizationCredentials = security_dependency) -> dict:
    """
    Validate Supabase JWT token and return current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify the JWT token using Supabase
        user_data = supabase_auth.verify_jwt_token(credentials.credentials)

        if not user_data:
            raise credentials_exception

        return user_data

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
