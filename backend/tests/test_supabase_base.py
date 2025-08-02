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

"""Tests for SupabaseBaseService."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from app.services.supabase import SupabaseBaseService


class MockRecord:
    """Mock record for testing."""

    def __init__(self, data: dict):
        self.data = data


class TestSupabaseBaseService(SupabaseBaseService[MockRecord]):
    """Test implementation of SupabaseBaseService."""

    def _parse_record(self, record: dict) -> MockRecord:
        """Parse a database record into MockRecord."""
        return MockRecord(record)


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    mock_client = MagicMock()
    with patch(
        "app.services.supabase.supabase_client.get_supabase_client", return_value=mock_client
    ):
        yield mock_client


@pytest.fixture
def base_service(mock_supabase_client):
    """Create a test instance of SupabaseBaseService."""
    return TestSupabaseBaseService("test_table", client=mock_supabase_client)


class TestSupabaseBaseServiceInitialization:
    """Test SupabaseBaseService initialization."""

    def test_init(self, mock_supabase_client):
        """Test service initialization."""
        service = TestSupabaseBaseService("test_table", client=mock_supabase_client)
        assert service.table_name == "test_table"
        assert service.client == mock_supabase_client


class TestSupabaseBaseServiceExecuteQuery:
    """Test _execute_query method."""

    @pytest.mark.asyncio
    async def test_execute_query_success(self, base_service):
        """Test successful query execution."""
        mock_response = Mock()
        mock_response.data = [{"id": "1", "name": "test"}]

        query_func = Mock(return_value=mock_response)

        result = await base_service._execute_query(query_func)

        assert result == [{"id": "1", "name": "test"}]
        query_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_no_data(self, base_service):
        """Test query execution with no data."""
        mock_response = Mock()
        mock_response.data = None

        query_func = Mock(return_value=mock_response)

        result = await base_service._execute_query(query_func)

        assert result == []
        query_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_exception(self, base_service):
        """Test query execution with exception."""
        query_func = Mock(side_effect=Exception("Database error"))

        result = await base_service._execute_query(query_func)

        assert result is None
        query_func.assert_called_once()


class TestSupabaseBaseServiceGetById:
    """Test get_by_id method."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, base_service, mock_supabase_client):
        """Test successful get by ID."""
        mock_response = Mock()
        mock_response.data = [{"id": "1", "name": "test"}]

        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_limit = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.limit.return_value = mock_limit
        mock_limit.execute.return_value = mock_response

        result = await base_service.get_by_id("1")

        assert result is not None
        assert result.data["id"] == "1"
        assert result.data["name"] == "test"

    @pytest.mark.asyncio
    async def test_get_by_id_no_result(self, base_service, mock_supabase_client):
        """Test get by ID with no result."""
        mock_response = Mock()
        mock_response.data = []

        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_limit = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.limit.return_value = mock_limit
        mock_limit.execute.return_value = mock_response

        result = await base_service.get_by_id("1")

        assert result is None


class TestSupabaseBaseServiceGetByField:
    """Test get_by_field method."""

    @pytest.mark.asyncio
    async def test_get_by_field_success(self, base_service, mock_supabase_client):
        """Test successful get by field."""
        mock_response = Mock()
        mock_response.data = [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}]

        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response

        result = await base_service.get_by_field("name", "test")

        assert len(result) == 2
        assert result[0].data["id"] == "1"
        assert result[1].data["id"] == "2"

    @pytest.mark.asyncio
    async def test_get_by_field_no_results(self, base_service, mock_supabase_client):
        """Test get by field with no results."""
        mock_response = Mock()
        mock_response.data = []

        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response

        result = await base_service.get_by_field("name", "nonexistent")

        assert result == []


class TestSupabaseBaseServiceGetAll:
    """Test get_all method."""

    @pytest.mark.asyncio
    async def test_get_all_with_limit(self, base_service, mock_supabase_client):
        """Test get all with limit."""
        mock_response = Mock()
        mock_response.data = [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}]

        mock_table = Mock()
        mock_select = Mock()
        mock_limit = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.limit.return_value = mock_limit
        mock_limit.execute.return_value = mock_response

        result = await base_service.get_all(limit=10)

        assert len(result) == 2
        assert result[0].data["id"] == "1"
        assert result[1].data["id"] == "2"

    @pytest.mark.asyncio
    async def test_get_all_default_limit(self, base_service, mock_supabase_client):
        """Test get all with default limit."""
        mock_response = Mock()
        mock_response.data = [{"id": "1", "name": "test"}]

        mock_table = Mock()
        mock_select = Mock()
        mock_limit = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.limit.return_value = mock_limit
        mock_limit.execute.return_value = mock_response

        result = await base_service.get_all()

        assert len(result) == 1
        assert result[0].data["id"] == "1"


class TestSupabaseBaseServiceCreate:
    """Test create method."""

    @pytest.mark.asyncio
    async def test_create_success(self, base_service, mock_supabase_client):
        """Test successful record creation."""
        mock_response = Mock()
        mock_response.data = [{"id": "1", "name": "new_test"}]

        mock_table = Mock()
        mock_insert = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_response

        data = {"name": "new_test"}
        result = await base_service.create(data)

        assert result is not None
        assert result.data["id"] == "1"
        assert result.data["name"] == "new_test"

    @pytest.mark.asyncio
    async def test_create_no_data_returned(self, base_service, mock_supabase_client):
        """Test create with no data returned."""
        mock_response = Mock()
        mock_response.data = []

        mock_table = Mock()
        mock_insert = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_response

        data = {"name": "new_test"}
        result = await base_service.create(data)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_exception(self, base_service, mock_supabase_client):
        """Test create with exception."""
        mock_table = Mock()
        mock_insert = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.side_effect = Exception("Database error")

        data = {"name": "new_test"}
        result = await base_service.create(data)

        assert result is None


class TestSupabaseBaseServiceUpdate:
    """Test update method."""

    @pytest.mark.asyncio
    async def test_update_success(self, base_service, mock_supabase_client):
        """Test successful record update."""
        mock_response = Mock()
        mock_response.data = [{"id": "1", "name": "updated_test"}]

        mock_table = Mock()
        mock_update = Mock()
        mock_eq = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.update.return_value = mock_update
        mock_update.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response

        data = {"name": "updated_test"}
        result = await base_service.update("1", data)

        assert result is not None
        assert result.data["id"] == "1"
        assert result.data["name"] == "updated_test"

    @pytest.mark.asyncio
    async def test_update_no_data_returned(self, base_service, mock_supabase_client):
        """Test update with no data returned."""
        mock_response = Mock()
        mock_response.data = []

        mock_table = Mock()
        mock_update = Mock()
        mock_eq = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.update.return_value = mock_update
        mock_update.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response

        data = {"name": "updated_test"}
        result = await base_service.update("1", data)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_exception(self, base_service, mock_supabase_client):
        """Test update with exception."""
        mock_table = Mock()
        mock_update = Mock()
        mock_eq = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.update.return_value = mock_update
        mock_update.eq.return_value = mock_eq
        mock_eq.execute.side_effect = Exception("Database error")

        data = {"name": "updated_test"}
        result = await base_service.update("1", data)

        assert result is None


class TestSupabaseBaseServiceDelete:
    """Test delete method."""

    @pytest.mark.asyncio
    async def test_delete_success(self, base_service, mock_supabase_client):
        """Test successful record deletion."""
        mock_table = Mock()
        mock_delete = Mock()
        mock_eq = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.delete.return_value = mock_delete
        mock_delete.eq.return_value = mock_eq
        mock_eq.execute.return_value = Mock()

        result = await base_service.delete("1")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_exception(self, base_service, mock_supabase_client):
        """Test delete with exception."""
        mock_table = Mock()
        mock_delete = Mock()
        mock_eq = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.delete.return_value = mock_delete
        mock_delete.eq.return_value = mock_eq
        mock_eq.execute.side_effect = Exception("Database error")

        result = await base_service.delete("1")

        assert result is False


class TestSupabaseBaseServiceUpsert:
    """Test upsert method."""

    @pytest.mark.asyncio
    async def test_upsert_success_new_record(self, base_service, mock_supabase_client):
        """Test successful record upsert for new record."""
        mock_response = Mock()
        mock_response.data = [{"id": "1", "name": "upserted_test"}]

        mock_table = Mock()
        mock_select = Mock()
        mock_match = Mock()
        mock_insert = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.match.return_value = mock_match
        mock_match.execute.return_value = Mock(data=[])  # No existing record
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_response

        data = {"id": "1", "name": "upserted_test"}
        result = await base_service.upsert(data, ["id"])

        assert result is not None
        assert result.data["id"] == "1"
        assert result.data["name"] == "upserted_test"

    @pytest.mark.asyncio
    async def test_upsert_success_existing_record(self, base_service, mock_supabase_client):
        """Test successful record upsert for existing record."""
        mock_response = Mock()
        mock_response.data = [{"id": "1", "name": "updated_test"}]

        mock_table = Mock()
        mock_select = Mock()
        mock_match = Mock()
        mock_update = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.match.return_value = mock_match
        mock_match.execute.return_value = Mock(
            data=[{"id": "1", "name": "old_test"}]
        )  # Existing record
        mock_table.update.return_value = mock_update
        mock_update.eq.return_value = mock_update
        mock_update.execute.return_value = mock_response

        data = {"id": "1", "name": "updated_test"}
        result = await base_service.upsert(data, ["id"])

        assert result is not None
        assert result.data["id"] == "1"
        assert result.data["name"] == "updated_test"

    @pytest.mark.asyncio
    async def test_upsert_no_data_returned(self, base_service, mock_supabase_client):
        """Test upsert with no data returned."""
        mock_response = Mock()
        mock_response.data = []

        mock_table = Mock()
        mock_select = Mock()
        mock_match = Mock()
        mock_insert = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.match.return_value = mock_match
        mock_match.execute.return_value = Mock(data=[])  # No existing record
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_response

        data = {"id": "1", "name": "upserted_test"}
        result = await base_service.upsert(data, ["id"])

        assert result is None

    @pytest.mark.asyncio
    async def test_upsert_exception(self, base_service, mock_supabase_client):
        """Test upsert with exception."""
        mock_table = Mock()
        mock_upsert = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.side_effect = Exception("Database error")

        data = {"id": "1", "name": "upserted_test"}
        result = await base_service.upsert(data, ["id"])

        assert result is None


class TestSupabaseBaseServiceValidateConnection:
    """Test _validate_connection method."""

    def test_validate_connection_success(self, base_service, mock_supabase_client):
        """Test successful connection validation."""
        mock_table = Mock()
        mock_select = Mock()
        mock_limit = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.limit.return_value = mock_limit
        mock_limit.execute.return_value = Mock()

        result = base_service._validate_connection()

        assert result is True

    def test_validate_connection_failure(self, base_service, mock_supabase_client):
        """Test connection validation failure."""
        mock_table = Mock()
        mock_select = Mock()
        mock_limit = Mock()

        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.limit.return_value = mock_limit
        mock_limit.execute.side_effect = Exception("Connection failed")

        result = base_service._validate_connection()

        assert result is False


class TestSupabaseBaseServiceParseRecord:
    """Test _parse_record abstract method."""

    def test_parse_record_implementation(self, base_service):
        """Test that _parse_record is implemented in concrete class."""
        record_data = {"id": "1", "name": "test"}
        result = base_service._parse_record(record_data)

        assert isinstance(result, MockRecord)
        assert result.data == record_data

    def test_abstract_method_cannot_be_instantiated(self):
        """Test that abstract class cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SupabaseBaseService("test_table")
