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

"""Tests for authentication API endpoints."""

from unittest.mock import patch

from fastapi import status


class TestAuthEndpoints:
    """Test authentication API endpoints."""

    def test_login_success(self, authenticated_client):
        """Test successful login."""
        with patch("app.services.auth_service.auth_service.login") as mock_login:
            mock_login.return_value = {
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {"id": "user-1", "email": "test@example.com"},
            }
            response = authenticated_client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "password123"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, authenticated_client):
        """Test login with invalid credentials."""
        with patch("app.services.auth_service.auth_service.login") as mock_login:
            mock_login.side_effect = ValueError("Invalid credentials")
            response = authenticated_client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "wrongpassword"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid email or password" in response.json()["detail"]

    def test_login_service_exception(self, authenticated_client):
        """Test login when service raises exception."""
        with patch("app.services.auth_service.auth_service.login") as mock_login:
            mock_login.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "password123"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        with patch("app.services.auth_service.auth_service.logout") as mock_logout:
            mock_logout.return_value = {
                "message": "Logged out successfully",
                "success": True,
            }
            response = authenticated_client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": "test_refresh_token"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == "Logged out successfully"
            assert data["success"] is True

    def test_logout_service_exception(self, authenticated_client):
        """Test logout when service raises exception."""
        with patch("app.services.auth_service.auth_service.logout") as mock_logout:
            mock_logout.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": "test_refresh_token"},
            )
            # Should still return success even if service fails
            assert response.status_code == status.HTTP_200_OK

    def test_register_success(self, authenticated_client):
        """Test successful user registration."""
        with patch("app.services.auth_service.auth_service.register") as mock_register:
            mock_register.return_value = {
                "access_token": "test_access_token",
                "token_type": "bearer",
                "expires_in": 3600,
                "message": "Registration successful",
                "user_id": "user-1",
                "success": True,
                "user": {"id": "user-1", "email": "test@example.com"},
            }
            response = authenticated_client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "password123",
                    "first_name": "John",
                    "last_name": "Doe",
                },
            )
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert "access_token" in data
            assert data["message"] == "Registration successful"
            assert data["success"] is True

    def test_register_invalid_data(self, authenticated_client):
        """Test registration with invalid data."""
        with patch("app.services.auth_service.auth_service.register") as mock_register:
            mock_register.side_effect = ValueError("Email already exists")
            response = authenticated_client.post(
                "/api/v1/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "password123",
                    "first_name": "John",
                    "last_name": "Doe",
                },
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Email already exists" in response.json()["detail"]

    def test_register_service_exception(self, authenticated_client):
        """Test registration when service raises exception."""
        with patch("app.services.auth_service.auth_service.register") as mock_register:
            mock_register.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "password123",
                    "first_name": "John",
                    "last_name": "Doe",
                },
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_forgot_password_success(self, authenticated_client):
        """Test successful forgot password request."""
        with patch("app.services.auth_service.auth_service.forgot_password") as mock_forgot:
            mock_forgot.return_value = {
                "message": "Password reset email sent",
                "success": True,
            }
            response = authenticated_client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "test@example.com"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "Password reset email sent" in data["message"]
            assert data["success"] is True

    def test_forgot_password_service_exception(self, authenticated_client):
        """Test forgot password when service raises exception."""
        with patch("app.services.auth_service.auth_service.forgot_password") as mock_forgot:
            mock_forgot.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "test@example.com"},
            )
            # Should still return success even if service fails
            assert response.status_code == status.HTTP_200_OK

    def test_reset_password_success(self, authenticated_client):
        """Test successful password reset."""
        with patch("app.services.auth_service.auth_service.reset_password") as mock_reset:
            mock_reset.return_value = {
                "message": "Password reset successful",
                "success": True,
            }
            response = authenticated_client.post(
                "/api/v1/auth/reset-password",
                json={"token": "valid_token", "new_password": "newpassword123"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == "Password reset successful"
            assert data["success"] is True

    def test_reset_password_invalid_token(self, authenticated_client):
        """Test password reset with invalid token."""
        with patch("app.services.auth_service.auth_service.reset_password") as mock_reset:
            mock_reset.side_effect = ValueError("Invalid or expired token")
            response = authenticated_client.post(
                "/api/v1/auth/reset-password",
                json={"token": "invalid_token", "new_password": "newpassword123"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Invalid or expired reset token" in response.json()["detail"]

    def test_reset_password_service_exception(self, authenticated_client):
        """Test password reset when service raises exception."""
        with patch("app.services.auth_service.auth_service.reset_password") as mock_reset:
            mock_reset.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/auth/reset-password",
                json={"token": "valid_token", "new_password": "newpassword123"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_refresh_token_success(self, authenticated_client):
        """Test successful token refresh."""
        with patch("app.services.auth_service.auth_service.refresh_token") as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "token_type": "bearer",
                "expires_in": 3600,
            }
            response = authenticated_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid_refresh_token"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"

    def test_refresh_token_invalid_token(self, authenticated_client):
        """Test token refresh with invalid refresh token."""
        with patch("app.services.auth_service.auth_service.refresh_token") as mock_refresh:
            mock_refresh.side_effect = ValueError("Invalid refresh token")
            response = authenticated_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "invalid_refresh_token"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid refresh token" in response.json()["detail"]

    def test_refresh_token_service_exception(self, authenticated_client):
        """Test token refresh when service raises exception."""
        with patch("app.services.auth_service.auth_service.refresh_token") as mock_refresh:
            mock_refresh.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid_refresh_token"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_auth_no_auth(self, client):
        """Test auth endpoints without authentication."""
        # Test login (should work without auth)
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert response.status_code in [401, 403, 500]  # Various possible responses

        # Test register (should work without auth)
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "first_name": "John",
                "last_name": "Doe",
            },
        )
        assert response.status_code in [400, 401, 403, 500]  # Various possible responses

        # Test logout (requires auth)
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "test_refresh_token"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test refresh (should work without auth)
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "valid_refresh_token"},
        )
        assert response.status_code in [401, 403, 500]  # Various possible responses
