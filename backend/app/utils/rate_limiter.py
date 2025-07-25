"""
Rate limiting utilities for the TravelStyle AI application.
Provides decorators and functions for API rate limiting.
"""

import logging
import time
from functools import wraps

from fastapi import HTTPException, Request
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

# In-memory rate limit storage (use Redis in production)
rate_limit_storage: dict[str, tuple[int, float]] = {}


def rate_limit(calls: int, period: int):
    """
    Rate limiting decorator

    Args:
        calls: Number of allowed calls
        period: Time period in seconds
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
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

            # Check current rate limit status
            if rate_limit_key in rate_limit_storage:
                call_count, last_reset = rate_limit_storage[rate_limit_key]

                # Reset counter if period has passed
                if current_time - last_reset > period:
                    rate_limit_storage[rate_limit_key] = (1, current_time)
                else:
                    # Check if limit exceeded
                    if call_count >= calls:
                        reset_time = int(last_reset + period - current_time)
                        raise HTTPException(
                            status_code=429,
                            detail=f"Rate limit exceeded. Try again in {reset_time} seconds.",
                            headers={"Retry-After": str(reset_time)},
                        )

                    # Increment counter
                    rate_limit_storage[rate_limit_key] = (call_count + 1, last_reset)
            else:
                # First call for this client
                rate_limit_storage[rate_limit_key] = (1, current_time)

            # Clean up old entries periodically
            if len(rate_limit_storage) > 10000:  # Arbitrary cleanup threshold
                cleanup_old_entries(current_time, period)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def cleanup_old_entries(current_time: float, max_age: int):
    """Clean up old rate limit entries"""
    keys_to_remove = []

    for key, (_, last_reset) in rate_limit_storage.items():
        if current_time - last_reset > max_age * 2:  # Keep entries for 2x the period
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del rate_limit_storage[key]

    logger.info("Cleaned up %d old rate limit entries", len(keys_to_remove))
