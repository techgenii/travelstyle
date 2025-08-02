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
Rate limiter for database operations in TravelStyle AI application.
Prevents overwhelming the database with too many requests.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class DatabaseRateLimiter:
    """Rate limiter for database operations to prevent overwhelming the database."""

    def __init__(self, max_requests_per_second: int = 100, max_requests_per_minute: int = 1000):
        """
        Initialize the rate limiter.

        Args:
            max_requests_per_second: Maximum requests per second
            max_requests_per_minute: Maximum requests per minute
        """
        self.max_requests_per_second = max_requests_per_second
        self.max_requests_per_minute = max_requests_per_minute

        # Track requests by operation type
        self.requests_per_second: dict[str, deque[float]] = defaultdict(deque)
        self.requests_per_minute: dict[str, deque[float]] = defaultdict(deque)

        # Lock for thread safety
        self._lock = asyncio.Lock()

    async def acquire(self, operation_type: str = "default") -> bool:
        """
        Check if a database operation can proceed based on rate limits.

        Args:
            operation_type: Type of operation (e.g., 'read', 'write', 'cache')

        Returns:
            True if operation can proceed, False if rate limited
        """
        async with self._lock:
            current_time = time.time()

            # Clean old entries
            self._clean_old_entries(operation_type, current_time)

            # Check rate limits
            if len(self.requests_per_second[operation_type]) >= self.max_requests_per_second:
                logger.warning(f"Rate limit exceeded for {operation_type} operations per second")
                return False

            if len(self.requests_per_minute[operation_type]) >= self.max_requests_per_minute:
                logger.warning(f"Rate limit exceeded for {operation_type} operations per minute")
                return False

            # Record the request
            self.requests_per_second[operation_type].append(current_time)
            self.requests_per_minute[operation_type].append(current_time)

            return True

    def _clean_old_entries(self, operation_type: str, current_time: float) -> None:
        """Remove old entries from the tracking queues."""
        # Clean per-second entries older than 1 second
        while (
            self.requests_per_second[operation_type]
            and current_time - self.requests_per_second[operation_type][0] >= 1.0
        ):
            self.requests_per_second[operation_type].popleft()

        # Clean per-minute entries older than 60 seconds
        while (
            self.requests_per_minute[operation_type]
            and current_time - self.requests_per_minute[operation_type][0] >= 60.0
        ):
            self.requests_per_minute[operation_type].popleft()

    async def wait_if_needed(
        self, operation_type: str = "default", max_wait_time: float = 5.0
    ) -> bool:
        """
        Wait if rate limited, up to a maximum wait time.

        Args:
            operation_type: Type of operation
            max_wait_time: Maximum time to wait in seconds

        Returns:
            True if operation can proceed after waiting, False if still rate limited
        """
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            if await self.acquire(operation_type):
                return True

            # Wait a bit before trying again
            await asyncio.sleep(0.1)

        logger.error(
            f"Rate limit exceeded for {operation_type} operations after waiting {max_wait_time}s"
        )
        return False

    def get_stats(self) -> dict[str, dict[str, int]]:
        """Get current rate limiting statistics."""
        stats = {}
        for operation_type in set(self.requests_per_second.keys()) | set(
            self.requests_per_minute.keys()
        ):
            stats[operation_type] = {
                "requests_per_second": len(self.requests_per_second[operation_type]),
                "requests_per_minute": len(self.requests_per_minute[operation_type]),
            }
        return stats


# Global rate limiter instance
db_rate_limiter = DatabaseRateLimiter()


async def rate_limited_operation(operation_type: str = "default", max_wait_time: float = 5.0):
    """
    Decorator for rate-limited database operations.

    Args:
        operation_type: Type of operation
        max_wait_time: Maximum time to wait in seconds
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            if await db_rate_limiter.wait_if_needed(operation_type, max_wait_time):
                return await func(*args, **kwargs)
            else:
                raise Exception(f"Rate limit exceeded for {operation_type} operations")

        return wrapper

    return decorator
