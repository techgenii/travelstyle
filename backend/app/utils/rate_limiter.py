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
Rate limiting utilities for TravelStyle AI application.
Provides centralized rate limiting configuration and implementation.
"""

import logging
import time
from functools import wraps

import jwt
from fastapi import HTTPException, Request
from jwt import PyJWTError as JWTError

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMITS = {
    "chat": (30, 60),  # 30 calls per minute
    "currency": (15, 60),  # 15 calls per minute
    "currency_rates": (10, 60),  # 10 calls per minute
    "currency_convert": (15, 60),  # 15 calls per minute
    "currency_pair": (10, 60),  # 10 calls per minute
    "cultural_insights": (20, 60),  # 20 calls per minute
    "weather": (30, 60),  # 30 calls per minute
    "default": (50, 60),  # 50 calls per minute
}

# In-memory rate limit storage (use Redis in production)
rate_limit_storage: dict[str, tuple[int, float]] = {}


def get_rate_limit_config(endpoint_type: str) -> tuple[int, int]:
    """
    Get rate limit configuration for an endpoint type.

    Args:
        endpoint_type: The type of endpoint (e.g., 'chat', 'currency')

    Returns:
        Tuple of (calls, period) for rate limiting
    """
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])


def rate_limit(calls: int = None, period: int = None, endpoint_type: str = None):
    """
    Rate limiting decorator with centralized configuration.

    Args:
        calls: Number of allowed calls (overrides endpoint_type if provided)
        period: Time period in seconds (overrides endpoint_type if provided)
        endpoint_type: Type of endpoint to use predefined limits
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Use endpoint_type configuration if provided
            if endpoint_type and (calls is None or period is None):
                config_calls, config_period = get_rate_limit_config(endpoint_type)
                actual_calls = calls if calls is not None else config_calls
                actual_period = period if period is not None else config_period
            else:
                actual_calls = calls or RATE_LIMITS["default"][0]
                actual_period = period or RATE_LIMITS["default"][1]

            # Extract request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # If no request object found, skip rate limiting
                return await func(*args, **kwargs)

            # Get client identifier (IP address or user ID)
            client_id = request.client.host if request.client else "unknown"

            # Check if user is authenticated and use user ID instead
            auth_header = request.headers.get("authorization")
            if auth_header:
                try:
                    token = auth_header.replace("Bearer ", "")
                    payload = jwt.decode(
                        token,
                        key="",  # Supabase handles signature verification
                        options={"verify_signature": False},
                    )
                    client_id = payload.get("sub", client_id)
                except (JWTError, ValueError, KeyError) as e:
                    logger.debug("JWT decode failed, using IP address: %s", e)
                    # Fall back to IP address

            # Create rate limit key
            rate_limit_key = f"{func.__name__}:{client_id}"

            current_time = time.time()

            # Check if rate limit exists and is still valid
            if rate_limit_key in rate_limit_storage:
                last_call_time, call_count = rate_limit_storage[rate_limit_key]

                # Reset if period has passed
                if current_time - last_call_time > actual_period:
                    rate_limit_storage[rate_limit_key] = (current_time, 1)
                else:
                    # Check if limit exceeded
                    if call_count >= actual_calls:
                        raise HTTPException(
                            status_code=429,
                            detail=(
                                f"Rate limit exceeded. Maximum {actual_calls} calls per "
                                f"{actual_period} seconds."
                            ),
                        )
                    # Increment call count
                    rate_limit_storage[rate_limit_key] = (last_call_time, call_count + 1)
            else:
                # First call
                rate_limit_storage[rate_limit_key] = (current_time, 1)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Convenience decorators for common endpoint types
def chat_rate_limit():
    """Rate limiting for chat endpoints."""
    return rate_limit(endpoint_type="chat")


def currency_rate_limit():
    """Rate limiting for currency conversion endpoints."""
    return rate_limit(endpoint_type="currency")


def currency_rates_limit():
    """Rate limiting for currency rates endpoints."""
    return rate_limit(endpoint_type="currency_rates")


def cultural_insights_limit():
    """Rate limiting for cultural insights endpoints."""
    return rate_limit(endpoint_type="cultural_insights")


def weather_limit():
    """Rate limiting for weather endpoints."""
    return rate_limit(endpoint_type="weather")
