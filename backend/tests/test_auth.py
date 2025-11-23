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

"""Tests for authentication API endpoints and validators."""

from unittest.mock import patch

import pytest
from app.services.auth.validators import (
    validate_auth_request,
    validate_email,
    validate_password,
    validate_registration_data,
    validate_token,
    validate_user_id,
    validate_user_metadata,
)
from fastapi import status


class TestAuthValidators:
    """Test authentication validators."""

    def test_validate_email_valid(self):
        """Test validate_email with valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@numbers.com",
            "test.email@subdomain.example.com",
        ]

        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test validate_email with invalid email addresses."""
        invalid_emails = [
            "",  # Empty string
            None,  # None value
            123,  # Non-string
            "invalid-email",  # Missing @
            "@example.com",  # Missing local part
            "test@",  # Missing domain
            "test@.com",  # Missing domain name
            "test@example",  # Missing TLD
        ]

        for email in invalid_emails:
            assert validate_email(email) is False

    def test_validate_password_valid(self):
        """Test validate_password with valid passwords."""
        valid_passwords = [
            "password123",
            "123456",  # Minimum length
            "verylongpasswordwithspecialchars!@#",
            "a" * 100,  # Very long password
        ]

        for password in valid_passwords:
            assert validate_password(password) is True

    def test_validate_password_invalid(self):
        """Test validate_password with invalid passwords."""
        invalid_passwords = [
            "",  # Empty string
            None,  # None value
            123,  # Non-string
            "12345",  # Too short (less than 6 characters)
            "abc",  # Too short
            "",  # Empty string
        ]

        for password in invalid_passwords:
            assert validate_password(password) is False

    def test_validate_user_id_valid(self):
        """Test validate_user_id with valid user IDs."""
        valid_user_ids = [
            "12345678-1234-1234-1234-123456789012",
            "abcdef12-3456-7890-abcd-ef1234567890",
            "00000000-0000-0000-0000-000000000000",
            "ffffffff-ffff-ffff-ffff-ffffffffffff",
        ]

        for user_id in valid_user_ids:
            assert validate_user_id(user_id) is True

    def test_validate_user_id_invalid(self):
        """Test validate_user_id with invalid user IDs."""
        invalid_user_ids = [
            "",  # Empty string
            None,  # None value
            123,  # Non-string
            "invalid-uuid",  # Invalid format
            "12345678-1234-1234-1234-12345678901",  # Too short
            "12345678-1234-1234-1234-1234567890123",  # Too long
            "12345678-1234-1234-1234-12345678901g",  # Invalid character
            "12345678-1234-1234-1234-12345678901G",  # Invalid character
            "12345678-1234-1234-1234-12345678901-",  # Invalid character
        ]

        for user_id in invalid_user_ids:
            assert validate_user_id(user_id) is False

    def test_validate_token_valid(self):
        """Test validate_token with valid tokens."""
        valid_tokens = [
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            "very_long_token_with_more_than_ten_characters",
            "a" * 20,  # 20 character token
            "token123456789",  # 13 character token
        ]

        for token in valid_tokens:
            assert validate_token(token) is True

    def test_validate_token_invalid(self):
        """Test validate_token with invalid tokens."""
        invalid_tokens = [
            "",  # Empty string
            None,  # None value
            123,  # Non-string
            "short",  # Too short (less than 10 characters)
            "123456789",  # Exactly 9 characters (less than 10)
            "",  # Empty string
        ]

        for token in invalid_tokens:
            assert validate_token(token) is False

    def test_validate_user_metadata_valid(self):
        """Test validate_user_metadata with valid metadata."""
        valid_metadata = [
            {},  # Empty dict
            {"name": "John Doe"},
            {"age": 25, "email": "test@example.com"},
            {"score": 95.5, "active": True, "name": "Alice"},
        ]

        for metadata in valid_metadata:
            assert validate_user_metadata(metadata) is True

    def test_validate_user_metadata_invalid(self):
        """Test validate_user_metadata with invalid metadata."""
        invalid_metadata = [
            None,  # None value
            "not_a_dict",  # String instead of dict
            123,  # Number instead of dict
            [],  # List instead of dict
            {123: "value"},  # Non-string key
            {"key": [1, 2, 3]},  # List value (not allowed)
            {"key": {"nested": "dict"}},  # Dict value (not allowed)
            {"key": lambda x: x},  # Function value (not allowed)
        ]

        for metadata in invalid_metadata:
            assert validate_user_metadata(metadata) is False

    def test_validate_auth_request_valid(self):
        """Test validate_auth_request with valid data."""
        # Should not raise any exception
        validate_auth_request("test@example.com", "password123")

    def test_validate_auth_request_invalid_email(self):
        """Test validate_auth_request with invalid email."""
        from app.services.auth.exceptions import AuthenticationError

        with pytest.raises(AuthenticationError, match="Invalid email format"):
            validate_auth_request("invalid-email", "password123")

    def test_validate_auth_request_invalid_password(self):
        """Test validate_auth_request with invalid password."""
        from app.services.auth.exceptions import AuthenticationError

        with pytest.raises(AuthenticationError, match="Invalid password format"):
            validate_auth_request("test@example.com", "123")

    def test_validate_registration_data_valid(self):
        """Test validate_registration_data with valid data."""
        # Should not raise any exception
        validate_registration_data("test@example.com", "password123")
        validate_registration_data("test@example.com", "password123", "John", "Doe")
        validate_registration_data("test@example.com", "password123", first_name="John")
        validate_registration_data("test@example.com", "password123", last_name="Doe")

    def test_validate_registration_data_invalid_email(self):
        """Test validate_registration_data with invalid email."""
        from app.services.auth.exceptions import AuthenticationError

        with pytest.raises(AuthenticationError, match="Invalid email format"):
            validate_registration_data("invalid-email", "password123")

    def test_validate_registration_data_invalid_password(self):
        """Test validate_registration_data with invalid password."""
        from app.services.auth.exceptions import AuthenticationError

        with pytest.raises(AuthenticationError, match="Invalid password format"):
            validate_registration_data("test@example.com", "123")

    def test_validate_registration_data_invalid_first_name(self):
        """Test validate_registration_data with invalid first name."""
        from app.services.auth.exceptions import AuthenticationError

        with pytest.raises(AuthenticationError, match="Invalid first name format"):
            validate_registration_data("test@example.com", "password123", first_name=123)

    def test_validate_registration_data_invalid_last_name(self):
        """Test validate_registration_data with invalid last name."""
        from app.services.auth.exceptions import AuthenticationError

        with pytest.raises(AuthenticationError, match="Invalid last name format"):
            validate_registration_data("test@example.com", "password123", last_name=456)


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
            from app.services.auth.exceptions import AuthenticationError

            mock_login.side_effect = AuthenticationError("Invalid email or password")
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
                "refresh_token": "test_refresh_token",
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
            assert "refresh_token" in data
            assert data["refresh_token"] == "test_refresh_token"
            assert data["message"] == "Registration successful"
            assert data["success"] is True

    def test_register_invalid_data(self, authenticated_client):
        """Test registration with invalid data."""
        with patch("app.services.auth_service.auth_service.register") as mock_register:
            from app.services.auth.exceptions import RegistrationError

            mock_register.side_effect = RegistrationError("Email already exists")
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
            from app.services.auth.exceptions import TokenError

            mock_reset.side_effect = TokenError("Invalid or expired reset token")
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
            from app.services.auth.exceptions import TokenError

            mock_refresh.side_effect = TokenError("Invalid refresh token")
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
        # Test login (should work without auth, but fail with invalid credentials)
        with patch("app.services.auth_service.auth_service.login") as mock_login:
            from app.services.auth.exceptions import AuthenticationError

            mock_login.side_effect = AuthenticationError("Invalid email or password")
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "nonexistent@example.com", "password": "wrongpassword"},
            )
            # Login should fail with invalid credentials, not because of missing auth
            assert response.status_code in [401, 400]  # Invalid credentials or validation error

        # Test register (should work without auth, but fail with existing user)
        with patch("app.services.auth_service.auth_service.register") as mock_register:
            from app.services.auth.exceptions import RegistrationError

            mock_register.side_effect = RegistrationError("Email already exists")
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",  # This user likely exists
                    "password": "password123",
                    "first_name": "John",
                    "last_name": "Doe",
                },
            )
            # Register should fail if user exists, not because of missing auth
            assert response.status_code in [400, 409]  # Validation error or user already exists

        # Test logout (requires auth)
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "test_refresh_token"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test refresh (should work without auth, but fail with invalid token)
        with patch("app.services.auth_service.auth_service.refresh_token") as mock_refresh:
            from app.services.auth.exceptions import TokenError

            mock_refresh.side_effect = TokenError("Invalid refresh token")
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "invalid_refresh_token"},
            )
            assert response.status_code in [401, 400]  # Invalid refresh token
