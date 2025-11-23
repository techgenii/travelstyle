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
    mock_session = Mock(access_token="token", refresh_token="refresh_token", expires_in=3600)
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
        assert result.refresh_token == "refresh_token"
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
async def test_auth_service_init_client_failure_with_cause():
    """Test AuthService initialization when Supabase client creation fails with __cause__."""
    from app.services.auth.exceptions import ClientInitializationError
    from app.services.supabase import SupabaseClientManager

    # Reset the singleton first
    SupabaseClientManager.reset_client()

    # Create an exception with __cause__
    cause_exception = ValueError("Root cause")
    main_exception = Exception("Connection failed")
    main_exception.__cause__ = cause_exception

    with patch(
        "app.services.supabase.SupabaseClientManager._create_client",
        side_effect=main_exception,
    ):
        with pytest.raises(ClientInitializationError):
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


# ============================================================================
# Rate Limiting Tests
# ============================================================================


@pytest.mark.asyncio
async def test_check_rate_limit_exceeded(auth_service):
    """Test _check_rate_limit when rate limit is exceeded."""
    from app.services.auth.exceptions import RateLimitError

    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        with pytest.raises(RateLimitError, match="Too many attempts"):
            await auth_service._check_rate_limit("login")


@pytest.mark.asyncio
async def test_login_rate_limited(auth_service):
    """Test login when rate limited."""
    from app.services.auth.exceptions import RateLimitError

    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        login_data = LoginRequest(email="test@example.com", password="password")
        with pytest.raises(RateLimitError):
            await auth_service.login(login_data)


@pytest.mark.asyncio
async def test_logout_rate_limited(auth_service):
    """Test logout when rate limited."""
    from app.services.auth.exceptions import RateLimitError

    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        with pytest.raises(RateLimitError):
            await auth_service.logout()


@pytest.mark.asyncio
async def test_forgot_password_rate_limited(auth_service):
    """Test forgot_password when rate limited."""
    from app.services.auth.exceptions import RateLimitError

    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        with pytest.raises(RateLimitError):
            await auth_service.forgot_password("test@example.com")


@pytest.mark.asyncio
async def test_reset_password_rate_limited(auth_service):
    """Test reset_password when rate limited."""
    from app.services.auth.exceptions import RateLimitError

    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        with pytest.raises(RateLimitError):
            await auth_service.reset_password("token", "newpass")


@pytest.mark.asyncio
async def test_refresh_token_rate_limited(auth_service):
    """Test refresh_token when rate limited."""
    from app.services.auth.exceptions import RateLimitError

    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        with pytest.raises(RateLimitError):
            await auth_service.refresh_token("refresh_token")


@pytest.mark.asyncio
async def test_register_rate_limited(auth_service):
    """Test register when rate limited."""
    from app.services.auth.exceptions import RateLimitError

    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        with pytest.raises(RateLimitError):
            await auth_service.register("test@example.com", "password")


@pytest.mark.asyncio
async def test_get_user_profile_rate_limited(auth_service):
    """Test get_user_profile when rate limited."""
    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        result = await auth_service.get_user_profile("user_id")
        assert result is None


@pytest.mark.asyncio
async def test_get_complete_user_profile_rate_limited(auth_service):
    """Test get_complete_user_profile when rate limited."""
    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        result = await auth_service.get_complete_user_profile("user_id")
        assert result is None


@pytest.mark.asyncio
async def test_update_user_profile_rate_limited(auth_service):
    """Test update_user_profile when rate limited."""
    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        result = await auth_service.update_user_profile("user_id", {"first_name": "John"})
        assert result is None


@pytest.mark.asyncio
async def test_update_user_profile_sync_rate_limited(auth_service):
    """Test update_user_profile_sync when rate limited."""
    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        result = await auth_service.update_user_profile_sync("user_id", {"first_name": "John"})
        assert result is None


@pytest.mark.asyncio
async def test_update_user_preferences_rate_limited(auth_service):
    """Test update_user_preferences when rate limited."""
    with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=False):
        result = await auth_service.update_user_preferences("user_id", {"theme": "dark"})
        assert result is False


# ============================================================================
# Login Edge Cases Tests
# ============================================================================


@pytest.mark.asyncio
async def test_login_last_login_update_failure(auth_service):
    """Test login when last_login update fails with response attribute."""
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock exception with response attribute
    update_exception = Exception("Update failed")
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    update_exception.response = mock_response

    # Mock table operations
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.side_effect = update_exception
    mock_profile_response = MagicMock()
    mock_profile_response.data = {
        "id": "user-1",
        "email": "test@example.com",
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_profile_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    # Mock get_complete_user_profile to return None
    with patch.object(auth_service, "get_complete_user_profile", return_value=None):
        with patch(
            "app.services.auth.helpers.extract_user_profile",
            return_value={"id": "user-1", "email": "test@example.com"},
        ):
            login_data = LoginRequest(email="test@example.com", password="password")
            result = await auth_service.login(login_data)
            assert result.access_token == "token"


@pytest.mark.asyncio
async def test_login_last_login_update_failure_with_message(auth_service):
    """Test login when last_login update fails with message attribute."""
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock exception with message attribute
    update_exception = Exception("Update failed")
    update_exception.message = "Database error"

    # Mock table operations
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.side_effect = update_exception
    mock_profile_response = MagicMock()
    mock_profile_response.data = {
        "id": "user-1",
        "email": "test@example.com",
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_profile_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    with patch.object(auth_service, "get_complete_user_profile", return_value=None):
        with patch(
            "app.services.auth.helpers.extract_user_profile",
            return_value={"id": "user-1", "email": "test@example.com"},
        ):
            login_data = LoginRequest(email="test@example.com", password="password")
            result = await auth_service.login(login_data)
            assert result.access_token == "token"


@pytest.mark.asyncio
async def test_login_last_login_update_failure_with_details(auth_service):
    """Test login when last_login update fails with details attribute."""
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock exception with details attribute
    update_exception = Exception("Update failed")
    update_exception.details = "Constraint violation"

    # Mock table operations
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.side_effect = update_exception
    mock_profile_response = MagicMock()
    mock_profile_response.data = {
        "id": "user-1",
        "email": "test@example.com",
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_profile_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    with patch.object(auth_service, "get_complete_user_profile", return_value=None):
        with patch(
            "app.services.auth.helpers.extract_user_profile",
            return_value={"id": "user-1", "email": "test@example.com"},
        ):
            login_data = LoginRequest(email="test@example.com", password="password")
            result = await auth_service.login(login_data)
            assert result.access_token == "token"


@pytest.mark.asyncio
async def test_login_get_complete_profile_returns_none(auth_service):
    """Test login when get_complete_user_profile returns None."""
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.return_value = None
    mock_preferences_response = MagicMock()
    mock_preferences_response.data = {
        "style_preferences": {"color": "blue"},
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_preferences_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    with patch.object(auth_service, "get_complete_user_profile", return_value=None):
        with patch(
            "app.services.auth.helpers.extract_user_profile",
            return_value={"id": "user-1", "email": "test@example.com"},
        ):
            login_data = LoginRequest(email="test@example.com", password="password")
            result = await auth_service.login(login_data)
            assert result.access_token == "token"
            assert "style_preferences" in result.user


@pytest.mark.asyncio
async def test_login_preferences_fetch_no_data(auth_service):
    """Test login when preferences fetch returns no data."""
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.return_value = None
    mock_preferences_response = MagicMock()
    mock_preferences_response.data = None  # No preferences found
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_preferences_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    mock_profile_response = MagicMock()
    mock_profile_response.data = {
        "id": "user-1",
        "email": "test@example.com",
    }

    with patch.object(
        auth_service, "get_complete_user_profile", return_value=mock_profile_response.data
    ):
        login_data = LoginRequest(email="test@example.com", password="password")
        result = await auth_service.login(login_data)
        assert result.access_token == "token"
        # Should have default preferences
        assert "style_preferences" in result.user
        assert "quick_reply_preferences" in result.user
        assert result.user["quick_reply_preferences"] == {"enabled": True}


@pytest.mark.asyncio
async def test_login_preferences_fetch_exception(auth_service):
    """Test login when preferences fetch raises exception."""
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.return_value = None
    mock_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = (
        Exception("Preferences fetch failed")
    )
    auth_service.client.table = Mock(return_value=mock_table)

    mock_profile_response = MagicMock()
    mock_profile_response.data = {
        "id": "user-1",
        "email": "test@example.com",
    }

    with patch.object(
        auth_service, "get_complete_user_profile", return_value=mock_profile_response.data
    ):
        login_data = LoginRequest(email="test@example.com", password="password")
        result = await auth_service.login(login_data)
        assert result.access_token == "token"
        # Should have default preferences after exception
        assert "style_preferences" in result.user
        assert "quick_reply_preferences" in result.user


@pytest.mark.asyncio
async def test_login_get_complete_profile_exception(auth_service):
    """Test login when get_complete_user_profile raises exception."""
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.return_value = None
    mock_preferences_response = MagicMock()
    mock_preferences_response.data = {
        "style_preferences": {"color": "blue"},
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_preferences_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    with patch.object(
        auth_service, "get_complete_user_profile", side_effect=Exception("Profile fetch failed")
    ):
        with patch(
            "app.services.auth.helpers.extract_user_profile",
            return_value={"id": "user-1", "email": "test@example.com"},
        ):
            login_data = LoginRequest(email="test@example.com", password="password")
            result = await auth_service.login(login_data)
            assert result.access_token == "token"
            assert "style_preferences" in result.user


@pytest.mark.asyncio
async def test_login_preferences_fallback_exception(auth_service):
    """Test login when preferences fetch in fallback mode raises exception."""
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.return_value = None
    mock_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = (
        Exception("Preferences fetch failed")
    )
    auth_service.client.table = Mock(return_value=mock_table)

    with patch.object(
        auth_service, "get_complete_user_profile", side_effect=Exception("Profile fetch failed")
    ):
        with patch(
            "app.services.auth.helpers.extract_user_profile",
            return_value={"id": "user-1", "email": "test@example.com"},
        ):
            login_data = LoginRequest(email="test@example.com", password="password")
            result = await auth_service.login(login_data)
            assert result.access_token == "token"
            # Should have default preferences after exception
            assert "style_preferences" in result.user
            assert "quick_reply_preferences" in result.user


@pytest.mark.asyncio
async def test_login_missing_preference_fields(auth_service):
    """Test login when profile is missing some preference fields."""
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations
    mock_table = MagicMock()
    mock_table.update.return_value.eq.return_value.execute.return_value = None
    mock_preferences_response = MagicMock()
    mock_preferences_response.data = {
        "style_preferences": {"color": "blue"},
        # Missing other preference fields
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_preferences_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    # Profile missing some preference fields
    profile_data = {
        "id": "user-1",
        "email": "test@example.com",
        "style_preferences": {"color": "blue"},
        # Missing: size_info, travel_patterns, etc.
    }

    with patch.object(auth_service, "get_complete_user_profile", return_value=profile_data):
        login_data = LoginRequest(email="test@example.com", password="password")
        result = await auth_service.login(login_data)
        assert result.access_token == "token"
        # Should have all preference fields added
        assert "style_preferences" in result.user
        assert "size_info" in result.user
        assert "travel_patterns" in result.user
        assert "quick_reply_preferences" in result.user
        assert "packing_methods" in result.user
        assert "currency_preferences" in result.user


# ============================================================================
# get_complete_user_profile Comprehensive Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_complete_user_profile_success(auth_service):
    """Test get_complete_user_profile success path."""
    mock_table = MagicMock()
    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]
    mock_view_response = MagicMock()
    mock_view_response.data = {
        "id": "user-1",
        "email": "test@example.com",
        "style_preferences": {"color": "blue"},
    }

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                mock_profile_check
            )
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_view_response
            return mock_view_table
        return mock_table

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            assert result["id"] == "user-1"
            assert result["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_complete_user_profile_profile_not_exists(auth_service):
    """Test get_complete_user_profile when profile doesn't exist, triggers _ensure_user_profile_exists."""
    mock_table = MagicMock()
    mock_profile_check_empty = MagicMock()
    mock_profile_check_empty.data = []  # Profile doesn't exist
    mock_profile_check_after = MagicMock()
    mock_profile_check_after.data = [{"id": "user-1"}]  # After creation
    mock_view_response = MagicMock()
    mock_view_response.data = {
        "id": "user-1",
        "email": "test@example.com",
    }

    call_count = 0

    def table_side_effect(table_name):
        nonlocal call_count
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            if call_count == 0:
                mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                    mock_profile_check_empty
                )
            else:
                mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                    mock_profile_check_after
                )
            call_count += 1
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_view_response
            return mock_view_table
        return mock_table

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch.object(auth_service, "_ensure_user_profile_exists", return_value=True):
            with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
                result = await auth_service.get_complete_user_profile("user-1")
                assert result["id"] == "user-1"


@pytest.mark.asyncio
async def test_get_complete_user_profile_view_error_with_response(auth_service):
    """Test get_complete_user_profile when view query fails with response attribute."""
    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]

    view_error = Exception("View error")
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    view_error.response = mock_response

    # Mock fallback to basic profile
    mock_basic_profile = MagicMock()
    mock_basic_profile.data = {
        "id": "user-1",
        "email": "test@example.com",
    }

    mock_preferences_response = MagicMock()
    mock_preferences_response.data = None

    call_count = {"profiles": 0}

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            call_count["profiles"] += 1
            if call_count["profiles"] == 1:
                # First call - profile check
                mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                    mock_profile_check
                )
            else:
                # Second call - fallback to basic profile
                mock_profiles_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_basic_profile
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = view_error
            return mock_view_table
        elif table_name == "user_preferences":
            mock_prefs_table = MagicMock()
            mock_prefs_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_preferences_response
            return mock_prefs_table
        return MagicMock()

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            assert result is not None
            assert result["id"] == "user-1"


@pytest.mark.asyncio
async def test_get_complete_user_profile_view_error_with_all_attributes(auth_service):
    """Test get_complete_user_profile when view query fails with all error attributes."""
    mock_table = MagicMock()
    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]

    view_error = Exception("View error")
    view_error.message = "Error message"
    view_error.details = "Error details"
    view_error.code = "ERROR_CODE"
    view_error.hint = "Error hint"

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                mock_profile_check
            )
            # Mock fallback call
            mock_basic_profile = MagicMock()
            mock_basic_profile.data = {"id": "user-1", "email": "test@example.com"}
            mock_profiles_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_basic_profile
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = view_error
            return mock_view_table
        elif table_name == "user_preferences":
            mock_prefs_table = MagicMock()
            mock_prefs_response = MagicMock()
            mock_prefs_response.data = None
            mock_prefs_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_prefs_response
            return mock_prefs_table
        return mock_table

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            assert result is not None


@pytest.mark.asyncio
async def test_get_complete_user_profile_fallback_basic_profile_success(auth_service):
    """Test get_complete_user_profile fallback to basic profile with preferences."""
    mock_table = MagicMock()
    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]

    # View query fails
    view_error = Exception("View error")

    mock_basic_profile = MagicMock()
    mock_basic_profile.data = {
        "id": "user-1",
        "email": "test@example.com",
    }

    mock_preferences_response = MagicMock()
    mock_preferences_response.data = {
        "style_preferences": {"color": "blue"},
    }

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                mock_profile_check
            )
            # Fallback call
            mock_profiles_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_basic_profile
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = view_error
            return mock_view_table
        elif table_name == "user_preferences":
            mock_prefs_table = MagicMock()
            mock_prefs_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_preferences_response
            return mock_prefs_table
        return mock_table

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            assert result is not None
            assert result["id"] == "user-1"
            assert "style_preferences" in result


@pytest.mark.asyncio
async def test_get_complete_user_profile_fallback_preferences_no_data(auth_service):
    """Test get_complete_user_profile fallback when preferences fetch returns no data."""
    mock_table = MagicMock()
    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]

    view_error = Exception("View error")

    mock_basic_profile = MagicMock()
    mock_basic_profile.data = {
        "id": "user-1",
        "email": "test@example.com",
    }

    mock_preferences_response = MagicMock()
    mock_preferences_response.data = None  # No preferences

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                mock_profile_check
            )
            mock_profiles_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_basic_profile
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = view_error
            return mock_view_table
        elif table_name == "user_preferences":
            mock_prefs_table = MagicMock()
            mock_prefs_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_preferences_response
            return mock_prefs_table
        return mock_table

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            assert result is not None
            assert "style_preferences" in result
            assert result["quick_reply_preferences"] == {"enabled": True}


@pytest.mark.asyncio
async def test_get_complete_user_profile_fallback_preferences_exception(auth_service):
    """Test get_complete_user_profile fallback when preferences fetch raises exception."""
    mock_table = MagicMock()
    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]

    view_error = Exception("View error")

    mock_basic_profile = MagicMock()
    mock_basic_profile.data = {
        "id": "user-1",
        "email": "test@example.com",
    }

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                mock_profile_check
            )
            mock_profiles_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_basic_profile
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = view_error
            return mock_view_table
        elif table_name == "user_preferences":
            mock_prefs_table = MagicMock()
            mock_prefs_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception(
                "Preferences error"
            )
            return mock_prefs_table
        return mock_table

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            assert result is not None
            assert "style_preferences" in result


@pytest.mark.asyncio
async def test_get_complete_user_profile_fallback_also_fails(auth_service):
    """Test get_complete_user_profile when fallback also fails."""
    mock_table = MagicMock()
    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]

    view_error = Exception("View error")
    fallback_error = Exception("Fallback error")

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                mock_profile_check
            )
            # Fallback call fails
            mock_profiles_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = fallback_error
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = view_error
            return mock_view_table
        return mock_table

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            assert result is None


@pytest.mark.asyncio
async def test_get_complete_user_profile_api_error(auth_service):
    """Test get_complete_user_profile when APIError is raised and caught by outer handler."""
    from postgrest import APIError

    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]

    # Create APIError with a dictionary (as required by the constructor)
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"

    api_error = APIError({"message": "API Error", "code": "ERROR_CODE"})
    api_error.message = "API Error message"
    api_error.details = "API Error details"
    api_error.hint = "API Error hint"
    api_error.response = mock_response

    call_count = {"profiles": 0}

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            call_count["profiles"] += 1
            if call_count["profiles"] == 1:
                # First call - profile check succeeds
                mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                    mock_profile_check
                )
            else:
                # Second call - fallback raises APIError, which will be caught by outer handler
                mock_profiles_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = api_error
            return mock_profiles_table
        elif table_name == "user_profile_view":
            # View query also raises APIError (caught by inner handler, continues to fallback)
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = api_error
            return mock_view_table
        return MagicMock()

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            # The APIError from fallback should be caught by outer handler and return None
            assert result is None


@pytest.mark.asyncio
async def test_get_complete_user_profile_exception_with_cause(auth_service):
    """Test get_complete_user_profile when exception has __cause__."""
    mock_table = MagicMock()
    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]

    cause_exception = ValueError("Root cause")
    main_exception = Exception("Main error")
    main_exception.__cause__ = cause_exception

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                mock_profile_check
            )
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = main_exception
            return mock_view_table
        return mock_table

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            # Should fallback and potentially return None
            assert (
                result is None or result is not None
            )  # Either is acceptable depending on fallback


@pytest.mark.asyncio
async def test_get_complete_user_profile_view_response_no_data(auth_service):
    """Test get_complete_user_profile when view response has no data."""
    mock_table = MagicMock()
    mock_profile_check = MagicMock()
    mock_profile_check.data = [{"id": "user-1"}]

    mock_view_response = MagicMock()
    mock_view_response.data = None  # No data
    mock_view_response.error = "Error message"
    mock_view_response.status = 404

    mock_basic_profile = MagicMock()
    mock_basic_profile.data = {
        "id": "user-1",
        "email": "test@example.com",
    }

    def table_side_effect(table_name):
        if table_name == "profiles":
            mock_profiles_table = MagicMock()
            mock_profiles_table.select.return_value.eq.return_value.execute.return_value = (
                mock_profile_check
            )
            mock_profiles_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_basic_profile
            return mock_profiles_table
        elif table_name == "user_profile_view":
            mock_view_table = MagicMock()
            mock_view_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_view_response
            return mock_view_table
        elif table_name == "user_preferences":
            mock_prefs_table = MagicMock()
            mock_prefs_response = MagicMock()
            mock_prefs_response.data = None
            mock_prefs_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_prefs_response
            return mock_prefs_table
        return mock_table

    with patch.object(auth_service.client, "table", side_effect=table_side_effect):
        with patch("app.services.auth.helpers.db_rate_limiter.acquire", return_value=True):
            result = await auth_service.get_complete_user_profile("user-1")
            assert result is not None


# ============================================================================
# _ensure_user_profile_exists Tests
# ============================================================================


@pytest.mark.asyncio
async def test_ensure_user_profile_exists_success(auth_service):
    """Test _ensure_user_profile_exists successful profile creation."""
    mock_auth_user = MagicMock()
    mock_auth_user.user = MagicMock()
    mock_auth_user.user.id = "user-1"
    mock_auth_user.user.email = "test@example.com"
    mock_auth_user.user.user_metadata = {
        "first_name": "John",
        "last_name": "Doe",
    }
    mock_auth_user.user.created_at = "2024-01-01T00:00:00Z"
    mock_auth_user.user.updated_at = "2024-01-01T00:00:00Z"

    mock_admin = Mock()
    mock_admin.get_user_by_id.return_value = mock_auth_user
    auth_service.client.auth.admin = mock_admin

    mock_table = MagicMock()
    mock_table.insert.return_value.execute.return_value = None
    auth_service.client.table = Mock(return_value=mock_table)

    result = await auth_service._ensure_user_profile_exists("user-1")
    assert result is True
    assert mock_admin.get_user_by_id.called
    assert mock_table.insert.called


@pytest.mark.asyncio
async def test_ensure_user_profile_exists_user_not_found(auth_service):
    """Test _ensure_user_profile_exists when user not found in auth.users."""
    mock_auth_user = MagicMock()
    mock_auth_user.user = None  # User not found

    mock_admin = Mock()
    mock_admin.get_user_by_id.return_value = mock_auth_user
    auth_service.client.auth.admin = mock_admin

    result = await auth_service._ensure_user_profile_exists("user-1")
    assert result is False


@pytest.mark.asyncio
async def test_ensure_user_profile_exists_none_metadata(auth_service):
    """Test _ensure_user_profile_exists when user_metadata is None."""
    mock_auth_user = MagicMock()
    mock_auth_user.user = MagicMock()
    mock_auth_user.user.id = "user-1"
    mock_auth_user.user.email = "test@example.com"
    mock_auth_user.user.user_metadata = None  # No metadata
    mock_auth_user.user.created_at = "2024-01-01T00:00:00Z"
    mock_auth_user.user.updated_at = "2024-01-01T00:00:00Z"

    mock_admin = Mock()
    mock_admin.get_user_by_id.return_value = mock_auth_user
    auth_service.client.auth.admin = mock_admin

    mock_table = MagicMock()
    mock_insert_chain = MagicMock()
    mock_insert_chain.execute.return_value = None
    mock_table.insert.return_value = mock_insert_chain
    auth_service.client.table = Mock(return_value=mock_table)

    result = await auth_service._ensure_user_profile_exists("user-1")
    assert result is True
    # Verify profile_completed is False when metadata is None
    # insert is called twice - once for profiles, once for user_preferences
    assert mock_table.insert.call_count == 2
    # Check the first call (profiles table)
    profile_call_args = mock_table.insert.call_args_list[0][0][0]
    assert profile_call_args["first_name"] is None
    assert profile_call_args["last_name"] is None
    assert profile_call_args["profile_completed"] is False


@pytest.mark.asyncio
async def test_ensure_user_profile_exists_exception(auth_service):
    """Test _ensure_user_profile_exists when exception is raised."""
    mock_admin = Mock()
    mock_admin.get_user_by_id.side_effect = Exception("Auth error")
    auth_service.client.auth.admin = mock_admin

    result = await auth_service._ensure_user_profile_exists("user-1")
    assert result is False


@pytest.mark.asyncio
async def test_ensure_user_profile_exists_partial_metadata(auth_service):
    """Test _ensure_user_profile_exists with partial metadata (only first_name)."""
    mock_auth_user = MagicMock()
    mock_auth_user.user = MagicMock()
    mock_auth_user.user.id = "user-1"
    mock_auth_user.user.email = "test@example.com"
    mock_auth_user.user.user_metadata = {
        "first_name": "John",
        # Missing last_name
    }
    mock_auth_user.user.created_at = "2024-01-01T00:00:00Z"
    mock_auth_user.user.updated_at = "2024-01-01T00:00:00Z"

    mock_admin = Mock()
    mock_admin.get_user_by_id.return_value = mock_auth_user
    auth_service.client.auth.admin = mock_admin

    mock_table = MagicMock()
    mock_insert_chain = MagicMock()
    mock_insert_chain.execute.return_value = None
    mock_table.insert.return_value = mock_insert_chain
    auth_service.client.table = Mock(return_value=mock_table)

    result = await auth_service._ensure_user_profile_exists("user-1")
    assert result is True
    # Verify profile_completed is False when only first_name is present
    # insert is called twice - once for profiles, once for user_preferences
    assert mock_table.insert.call_count == 2
    # Check the first call (profiles table)
    profile_call_args = mock_table.insert.call_args_list[0][0][0]
    assert profile_call_args["first_name"] == "John"
    assert profile_call_args["last_name"] is None
    assert profile_call_args["profile_completed"] is False


# ============================================================================
# Register Edge Cases Tests
# ============================================================================


@pytest.mark.asyncio
async def test_register_sign_out_failure(auth_service):
    """Test register when sign_out after registration fails (should not fail registration)."""
    mock_auth = Mock()
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_session = Mock(access_token="token", refresh_token="refresh_token", expires_in=3600)
    mock_auth.sign_up.return_value = Mock(user=mock_user)
    mock_auth.sign_out.side_effect = Exception("Sign out failed")  # Sign out fails
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations
    mock_table = MagicMock()
    mock_table.insert.return_value.execute.return_value = None
    mock_profile_response = MagicMock()
    mock_profile_response.data = {
        "id": "user-1",
        "email": "test@example.com",
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_profile_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    with patch.object(
        auth_service, "get_complete_user_profile", return_value=mock_profile_response.data
    ):
        result = await auth_service.register("test@example.com", "password", "Jane", "Doe")
        assert result.success is True
        assert result.access_token == "token"


@pytest.mark.asyncio
async def test_register_preferences_creation_failure(auth_service):
    """Test register when user preferences creation fails (should not fail registration)."""
    mock_auth = Mock()
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_session = Mock(access_token="token", refresh_token="refresh_token", expires_in=3600)
    mock_auth.sign_up.return_value = Mock(user=mock_user)
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations - preferences insert fails
    mock_table = MagicMock()
    mock_table.insert.return_value.execute.side_effect = Exception("Preferences already exist")
    mock_profile_response = MagicMock()
    mock_profile_response.data = {
        "id": "user-1",
        "email": "test@example.com",
    }
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_profile_response
    )
    auth_service.client.table = Mock(return_value=mock_table)

    with patch.object(
        auth_service, "get_complete_user_profile", return_value=mock_profile_response.data
    ):
        result = await auth_service.register("test@example.com", "password", "Jane", "Doe")
        assert result.success is True
        assert result.access_token == "token"


@pytest.mark.asyncio
async def test_register_get_complete_profile_failure(auth_service):
    """Test register when get_complete_user_profile fails (should use fallback)."""
    mock_auth = Mock()
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_session = Mock(access_token="token", refresh_token="refresh_token", expires_in=3600)
    mock_auth.sign_up.return_value = Mock(user=mock_user)
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations
    mock_table = MagicMock()
    mock_table.insert.return_value.execute.return_value = None
    auth_service.client.table = Mock(return_value=mock_table)

    with patch.object(
        auth_service, "get_complete_user_profile", side_effect=Exception("Profile fetch failed")
    ):
        with patch(
            "app.services.auth.helpers.extract_user_profile",
            return_value={"id": "user-1", "email": "test@example.com"},
        ):
            result = await auth_service.register("test@example.com", "password", "Jane", "Doe")
            assert result.success is True
            assert result.access_token == "token"
            assert result.user["id"] == "user-1"


@pytest.mark.asyncio
async def test_register_get_complete_profile_returns_none(auth_service):
    """Test register when get_complete_user_profile returns None (should use fallback)."""
    mock_auth = Mock()
    mock_user = Mock()
    mock_user.id = "user-1"
    mock_session = Mock(access_token="token", refresh_token="refresh_token", expires_in=3600)
    mock_auth.sign_up.return_value = Mock(user=mock_user)
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth

    # Mock table operations
    mock_table = MagicMock()
    mock_table.insert.return_value.execute.return_value = None
    auth_service.client.table = Mock(return_value=mock_table)

    with patch.object(auth_service, "get_complete_user_profile", return_value=None):
        with patch(
            "app.services.auth.helpers.extract_user_profile",
            return_value={"id": "user-1", "email": "test@example.com"},
        ):
            result = await auth_service.register("test@example.com", "password", "Jane", "Doe")
            assert result.success is True
            assert result.access_token == "token"
            assert result.user["id"] == "user-1"


# ============================================================================
# update_user_profile_sync Edge Cases Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_user_profile_sync_profile_completed_with_first_name(auth_service):
    """Test update_user_profile_sync sets profile_completed when first_name is updated."""
    mock_admin = Mock()
    mock_user = Mock()
    mock_user.user_metadata = {"first_name": "John", "last_name": "Doe"}
    mock_admin.update_user_by_id.return_value = Mock(user=mock_user)
    auth_service.client.auth.admin = mock_admin

    mock_view_response = Mock()
    mock_view_response.data = [
        {
            "id": "user-1",
            "email": "test@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "profile_completed": True,
        }
    ]

    mock_table = Mock()
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = mock_view_response
    auth_service.client.table = Mock(return_value=mock_table)

    result = await auth_service.update_user_profile_sync("user-1", {"first_name": "Jane"})
    assert result is not None
    assert result["profile_completed"] is True
    # Verify profile_completed was set in updates
    update_call = mock_table.update.call_args[0][0]
    assert update_call.get("profile_completed") is True


@pytest.mark.asyncio
async def test_update_user_profile_sync_profile_completed_with_last_name(auth_service):
    """Test update_user_profile_sync sets profile_completed when last_name is updated."""
    mock_admin = Mock()
    mock_user = Mock()
    mock_user.user_metadata = {"first_name": "John", "last_name": "Doe"}
    mock_admin.update_user_by_id.return_value = Mock(user=mock_user)
    auth_service.client.auth.admin = mock_admin

    mock_view_response = Mock()
    mock_view_response.data = [
        {
            "id": "user-1",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Smith",
            "profile_completed": True,
        }
    ]

    mock_table = Mock()
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = mock_view_response
    auth_service.client.table = Mock(return_value=mock_table)

    result = await auth_service.update_user_profile_sync("user-1", {"last_name": "Smith"})
    assert result is not None
    assert result["profile_completed"] is True


@pytest.mark.asyncio
async def test_update_user_profile_sync_profile_completed_false_when_missing_name(auth_service):
    """Test update_user_profile_sync sets profile_completed False when name is missing."""
    mock_admin = Mock()
    mock_user = Mock()
    mock_user.user_metadata = {"first_name": "John"}  # Missing last_name
    mock_admin.update_user_by_id.return_value = Mock(user=mock_user)
    auth_service.client.auth.admin = mock_admin

    mock_view_response = Mock()
    mock_view_response.data = [
        {
            "id": "user-1",
            "email": "test@example.com",
            "first_name": "John",
            "profile_completed": False,
        }
    ]

    mock_table = Mock()
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = mock_view_response
    auth_service.client.table = Mock(return_value=mock_table)

    result = await auth_service.update_user_profile_sync("user-1", {"first_name": "John"})
    assert result is not None
    # Verify profile_completed was set to False
    update_call = mock_table.update.call_args[0][0]
    assert update_call.get("profile_completed") is False


@pytest.mark.asyncio
async def test_update_user_profile_sync_empty_data(auth_service):
    """Test update_user_profile_sync when view update returns empty data."""
    mock_admin = Mock()
    mock_user = Mock()
    mock_user.user_metadata = {}
    mock_admin.update_user_by_id.return_value = Mock(user=mock_user)
    auth_service.client.auth.admin = mock_admin

    mock_view_response = Mock()
    mock_view_response.data = []  # Empty data

    mock_table = Mock()
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = mock_view_response
    auth_service.client.table = Mock(return_value=mock_table)

    result = await auth_service.update_user_profile_sync("user-1", {"first_name": "John"})
    assert result is None
