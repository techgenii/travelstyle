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
Shared Supabase client with connection pooling for TravelStyle AI application.
Provides a singleton client instance to avoid creating multiple connections.
"""

import logging
import threading
import time

from app.core.config import settings
from supabase import Client, create_client

logger = logging.getLogger(__name__)


class SupabaseConnectionError(Exception):
    """Raised when there's an issue with Supabase connection."""

    pass


class SupabaseClientManager:
    """Manages a singleton Supabase client instance with connection pooling."""

    _instance: Client | None = None
    _lock = threading.Lock()
    _initialized = False
    _last_health_check = 0.0
    _health_check_interval = 300.0  # 5 minutes

    @classmethod
    def get_client(cls) -> Client:
        """Get the singleton Supabase client instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls._create_client()
                    cls._initialized = True
                    logger.info("Supabase client initialized successfully")
        else:
            # Perform periodic health check
            cls._check_connection_health()

        return cls._instance

    @classmethod
    def _create_client(cls) -> Client:
        """Create a new Supabase client instance."""
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise SupabaseConnectionError("Missing Supabase URL or key in configuration")

            client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Supabase client created successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {e}")
            raise SupabaseConnectionError(f"Failed to create Supabase client: {e}") from e

    @classmethod
    def _check_connection_health(cls) -> None:
        """Perform periodic health check on the connection."""
        current_time = time.time()
        if current_time - cls._last_health_check > cls._health_check_interval:
            try:
                # Simple health check - try to access a system table
                cls._instance.table("_supabase_migrations").select("id").limit(1).execute()
                cls._last_health_check = current_time
                logger.debug("Supabase connection health check passed")
            except Exception as e:
                logger.warning(f"Supabase connection health check failed: {e}")
                # Reset the client to force reconnection
                cls.reset_client()

    @classmethod
    def reset_client(cls) -> None:
        """Reset the client instance (useful for testing or reconnection)."""
        with cls._lock:
            cls._instance = None
            cls._initialized = False
            cls._last_health_check = 0.0
            logger.info("Supabase client reset")

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the client has been initialized."""
        return cls._initialized

    @classmethod
    def test_connection(cls) -> bool:
        """Test the current connection to Supabase."""
        try:
            client = cls.get_client()
            # Try a simple query to test the connection
            client.table("_supabase_migrations").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False


def get_supabase_client() -> Client:
    """Get the shared Supabase client instance."""
    return SupabaseClientManager.get_client()


def test_supabase_connection() -> bool:
    """Test the Supabase connection."""
    return SupabaseClientManager.test_connection()


# Export the client for backward compatibility
supabase_client = get_supabase_client()
