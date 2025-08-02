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
Base service class for Supabase operations.
Provides common functionality for all Supabase-related services.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from supabase import Client

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

T = TypeVar("T")


class SupabaseBaseService(ABC, Generic[T]):
    """Base class for Supabase services with common operations."""

    def __init__(self, table_name: str, client: Client = None):
        """Initialize the service with a table name."""
        self.table_name = table_name
        self.client: Client = client if client is not None else get_supabase_client()

    async def _execute_query(self, query_func) -> list[dict[str, Any]] | None:
        """Execute a Supabase query with error handling."""
        try:
            response = await asyncio.to_thread(query_func)
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error executing query on {self.table_name}: {e}")
            return None

    async def get_by_id(self, record_id: str) -> T | None:
        """Get a record by ID."""
        query_func = lambda: (
            self.client.table(self.table_name).select("*").eq("id", record_id).limit(1).execute()
        )
        result = await self._execute_query(query_func)
        return self._parse_record(result[0]) if result else None

    async def get_by_field(self, field: str, value: Any) -> list[T]:
        """Get records by a specific field value."""
        query_func = lambda: (
            self.client.table(self.table_name).select("*").eq(field, value).execute()
        )
        result = await self._execute_query(query_func)
        return [self._parse_record(record) for record in result]

    async def get_all(self, limit: int | None = None) -> list[T]:
        """Get all records with optional limit."""
        query_func = lambda: (
            self.client.table(self.table_name).select("*").limit(limit or 1000).execute()
        )
        result = await self._execute_query(query_func)
        return [self._parse_record(record) for record in result]

    async def create(self, data: dict[str, Any]) -> T | None:
        """Create a new record."""
        try:
            response = await asyncio.to_thread(
                lambda: self.client.table(self.table_name).insert(data).execute()
            )
            if response.data:
                return self._parse_record(response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error creating record in {self.table_name}: {e}")
            return None

    async def update(self, record_id: str, data: dict[str, Any]) -> T | None:
        """Update a record by ID."""
        try:
            response = await asyncio.to_thread(
                lambda: (
                    self.client.table(self.table_name).update(data).eq("id", record_id).execute()
                )
            )
            if response.data:
                return self._parse_record(response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating record in {self.table_name}: {e}")
            return None

    async def delete(self, record_id: str) -> bool:
        """Delete a record by ID."""
        try:
            await asyncio.to_thread(
                lambda: (self.client.table(self.table_name).delete().eq("id", record_id).execute())
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting record from {self.table_name}: {e}")
            return False

    async def upsert(self, data: dict[str, Any], unique_fields: list[str]) -> T | None:
        """Upsert a record based on unique fields."""
        try:
            response = await asyncio.to_thread(
                lambda: self.client.table(self.table_name).upsert(data).execute()
            )
            if response.data:
                return self._parse_record(response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error upserting record in {self.table_name}: {e}")
            return None

    @abstractmethod
    def _parse_record(self, record: dict[str, Any]) -> T:
        """Parse a database record into the appropriate model."""
        pass

    def _validate_connection(self) -> bool:
        """Validate that the Supabase connection is working."""
        try:
            # Simple test query
            self.client.table(self.table_name).select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection validation failed: {e}")
            return False
