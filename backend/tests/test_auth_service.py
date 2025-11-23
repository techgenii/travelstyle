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

from unittest.mock import MagicMock, Mock, patch

import pytest
from app.models.auth import LoginRequest
from app.services.auth.exceptions import AuthenticationError
from app.services.auth_service import AuthService


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    with patch("app.services.auth.helpers.get_supabase_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def auth_service(mock_supabase_client):  # noqa: ARG001
    """Create AuthService instance for testing."""
    from app.services.auth_service import AuthService

    return AuthService()


@patch(
    "app.utils.user_utils.extract_user_profile",
    return_value={"id": "user-1", "email": "test@example.com"},
)
@pytest.mark.asyncio
async def test_login_success(mock_extract, auth_service):
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"  # Set the user ID
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock the database table operations for user_profile_view
    mock_table = MagicMock()
    mock_response = MagicMock()
    mock_response.data = {
        "id": "user-1",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    login_data = LoginRequest(email="test@example.com", password="password")
    result = await auth_service.login(login_data)
    assert result.access_token == "token"
    assert result.user["id"] == "user-1"


@pytest.mark.asyncio
async def test_login_invalid_credentials(auth_service):
    mock_auth = Mock()
    mock_auth.sign_in_with_password.return_value = Mock(user=None, session=None)
    auth_service.client.auth = mock_auth
    login_data = LoginRequest(email="bad@example.com", password="badpassword")
    with pytest.raises(AuthenticationError):
        await auth_service.login(login_data)


@pytest.mark.asyncio
async def test_login_no_session(auth_service):
    mock_auth = Mock()
    mock_auth.sign_in_with_password.return_value = Mock(user=Mock(), session=None)
    auth_service.client.auth = mock_auth
    login_data = LoginRequest(email="test@example.com", password="password")
    with pytest.raises(AuthenticationError):
        await auth_service.login(login_data)


@pytest.mark.asyncio
async def test_login_exception(auth_service):
    mock_auth = Mock()
    mock_auth.sign_in_with_password.side_effect = Exception("fail")
    auth_service.client.auth = mock_auth
    login_data = LoginRequest(email="test@example.com", password="password")
    with pytest.raises(AuthenticationError):
        await auth_service.login(login_data)


@pytest.mark.asyncio
async def test_logout_success(auth_service):
    mock_auth = Mock()
    mock_admin = Mock()
    mock_auth.admin = mock_admin
    auth_service.client.auth = mock_auth
    result = await auth_service.logout()
    assert result.success is True


@pytest.mark.asyncio
async def test_logout_with_refresh_token(auth_service):
    mock_auth = Mock()
    mock_admin = Mock()
    mock_auth.admin = mock_admin
    auth_service.client.auth = mock_auth
    result = await auth_service.logout(refresh_token="refresh")
    assert result.success is True


@pytest.mark.asyncio
async def test_logout_exception(auth_service):
    mock_auth = Mock()
    mock_auth.sign_out.side_effect = Exception("fail")
    auth_service.client.auth = mock_auth
    result = await auth_service.logout()
    assert result.success is True


@pytest.mark.asyncio
async def test_forgot_password_success(auth_service):
    mock_auth = Mock()
    mock_auth.reset_password_email.return_value = None
    auth_service.client.auth = mock_auth
    result = await auth_service.forgot_password("test@example.com")
    assert result.success is True


@pytest.mark.asyncio
async def test_forgot_password_exception_original(auth_service):
    mock_auth = Mock()
    mock_auth.reset_password_email.side_effect = Exception("fail")
    auth_service.client.auth = mock_auth
    result = await auth_service.forgot_password("test@example.com")
    assert result.success is True


@pytest.mark.asyncio
async def test_reset_password_success(auth_service):
    mock_auth = Mock()
    mock_auth.update_user.return_value = None
    auth_service.client.auth = mock_auth
    result = await auth_service.reset_password("token", "newpass")
    assert result.success is True


@pytest.mark.asyncio
async def test_reset_password_exception_original(auth_service):
    mock_auth = Mock()
    mock_auth.update_user.side_effect = Exception("fail")
    auth_service.client.auth = mock_auth
    from app.services.auth.exceptions import TokenError

    with pytest.raises(TokenError):
        await auth_service.reset_password("token", "newpass")


@pytest.mark.asyncio
async def test_refresh_token_success(auth_service):
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_auth.refresh_session.return_value = Mock(session=mock_session)
    auth_service.client.auth = mock_auth
    result = await auth_service.refresh_token("refresh")
    assert result.access_token == "token"


@pytest.mark.asyncio
async def test_refresh_token_no_session_original(auth_service):
    mock_auth = Mock()
    mock_auth.refresh_session.return_value = Mock(session=None)
    auth_service.client.auth = mock_auth
    from app.services.auth.exceptions import TokenError

    with pytest.raises(TokenError):
        await auth_service.refresh_token("refresh")


@pytest.mark.asyncio
async def test_register_success(auth_service):
    mock_auth = Mock()
    mock_user = Mock()
    mock_user.id = "user-1"  # Set the user ID properly
    mock_session = Mock(access_token="token", expires_in=3600)
    mock_auth.sign_up.return_value = Mock(user=mock_user)
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock the database table operations for user_profile_view
    mock_table = MagicMock()
    mock_response = MagicMock()
    mock_response.data = {
        "id": "user-1",
        "email": "test@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    # Create a proper mock user profile that returns actual values
    mock_user_profile = {"id": "user-1", "email": "test@example.com"}

    # Patch the extract_user_profile function to return our mock profile
    with patch(
        "app.services.auth.helpers.extract_user_profile",
        return_value=mock_user_profile,
    ):
        result = await auth_service.register("test@example.com", "password", "Jane", "Doe")
        assert result.access_token == "token"
        assert result.user["id"] == "user-1"
        assert result.user_id == "user-1"
        assert result.success is True


@pytest.mark.asyncio
async def test_register_no_session(auth_service):
    mock_auth = Mock()
    mock_user = Mock()
    mock_auth.sign_up.return_value = Mock(user=mock_user)
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=None)
    auth_service.client.auth = mock_auth
    from app.services.auth.exceptions import RegistrationError

    with pytest.raises(RegistrationError):
        await auth_service.register("test@example.com", "password")


@patch(
    "app.utils.user_utils.extract_user_profile",
    return_value={"id": "user-1", "email": "test@example.com"},
)
@pytest.mark.asyncio
async def test_get_user_profile_success(mock_extract, auth_service):
    """Test get_user_profile success with view-based approach."""
    mock_response = MagicMock()
    mock_response.data = [{"id": "user-1", "email": "test@example.com"}]

    mock_table = MagicMock()
    mock_table.select.return_value.eq.return_value.execute.return_value = mock_response

    with patch.object(auth_service.client, "table", return_value=mock_table):
        result = await auth_service.get_user_profile("user-1")
        assert result["id"] == "user-1"


@patch(
    "app.utils.user_utils.extract_user_profile",
    return_value={"id": "user-1", "email": "test@example.com"},
)
@pytest.mark.asyncio
async def test_update_user_profile_success(mock_extract, auth_service):
    mock_admin = Mock()
    mock_user = Mock()
    mock_user.id = "user-1"  # Set the user ID properly
    mock_admin.update_user_by_id.return_value = Mock(user=mock_user)
    auth_service.client.auth.admin = mock_admin
    result = await auth_service.update_user_profile("user-1", {"first_name": "Jane"})
    assert result["id"] == "user-1"


@pytest.mark.asyncio
async def test_update_user_profile_sync_success(auth_service):
    mock_admin = Mock()
    mock_admin.update_user_by_id.return_value = Mock(
        user=Mock(), user_metadata={"first_name": "Jane", "last_name": "Doe"}
    )

    # Mock the view update response
    mock_view_response = Mock()
    mock_view_response.data = [
        {"id": "user-1", "email": "test@example.com", "first_name": "Jane", "last_name": "Doe"}
    ]

    mock_table = Mock()
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = mock_view_response

    auth_service.client.auth.admin = mock_admin
    auth_service.client.table = Mock(return_value=mock_table)

    result = await auth_service.update_user_profile_sync(
        "user-1", {"first_name": "Jane", "last_name": "Doe"}
    )
    assert result["id"] == "user-1"


@pytest.mark.asyncio
async def test_update_user_profile_sync_no_user(auth_service):
    mock_admin = Mock()
    mock_admin.update_user_by_id.return_value = Mock(user=None, user_metadata={})
    auth_service.client.auth.admin = mock_admin
    result = await auth_service.update_user_profile_sync("user-1", {"first_name": "Jane"})
    assert result is None


@pytest.mark.asyncio
async def test_update_user_preferences_success(auth_service):
    mock_table = Mock()
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = None
    auth_service.client.table = Mock(return_value=mock_table)
    result = await auth_service.update_user_preferences(
        "user-1", {"style_preferences": {"color": "blue"}}
    )
    assert result is True


@pytest.mark.asyncio
async def test_auth_service_init_client_failure():
    """Test AuthService initialization when Supabase client creation fails."""
    from app.services.supabase import SupabaseClientManager

    # Reset the singleton first
    SupabaseClientManager.reset_client()

    with patch(
        "app.services.supabase.SupabaseClientManager._create_client",
        side_effect=Exception("Connection failed"),
    ):
        with pytest.raises(Exception):  # noqa: B017
            from app.services.auth_service import AuthService

            AuthService()


@pytest.mark.asyncio
async def test_login_no_user_profile(auth_service):
    """Test login when extract_user_profile returns None."""
    mock_response = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "user-1"  # Set the user ID properly
    mock_response.user = mock_user
    mock_response.session = MagicMock()
    mock_response.session.access_token = "access_token"
    mock_response.session.refresh_token = "refresh_token"
    mock_response.session.expires_in = 3600

    # Mock the database table operations for user_profile_view
    mock_table = MagicMock()
    mock_db_response = MagicMock()
    mock_db_response.data = {
        "id": "user-1",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_db_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    with patch("app.services.auth.helpers.extract_user_profile", return_value=None):
        with patch.object(
            auth_service.client.auth, "sign_in_with_password", return_value=mock_response
        ):
            result = await auth_service.login(
                LoginRequest(email="test@example.com", password="password")
            )
            # The service should return the profile data from the database when extract_user_profile returns None
            assert result.user["id"] == "user-1"
            assert result.user["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_logout_with_refresh_token_exception(auth_service):
    """Test logout with refresh token when Supabase raises an exception."""
    with patch.object(
        auth_service.client.auth.admin, "sign_out", side_effect=Exception("Logout error")
    ):
        result = await auth_service.logout(refresh_token="refresh_token")
        assert result.success is True
        assert "Logged out successfully" in result.message


@pytest.mark.asyncio
async def test_logout_without_refresh_token_exception(auth_service):
    """Test logout without refresh token when Supabase raises an exception."""
    with patch.object(auth_service.client.auth, "sign_out", side_effect=Exception("Logout error")):
        result = await auth_service.logout()
        assert result.success is True
        assert "Logged out successfully" in result.message


@pytest.mark.asyncio
async def test_forgot_password_exception(auth_service):
    """Test forgot_password when Supabase raises an exception."""
    with patch.object(
        auth_service.client.auth, "reset_password_email", side_effect=Exception("Email error")
    ):
        result = await auth_service.forgot_password("test@example.com")
        assert result.success is True
        assert "If the email exists" in result.message


@pytest.mark.asyncio
async def test_reset_password_exception(auth_service):
    """Test reset_password when Supabase raises an exception."""
    with patch.object(
        auth_service.client.auth, "update_user", side_effect=Exception("Update error")
    ):
        from app.services.auth.exceptions import TokenError

        with pytest.raises(TokenError, match="Invalid or expired reset token"):
            await auth_service.reset_password("token", "new_password")


@pytest.mark.asyncio
async def test_refresh_token_no_session(auth_service):
    """Test refresh_token when no session is created."""
    mock_response = MagicMock()
    mock_response.session = None

    with patch.object(auth_service.client.auth, "refresh_session", return_value=mock_response):
        from app.services.auth.exceptions import TokenError

        with pytest.raises(TokenError, match="Invalid refresh token"):
            await auth_service.refresh_token("refresh_token")


@pytest.mark.asyncio
async def test_refresh_token_exception(auth_service):
    """Test refresh_token when Supabase raises an exception."""
    with patch.object(
        auth_service.client.auth, "refresh_session", side_effect=Exception("Refresh error")
    ):
        from app.services.auth.exceptions import TokenError

        with pytest.raises(TokenError, match="Invalid refresh token"):
            await auth_service.refresh_token("refresh_token")


@pytest.mark.asyncio
async def test_register_no_user(auth_service):
    """Test register when no user is created."""
    mock_response = MagicMock()
    mock_response.user = None

    with patch.object(auth_service.client.auth, "sign_up", return_value=mock_response):
        from app.services.auth.exceptions import RegistrationError

        with pytest.raises(RegistrationError, match="Registration failed"):
            await auth_service.register("test@example.com", "password")


@pytest.mark.asyncio
async def test_register_no_session_after_login(auth_service):
    """Test register when no session is created after login."""
    mock_signup_response = MagicMock()
    mock_signup_response.user = MagicMock()

    mock_login_response = MagicMock()
    mock_login_response.session = None

    with (
        patch.object(auth_service.client.auth, "sign_up", return_value=mock_signup_response),
        patch.object(
            auth_service.client.auth, "sign_in_with_password", return_value=mock_login_response
        ),
    ):
        from app.services.auth.exceptions import RegistrationError

        with pytest.raises(RegistrationError, match="Registration failed"):
            await auth_service.register("test@example.com", "password")


@pytest.mark.asyncio
async def test_register_exception(auth_service):
    """Test register when Supabase raises an exception."""
    with patch.object(
        auth_service.client.auth, "sign_up", side_effect=Exception("Registration error")
    ):
        from app.services.auth.exceptions import RegistrationError

        with pytest.raises(RegistrationError, match="Registration failed"):
            await auth_service.register("test@example.com", "password")


@pytest.mark.asyncio
async def test_register_weak_password_error(auth_service):
    """Test register when Supabase raises AuthWeakPasswordError."""

    # Create a mock exception with the weak password error type name
    class AuthWeakPasswordError(Exception):
        """Mock AuthWeakPasswordError exception."""

        pass

    with patch.object(
        auth_service.client.auth,
        "sign_up",
        side_effect=AuthWeakPasswordError("Password is too weak"),
    ):
        from app.services.auth.constants import WEAK_PASSWORD_MSG
        from app.services.auth.exceptions import RegistrationError

        with pytest.raises(RegistrationError, match=WEAK_PASSWORD_MSG):
            # Use a password that passes local validation (6+ chars) but Supabase rejects
            await auth_service.register("test@example.com", "password123")


@pytest.mark.asyncio
async def test_register_weak_password_error_by_message(auth_service):
    """Test register when error message contains 'weak password'."""
    with patch.object(
        auth_service.client.auth, "sign_up", side_effect=Exception("Password is too weak")
    ):
        from app.services.auth.constants import WEAK_PASSWORD_MSG
        from app.services.auth.exceptions import RegistrationError

        with pytest.raises(RegistrationError, match=WEAK_PASSWORD_MSG):
            # Use a password that passes local validation (6+ chars) but Supabase rejects
            await auth_service.register("test@example.com", "password123")


@pytest.mark.asyncio
async def test_register_email_already_in_use(auth_service):
    """Test register when email is already in use."""
    with patch.object(
        auth_service.client.auth, "sign_up", side_effect=Exception("Email already exists")
    ):
        from app.services.auth.constants import EMAIL_ALREADY_IN_USE_MSG
        from app.services.auth.exceptions import RegistrationError

        with pytest.raises(RegistrationError, match=EMAIL_ALREADY_IN_USE_MSG):
            await auth_service.register("existing@example.com", "password")


@pytest.mark.asyncio
async def test_register_email_already_taken(auth_service):
    """Test register when email is already taken (different wording)."""
    with patch.object(
        auth_service.client.auth, "sign_up", side_effect=Exception("Email is already taken")
    ):
        from app.services.auth.constants import EMAIL_ALREADY_IN_USE_MSG
        from app.services.auth.exceptions import RegistrationError

        with pytest.raises(RegistrationError, match=EMAIL_ALREADY_IN_USE_MSG):
            await auth_service.register("existing@example.com", "password")


@pytest.mark.asyncio
async def test_get_user_profile_no_user(auth_service):
    """Test get_user_profile when no user is returned."""
    mock_response = MagicMock()
    mock_response.data = []

    mock_table = MagicMock()
    mock_table.select.return_value.eq.return_value.execute.return_value = mock_response

    with patch.object(auth_service.client, "table", return_value=mock_table):
        result = await auth_service.get_user_profile("user_id")
        assert result is None


@pytest.mark.asyncio
async def test_get_user_profile_exception(auth_service):
    """Test get_user_profile when Supabase raises an exception."""
    mock_table = MagicMock()
    mock_table.select.return_value.eq.return_value.execute.side_effect = Exception("Profile error")

    with patch.object(auth_service.client, "table", return_value=mock_table):
        result = await auth_service.get_user_profile("user_id")
        assert result is None


@pytest.mark.asyncio
async def test_update_user_profile_no_user(auth_service):
    """Test update_user_profile when no user is returned."""
    mock_response = MagicMock()
    mock_response.user = None

    with patch.object(
        auth_service.client.auth.admin, "update_user_by_id", return_value=mock_response
    ):
        result = await auth_service.update_user_profile("user_id", {"first_name": "John"})
        assert result is None


@pytest.mark.asyncio
async def test_update_user_profile_exception(auth_service):
    """Test update_user_profile when Supabase raises an exception."""
    with patch.object(
        auth_service.client.auth.admin, "update_user_by_id", side_effect=Exception("Update error")
    ):
        result = await auth_service.update_user_profile("user_id", {"first_name": "John"})
        assert result is None


@pytest.mark.asyncio
async def test_update_user_profile_sync_no_auth_user(auth_service):
    """Test update_user_profile_sync when auth update fails."""
    mock_response = MagicMock()
    mock_response.user = None

    with patch.object(
        auth_service.client.auth.admin, "update_user_by_id", return_value=mock_response
    ):
        result = await auth_service.update_user_profile_sync("user_id", {"first_name": "John"})
        assert result is None


@pytest.mark.asyncio
async def test_update_user_profile_sync_with_style_preferences(auth_service):
    """Test update_user_profile_sync with style preferences."""
    mock_auth_response = MagicMock()
    mock_auth_response.user = MagicMock()
    mock_auth_response.user.user_metadata = {"first_name": "John", "last_name": "Doe"}

    # Mock the view update response
    mock_view_response = MagicMock()
    mock_view_response.data = [
        {
            "id": "user_id",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "style_preferences": {"color": "blue"},
        }
    ]

    mock_table = MagicMock()
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = mock_view_response

    with (
        patch.object(
            auth_service.client.auth.admin, "update_user_by_id", return_value=mock_auth_response
        ),
        patch.object(auth_service.client, "table", return_value=mock_table),
    ):
        result = await auth_service.update_user_profile_sync(
            "user_id",
            {"first_name": "John", "last_name": "Doe", "style_preferences": {"color": "blue"}},
        )
        assert result is not None


@pytest.mark.asyncio
async def test_update_user_profile_sync_exception(auth_service):
    """Test update_user_profile_sync when Supabase raises an exception."""
    with patch.object(
        auth_service.client.auth.admin, "update_user_by_id", side_effect=Exception("Sync error")
    ):
        result = await auth_service.update_user_profile_sync("user_id", {"first_name": "John"})
        assert result is None


@pytest.mark.asyncio
async def test_update_user_preferences_exception(auth_service):
    """Test update_user_preferences when Supabase raises an exception."""
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.side_effect = Exception(
        "Preferences error"
    )

    with patch.object(auth_service.client, "table", return_value=mock_table):
        result = await auth_service.update_user_preferences("user_id", {"theme": "dark"})
        assert result is False


@pytest.mark.asyncio
async def test_auth_service_no_client():
    """Test AuthService methods when client is not initialized."""
    from app.services.auth.exceptions import ClientInitializationError

    # Create a new instance without initializing the client
    service = AuthService.__new__(AuthService)
    service.client = None

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.login(LoginRequest(email="test@example.com", password="password"))

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.logout()

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.forgot_password("test@example.com")

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.reset_password("token", "new_password")

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.refresh_token("refresh_token")

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.register("test@example.com", "password")

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.get_user_profile("user_id")

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.update_user_profile("user_id", {})

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.update_user_profile_sync("user_id", {})

    with pytest.raises(ClientInitializationError, match="Supabase client not initialized"):
        await service.update_user_preferences("user_id", {})
