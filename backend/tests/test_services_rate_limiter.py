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

import asyncio
from unittest.mock import patch

import pytest
from app.services.rate_limiter import DatabaseRateLimiter, rate_limited_operation


class TestDatabaseRateLimiter:
    """Test cases for DatabaseRateLimiter class"""

    @pytest.fixture
    def rate_limiter(self):
        """Create a fresh rate limiter instance for each test"""
        return DatabaseRateLimiter(max_requests_per_second=20, max_requests_per_minute=30)

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test rate limiter initialization with default values"""
        limiter = DatabaseRateLimiter()
        assert limiter.max_requests_per_second == 100
        assert limiter.max_requests_per_minute == 1000
        assert len(limiter.requests_per_second) == 0
        assert len(limiter.requests_per_minute) == 0

    @pytest.mark.asyncio
    async def test_initialization_custom_values(self):
        """Test rate limiter initialization with custom values"""
        limiter = DatabaseRateLimiter(max_requests_per_second=50, max_requests_per_minute=500)
        assert limiter.max_requests_per_second == 50
        assert limiter.max_requests_per_minute == 500

    @pytest.mark.asyncio
    async def test_acquire_first_request(self, rate_limiter):
        """Test acquiring permission for the first request"""
        result = await rate_limiter.acquire("read")
        assert result is True
        assert len(rate_limiter.requests_per_second["read"]) == 1
        assert len(rate_limiter.requests_per_minute["read"]) == 1

    @pytest.mark.asyncio
    async def test_acquire_multiple_requests_within_limits(self, rate_limiter):
        """Test multiple requests within rate limits"""
        # Make 20 requests (within per-second limit)
        for i in range(20):
            result = await rate_limiter.acquire("read")
            assert result is True

        assert len(rate_limiter.requests_per_second["read"]) == 20
        assert len(rate_limiter.requests_per_minute["read"]) == 20

    @pytest.mark.asyncio
    async def test_acquire_exceeds_per_second_limit(self, rate_limiter):
        """Test when requests exceed per-second limit"""
        # Make 20 requests (at the limit)
        for i in range(20):
            result = await rate_limiter.acquire("read")
            assert result is True

        # 21st request should be rate limited
        result = await rate_limiter.acquire("read")
        assert result is False

    @pytest.mark.asyncio
    async def test_acquire_exceeds_per_minute_limit(self, rate_limiter):
        """Test when requests exceed per-minute limit"""
        # Mock time to control the test
        with patch("time.time") as mock_time:
            mock_time.return_value = 1000.0

            # Make requests up to the per-second limit
            for i in range(20):
                result = await rate_limiter.acquire("read")
                assert result is True

            # Advance time to clear per-second entries but keep per-minute entries
            mock_time.return_value = 1001.5  # 1.5 seconds later

            # Make more requests to reach per-minute limit
            for i in range(10):
                result = await rate_limiter.acquire("read")
                assert result is True

            # 31st request should be rate limited by per-minute limit
            result = await rate_limiter.acquire("read")
            assert result is False

    @pytest.mark.asyncio
    async def test_acquire_different_operation_types(self, rate_limiter):
        """Test that different operation types are tracked separately"""
        # Make requests for different operation types
        assert await rate_limiter.acquire("read") is True
        assert await rate_limiter.acquire("write") is True
        assert await rate_limiter.acquire("cache") is True

        assert len(rate_limiter.requests_per_second["read"]) == 1
        assert len(rate_limiter.requests_per_second["write"]) == 1
        assert len(rate_limiter.requests_per_second["cache"]) == 1

    @pytest.mark.asyncio
    async def test_clean_old_entries_per_second(self, rate_limiter):
        """Test cleaning of old per-second entries"""
        # Mock time from the start
        with patch("time.time") as mock_time:
            mock_time.return_value = 1000.0

            # Add some requests
            for i in range(3):
                await rate_limiter.acquire("read")

            # Advance time by 2 seconds (beyond 1-second window)
            mock_time.return_value = 1002.0
            result = await rate_limiter.acquire("read")

            # Should be able to acquire again after cleaning old entries
            assert result is True
            assert len(rate_limiter.requests_per_second["read"]) == 1  # Only the new request

    @pytest.mark.asyncio
    async def test_clean_old_entries_per_minute(self, rate_limiter):
        """Test cleaning of old per-minute entries"""
        # Mock time from the start
        with patch("time.time") as mock_time:
            mock_time.return_value = 1000.0

            # Add some requests
            for i in range(3):
                await rate_limiter.acquire("read")

            # Advance time by 70 seconds (beyond 60-second window)
            mock_time.return_value = 1070.0
            result = await rate_limiter.acquire("read")

            # Should be able to acquire again after cleaning old entries
            assert result is True
            assert len(rate_limiter.requests_per_minute["read"]) == 1  # Only the new request

    @pytest.mark.asyncio
    async def test_wait_if_needed_success(self, rate_limiter):
        """Test wait_if_needed when rate limit is not exceeded"""
        result = await rate_limiter.wait_if_needed("read", max_wait_time=1.0)
        assert result is True

    @pytest.mark.asyncio
    async def test_wait_if_needed_rate_limited(self, rate_limiter):
        """Test wait_if_needed when rate limit is exceeded"""
        # Fill up the rate limit
        for i in range(20):
            await rate_limiter.acquire("read")

        # Try to wait for permission (should fail after max_wait_time)
        result = await rate_limiter.wait_if_needed("read", max_wait_time=0.1)
        assert result is False

    @pytest.mark.asyncio
    async def test_wait_if_needed_acquires_after_cleanup(self, rate_limiter):
        """Test wait_if_needed succeeds after old entries are cleaned up"""
        # Fill up the rate limit
        for i in range(5):
            await rate_limiter.acquire("read")

        # Mock time to advance and clean old entries
        with patch("time.time") as mock_time:
            mock_time.return_value = 1002.0  # Use fixed time values
            result = await rate_limiter.wait_if_needed("read", max_wait_time=0.1)

        # Should succeed after cleanup
        assert result is True

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, rate_limiter):
        """Test get_stats when no requests have been made"""
        stats = rate_limiter.get_stats()
        assert stats == {}

    @pytest.mark.asyncio
    async def test_get_stats_with_requests(self, rate_limiter):
        """Test get_stats with some requests made"""
        # Make some requests
        await rate_limiter.acquire("read")
        await rate_limiter.acquire("write")
        await rate_limiter.acquire("read")

        stats = rate_limiter.get_stats()
        assert "read" in stats
        assert "write" in stats
        assert stats["read"]["requests_per_second"] == 2
        assert stats["read"]["requests_per_minute"] == 2
        assert stats["write"]["requests_per_second"] == 1
        assert stats["write"]["requests_per_minute"] == 1

    @pytest.mark.asyncio
    async def test_concurrent_access(self, rate_limiter):
        """Test concurrent access to the rate limiter"""

        async def make_request():
            return await rate_limiter.acquire("read")

        # Make multiple concurrent requests (within limits)
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed (within limits)
        assert all(results)
        assert len(rate_limiter.requests_per_second["read"]) == 10

    @pytest.mark.asyncio
    async def test_default_operation_type(self, rate_limiter):
        """Test using default operation type"""
        result = await rate_limiter.acquire()  # No operation_type specified
        assert result is True
        assert len(rate_limiter.requests_per_second["default"]) == 1
        assert len(rate_limiter.requests_per_minute["default"]) == 1


class TestRateLimitedOperationDecorator:
    """Test cases for the rate_limited_operation decorator"""

    @pytest.fixture
    def mock_rate_limiter(self):
        """Create a mock rate limiter"""
        with patch("app.services.rate_limiter.db_rate_limiter") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_rate_limited_operation_success(self, mock_rate_limiter):
        """Test successful rate-limited operation"""

        async def mock_wait_if_needed(operation_type, max_wait_time):
            return True

        mock_rate_limiter.wait_if_needed = mock_wait_if_needed

        decorator = await rate_limited_operation("read", max_wait_time=1.0)

        @decorator
        async def test_function():
            return "success"

        result = await test_function()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_rate_limited_operation_failure(self, mock_rate_limiter):
        """Test rate-limited operation when rate limit is exceeded"""

        async def mock_wait_if_needed(operation_type, max_wait_time):
            return False

        mock_rate_limiter.wait_if_needed = mock_wait_if_needed

        decorator = await rate_limited_operation("read", max_wait_time=1.0)

        @decorator
        async def test_function():
            return "success"

        with pytest.raises(Exception, match="Rate limit exceeded for read operations"):
            await test_function()

    @pytest.mark.asyncio
    async def test_rate_limited_operation_with_args(self, mock_rate_limiter):
        """Test rate-limited operation with function arguments"""

        async def mock_wait_if_needed(operation_type, max_wait_time):
            return True

        mock_rate_limiter.wait_if_needed = mock_wait_if_needed

        decorator = await rate_limited_operation("write", max_wait_time=2.0)

        @decorator
        async def test_function(arg1, arg2, kwarg=None):
            return f"success: {arg1} {arg2} {kwarg}"

        result = await test_function("hello", "world", kwarg="test")
        assert result == "success: hello world test"

    @pytest.mark.asyncio
    async def test_rate_limited_operation_default_values(self, mock_rate_limiter):
        """Test rate-limited operation with default values"""

        async def mock_wait_if_needed(operation_type, max_wait_time):
            return True

        mock_rate_limiter.wait_if_needed = mock_wait_if_needed

        decorator = await rate_limited_operation()

        @decorator
        async def test_function():
            return "success"

        result = await test_function()
        assert result == "success"


class TestGlobalRateLimiter:
    """Test cases for the global rate limiter instance"""

    @pytest.mark.asyncio
    async def test_global_rate_limiter_instance(self):
        """Test that the global rate limiter instance exists and works"""
        from app.services.rate_limiter import db_rate_limiter

        assert db_rate_limiter is not None
        assert isinstance(db_rate_limiter, DatabaseRateLimiter)
        assert db_rate_limiter.max_requests_per_second == 100
        assert db_rate_limiter.max_requests_per_minute == 1000

    @pytest.mark.asyncio
    async def test_global_rate_limiter_functionality(self):
        """Test basic functionality of the global rate limiter"""
        from app.services.rate_limiter import db_rate_limiter

        # Should be able to acquire initially
        result = await db_rate_limiter.acquire("test")
        assert result is True

        # Stats should show the request
        stats = db_rate_limiter.get_stats()
        assert "test" in stats
        assert stats["test"]["requests_per_second"] == 1
        assert stats["test"]["requests_per_minute"] == 1
