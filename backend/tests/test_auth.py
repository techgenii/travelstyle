"""
Tests for authentication endpoints.
"""
from unittest.mock import patch
from fastapi import status
from app.models.auth import (
    LoginResponse, LogoutResponse, ForgotPasswordResponse,
    ResetPasswordResponse, RefreshTokenResponse, RegisterResponse
)
# pylint: disable=line-too-long

# Split into two classes to avoid too-many-public-methods
class TestAuthRegistrationAndLogin:
    """Test registration and login endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        with patch('app.services.auth_service.auth_service.register') as mock_register:
            mock_register.return_value = RegisterResponse(
                access_token="test-access-token",
                token_type="bearer",
                expires_in=3600,
                message="Registration successful",
                user_id="test-user-id",
                success=True,
                user={
                    "id": "test-user-id",
                    "email": "test@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "avatar_url": None,
                    "role": "user",
                    "status": "active",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "last_login": None,
                    "preferences": None
                }
            )
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "testpassword123",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            )
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["access_token"] == "test-access-token"
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == 3600
            assert data["message"] == "Registration successful"
            assert data["user_id"] == "test-user-id"
            assert data["success"] is True
            assert data["user"]["email"] == "test@example.com"
            assert data["user"]["first_name"] == "John"
            assert data["user"]["last_name"] == "Doe"

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "invalid-email", "password": "testpassword123"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_password(self, client):
        """Test registration with short password."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "123"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_service_error(self, client):
        """Test registration when service raises error."""
        with patch('app.services.auth_service.auth_service.register') as mock_register:
            mock_register.side_effect = ValueError(
                "Registration failed. Email may already be in use."
            )
            response = client.post(
                "/api/v1/auth/register",
                json={"email": "test@example.com", "password": "testpassword123"}
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Registration failed" in response.json()["detail"]

    def test_login_success(self, client):
        """Test successful login."""
        with patch('app.services.auth_service.auth_service.login') as mock_login:
            mock_login.return_value = LoginResponse(
                access_token="test-access-token",
                refresh_token="test-refresh-token",
                token_type="bearer",
                expires_in=3600,
                user={
                    "id": "test-user-id",
                    "email": "test@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "avatar_url": None,
                    "role": "user",
                    "status": "active",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "last_login": None,
                    "preferences": None
                }
            )
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "testpassword123"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == "test-access-token"
            assert data["refresh_token"] == "test-refresh-token"
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == 3600
            assert data["user"]["email"] == "test@example.com"
            assert data["user"]["first_name"] == "John"
            assert data["user"]["last_name"] == "Doe"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        with patch('app.services.auth_service.auth_service.login') as mock_login:
            mock_login.side_effect = ValueError("Invalid credentials")
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "wrongpassword"}
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == "Invalid email or password"

    def test_login_invalid_email(self, client):
        """Test login with invalid email format."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "invalid-email", "password": "testpassword123"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestAuthOtherEndpoints:
    """Test logout, password, refresh, and profile endpoints."""

    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        with patch('app.services.auth_service.auth_service.logout') as mock_logout:
            mock_logout.return_value = LogoutResponse(
                message="Successfully logged out",
                success=True
            )
            response = authenticated_client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": "test-refresh-token"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == "Successfully logged out"
            assert data["success"] is True

    def test_logout_without_token(self, authenticated_client):
        """Test logout without refresh token."""
        with patch('app.services.auth_service.auth_service.logout') as mock_logout:
            mock_logout.return_value = LogoutResponse(
                message="Successfully logged out",
                success=True
            )
            response = authenticated_client.post("/api/v1/auth/logout")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True

    def test_logout_unauthorized(self, client):
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_forgot_password_success(self, client):
        """Test successful forgot password request."""
        with patch('app.services.auth_service.auth_service.forgot_password') as mock_forgot:
            mock_forgot.return_value = ForgotPasswordResponse(
                message="Password reset email sent successfully",
                success=True
            )
            response = client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "test@example.com"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == "Password reset email sent successfully"
            assert data["success"] is True

    def test_forgot_password_invalid_email(self, client):
        """Test forgot password with invalid email format."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "invalid-email"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_reset_password_success(self, client):
        """Test successful password reset."""
        with patch('app.services.auth_service.auth_service.reset_password') as mock_reset:
            mock_reset.return_value = ResetPasswordResponse(
                message="Password reset successfully",
                success=True
            )
            response = client.post(
                "/api/v1/auth/reset-password",
                json={"token": "test-reset-token", "new_password": "newpassword123"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == "Password reset successfully"
            assert data["success"] is True

    def test_reset_password_invalid_token(self, client):
        """Test password reset with invalid token."""
        with patch('app.services.auth_service.auth_service.reset_password') as mock_reset:
            mock_reset.side_effect = ValueError("Invalid or expired reset token")
            response = client.post(
                "/api/v1/auth/reset-password",
                json={"token": "invalid-token", "new_password": "newpassword123"}
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Invalid or expired reset token" in response.json()["detail"]

    def test_reset_password_short_password(self, client):
        """Test password reset with short password."""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "test-reset-token", "new_password": "123"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_refresh_token_success(self, client):
        """Test successful token refresh."""
        with patch('app.services.auth_service.auth_service.refresh_token') as mock_refresh:
            mock_refresh.return_value = RefreshTokenResponse(
                access_token="new-access-token",
                refresh_token="new-refresh-token",
                token_type="bearer",
                expires_in=3600
            )
            response = client.post(
                "/api/v1/auth/refresh",
                json={
                    "refresh_token": "test-refresh-token"
                }
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            # pylint: disable-next=line-too-long
            assert data["access_token"] == "new-access-token"
            # pylint: disable-next=line-too-long
            assert data["refresh_token"] == "new-refresh-token"
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == 3600

    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid refresh token."""
        with patch('app.services.auth_service.auth_service.refresh_token') as mock_refresh:
            mock_refresh.side_effect = ValueError("Invalid refresh token")
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "invalid-refresh-token"}
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == "Invalid refresh token"

    def test_get_current_user_profile_success(self, authenticated_client):
        """Test successful get current user profile."""
        with patch('app.services.auth_service.auth_service.get_user_profile') as mock_get_profile:
            mock_get_profile.return_value = {
                "id": "test-user-id",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "created_at": (
                    "2023-01-01T00:00:00Z"
                ),
                "updated_at": (
                    "2023-01-01T00:00:00Z"
                )
            }
            response = authenticated_client.get("/api/v1/auth/me")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == "test-user-id"
            assert data["email"] == "test@example.com"
            assert data["first_name"] == "John"
            assert data["last_name"] == "Doe"

    def test_get_current_user_profile_not_found(self, authenticated_client):
        """Test get current user profile when user not found."""
        with patch('app.services.auth_service.auth_service.get_user_profile') as mock_get_profile:
            mock_get_profile.return_value = None
            response = authenticated_client.get("/api/v1/auth/me")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "User profile not found"

    def test_get_current_user_profile_unauthorized(self, client):
        """Test get current user profile without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_current_user_profile_success(self, authenticated_client):
        """Test successful update current user profile."""
        with patch('app.services.auth_service.auth_service.update_user_profile_sync') as mock_update_profile:
            mock_update_profile.return_value = {
                "id": "test-user-id",
                "email": "test@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "created_at": (
                    "2023-01-01T00:00:00Z"
                ),
                "updated_at": (
                    "2023-01-01T00:00:00Z"
                )
            }
            response = authenticated_client.put(
                "/api/v1/auth/me",
                json={
                    "first_name": "Jane",
                    "last_name": "Smith"
                }
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            # pylint: disable-next=line-too-long
            assert data["first_name"] == "Jane"
            # pylint: disable-next=line-too-long
            assert data["last_name"] == "Smith"

    def test_update_current_user_profile_no_valid_fields(self, authenticated_client):
        """Test update current user profile with no valid fields."""
        response = authenticated_client.put(
            "/api/v1/auth/me",
            json={"invalid_field": "value"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "No valid fields to update"

    def test_update_current_user_profile_not_found(self, authenticated_client):
        """Test update current user profile when user not found."""
        with patch('app.services.auth_service.auth_service.update_user_profile_sync') as mock_update_profile:
            mock_update_profile.return_value = None
            response = authenticated_client.put(
                "/api/v1/auth/me",
                json={"first_name": "Jane"}
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "User profile not found"

    def test_update_current_user_profile_unauthorized(self, client):
        """Test update current user profile without authentication."""
        response = client.put(
            "/api/v1/auth/me",
            json={"first_name": "Jane"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
