from unittest.mock import Mock, patch

import pytest
from app.models.auth import LoginRequest
from app.services.auth_service import AuthService


@pytest.fixture
def mock_supabase_client():
    with patch("app.services.auth_service.create_client") as mock_create:
        mock_client = Mock()
        mock_create.return_value = mock_client
        yield mock_client


@pytest.fixture
def auth_service(mock_supabase_client):
    return AuthService()


@patch(
    "app.services.auth_service.extract_user_profile",
    return_value={"id": "user-1", "email": "test@example.com"},
)
@pytest.mark.asyncio
async def test_login_success(mock_extract, auth_service):
    mock_auth = Mock()
    mock_session = Mock(access_token="token", refresh_token="refresh", expires_in=3600)
    mock_user = Mock()
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth
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
    with pytest.raises(ValueError):
        await auth_service.login(login_data)


@pytest.mark.asyncio
async def test_login_no_session(auth_service):
    mock_auth = Mock()
    mock_auth.sign_in_with_password.return_value = Mock(user=Mock(), session=None)
    auth_service.client.auth = mock_auth
    login_data = LoginRequest(email="test@example.com", password="password")
    with pytest.raises(ValueError):
        await auth_service.login(login_data)


@pytest.mark.asyncio
async def test_login_exception(auth_service):
    mock_auth = Mock()
    mock_auth.sign_in_with_password.side_effect = Exception("fail")
    auth_service.client.auth = mock_auth
    login_data = LoginRequest(email="test@example.com", password="password")
    with pytest.raises(ValueError):
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
async def test_forgot_password_exception(auth_service):
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
async def test_reset_password_exception(auth_service):
    mock_auth = Mock()
    mock_auth.update_user.side_effect = Exception("fail")
    auth_service.client.auth = mock_auth
    with pytest.raises(ValueError):
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
async def test_refresh_token_no_session(auth_service):
    mock_auth = Mock()
    mock_auth.refresh_session.return_value = Mock(session=None)
    auth_service.client.auth = mock_auth
    with pytest.raises(ValueError):
        await auth_service.refresh_token("refresh")


@pytest.mark.asyncio
async def test_refresh_token_exception(auth_service):
    mock_auth = Mock()
    mock_auth.refresh_session.side_effect = Exception("fail")
    auth_service.client.auth = mock_auth
    with pytest.raises(ValueError):
        await auth_service.refresh_token("refresh")


@patch(
    "app.services.auth_service.extract_user_profile",
    return_value={"id": "user-1", "email": "test@example.com"},
)
@pytest.mark.asyncio
async def test_register_success(mock_extract, auth_service):
    mock_auth = Mock()
    mock_user = Mock()
    mock_session = Mock(access_token="token", expires_in=3600)
    mock_auth.sign_up.return_value = Mock(user=mock_user)
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    auth_service.client.auth = mock_auth
    result = await auth_service.register("test@example.com", "password", "Jane", "Doe")
    assert result.access_token == "token"
    assert result.user["id"] == "user-1"


@pytest.mark.asyncio
async def test_register_no_user(auth_service):
    mock_auth = Mock()
    mock_auth.sign_up.return_value = Mock(user=None)
    auth_service.client.auth = mock_auth
    with pytest.raises(ValueError):
        await auth_service.register("test@example.com", "password")


@pytest.mark.asyncio
async def test_register_no_session(auth_service):
    mock_auth = Mock()
    mock_user = Mock()
    mock_auth.sign_up.return_value = Mock(user=mock_user)
    mock_auth.sign_in_with_password.return_value = Mock(user=mock_user, session=None)
    auth_service.client.auth = mock_auth
    with pytest.raises(ValueError):
        await auth_service.register("test@example.com", "password")


@pytest.mark.asyncio
async def test_register_exception(auth_service):
    mock_auth = Mock()
    mock_auth.sign_up.side_effect = Exception("fail")
    auth_service.client.auth = mock_auth
    with pytest.raises(ValueError):
        await auth_service.register("test@example.com", "password")


@patch(
    "app.services.auth_service.extract_user_profile",
    return_value={"id": "user-1", "email": "test@example.com"},
)
@pytest.mark.asyncio
async def test_get_user_profile_success(mock_extract, auth_service):
    mock_admin = Mock()
    mock_admin.get_user_by_id.return_value = Mock(user=Mock())
    auth_service.client.auth.admin = mock_admin
    result = await auth_service.get_user_profile("user-1")
    assert result["id"] == "user-1"


@pytest.mark.asyncio
async def test_get_user_profile_no_user(auth_service):
    mock_admin = Mock()
    mock_admin.get_user_by_id.return_value = Mock(user=None)
    auth_service.client.auth.admin = mock_admin
    result = await auth_service.get_user_profile("user-1")
    assert result is None


@pytest.mark.asyncio
async def test_get_user_profile_exception(auth_service):
    mock_admin = Mock()
    mock_admin.get_user_by_id.side_effect = Exception("fail")
    auth_service.client.auth.admin = mock_admin
    result = await auth_service.get_user_profile("user-1")
    assert result is None


@patch(
    "app.services.auth_service.extract_user_profile",
    return_value={"id": "user-1", "email": "test@example.com"},
)
@pytest.mark.asyncio
async def test_update_user_profile_success(mock_extract, auth_service):
    mock_admin = Mock()
    mock_admin.update_user_by_id.return_value = Mock(user=Mock())
    auth_service.client.auth.admin = mock_admin
    result = await auth_service.update_user_profile("user-1", {"first_name": "Jane"})
    assert result["id"] == "user-1"


@pytest.mark.asyncio
async def test_update_user_profile_no_user(auth_service):
    mock_admin = Mock()
    mock_admin.update_user_by_id.return_value = Mock(user=None)
    auth_service.client.auth.admin = mock_admin
    result = await auth_service.update_user_profile("user-1", {"first_name": "Jane"})
    assert result is None


@pytest.mark.asyncio
async def test_update_user_profile_exception(auth_service):
    mock_admin = Mock()
    mock_admin.update_user_by_id.side_effect = Exception("fail")
    auth_service.client.auth.admin = mock_admin
    result = await auth_service.update_user_profile("user-1", {"first_name": "Jane"})
    assert result is None


@patch(
    "app.services.auth_service.extract_user_profile",
    return_value={"id": "user-1", "email": "test@example.com"},
)
@pytest.mark.asyncio
async def test_update_user_profile_sync_success(mock_extract, auth_service):
    mock_admin = Mock()
    mock_admin.update_user_by_id.return_value = Mock(
        user=Mock(), user_metadata={"first_name": "Jane", "last_name": "Doe"}
    )
    mock_table = Mock()
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = None
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
async def test_update_user_profile_sync_exception(auth_service):
    mock_admin = Mock()
    mock_admin.update_user_by_id.side_effect = Exception("fail")
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
async def test_update_user_preferences_exception(auth_service):
    mock_table = Mock()
    mock_table.update.side_effect = Exception("fail")
    auth_service.client.table = Mock(return_value=mock_table)
    result = await auth_service.update_user_preferences(
        "user-1", {"style_preferences": {"color": "blue"}}
    )
    assert result is False
