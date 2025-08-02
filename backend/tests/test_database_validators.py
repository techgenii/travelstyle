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
Tests for database validators.
"""

import uuid

from app.services.database.validators import (
    validate_conversation_id,
    validate_message_content,
    validate_profile_data,
    validate_user_id,
)


class TestValidateUserId:
    """Test validate_user_id function."""

    def test_validate_user_id_valid_uuid(self):
        """Test validate_user_id with valid UUID."""
        valid_uuid = str(uuid.uuid4())
        assert validate_user_id(valid_uuid) is True

    def test_validate_user_id_test_id(self):
        """Test validate_user_id with test ID."""
        test_id = "test-user-123"
        assert validate_user_id(test_id) is True

    def test_validate_user_id_empty_string(self):
        """Test validate_user_id with empty string."""
        assert validate_user_id("") is False

    def test_validate_user_id_none(self):
        """Test validate_user_id with None."""
        assert validate_user_id(None) is False

    def test_validate_user_id_invalid_uuid(self):
        """Test validate_user_id with invalid UUID."""
        invalid_uuid = "not-a-uuid"
        assert validate_user_id(invalid_uuid) is False

    def test_validate_user_id_wrong_type(self):
        """Test validate_user_id with wrong type."""
        assert validate_user_id(123) is False
        assert validate_user_id([]) is False
        assert validate_user_id({}) is False

    def test_validate_user_id_whitespace_only(self):
        """Test validate_user_id with whitespace only."""
        assert validate_user_id("   ") is False

    def test_validate_user_id_malformed_uuid(self):
        """Test validate_user_id with malformed UUID."""
        malformed_uuid = "123e4567-e89b-12d3-a456-426614174000-invalid"
        assert validate_user_id(malformed_uuid) is False


class TestValidateConversationId:
    """Test validate_conversation_id function."""

    def test_validate_conversation_id_valid_uuid(self):
        """Test validate_conversation_id with valid UUID."""
        valid_uuid = str(uuid.uuid4())
        assert validate_conversation_id(valid_uuid) is True

    def test_validate_conversation_id_none(self):
        """Test validate_conversation_id with None."""
        assert validate_conversation_id(None) is True

    def test_validate_conversation_id_test_id(self):
        """Test validate_conversation_id with test ID."""
        test_id = "test-conversation-123"
        assert validate_conversation_id(test_id) is True

    def test_validate_conversation_id_existing_id(self):
        """Test validate_conversation_id with existing ID."""
        existing_id = "existing-conversation-456"
        assert validate_conversation_id(existing_id) is True

    def test_validate_conversation_id_conv_id(self):
        """Test validate_conversation_id with conv ID."""
        conv_id = "conv-789"
        assert validate_conversation_id(conv_id) is True

    def test_validate_conversation_id_empty_string(self):
        """Test validate_conversation_id with empty string."""
        assert validate_conversation_id("") is False

    def test_validate_conversation_id_invalid_uuid(self):
        """Test validate_conversation_id with invalid UUID."""
        invalid_uuid = "not-a-uuid"
        assert validate_conversation_id(invalid_uuid) is False

    def test_validate_conversation_id_wrong_type(self):
        """Test validate_conversation_id with wrong type."""
        assert validate_conversation_id(123) is False
        assert validate_conversation_id([]) is False
        assert validate_conversation_id({}) is False

    def test_validate_conversation_id_whitespace_only(self):
        """Test validate_conversation_id with whitespace only."""
        assert validate_conversation_id("   ") is False

    def test_validate_conversation_id_malformed_uuid(self):
        """Test validate_conversation_id with malformed UUID."""
        malformed_uuid = "123e4567-e89b-12d3-a456-426614174000-invalid"
        assert validate_conversation_id(malformed_uuid) is False

    def test_validate_conversation_id_other_prefix(self):
        """Test validate_conversation_id with other prefix."""
        other_id = "other-prefix-123"
        assert validate_conversation_id(other_id) is False


class TestValidateMessageContent:
    """Test validate_message_content function."""

    def test_validate_message_content_valid(self):
        """Test validate_message_content with valid content."""
        valid_content = "Hello, this is a valid message!"
        assert validate_message_content(valid_content) is True

    def test_validate_message_content_empty_string(self):
        """Test validate_message_content with empty string."""
        assert validate_message_content("") is False

    def test_validate_message_content_whitespace_only(self):
        """Test validate_message_content with whitespace only."""
        assert validate_message_content("   ") is False
        assert validate_message_content("\n\t") is False

    def test_validate_message_content_none(self):
        """Test validate_message_content with None."""
        assert validate_message_content(None) is False

    def test_validate_message_content_wrong_type(self):
        """Test validate_message_content with wrong type."""
        assert validate_message_content(123) is False
        assert validate_message_content([]) is False
        assert validate_message_content({}) is False

    def test_validate_message_content_too_long(self):
        """Test validate_message_content with content exceeding 10KB limit."""
        long_content = "x" * 10001  # 10KB + 1 character
        assert validate_message_content(long_content) is False

    def test_validate_message_content_exactly_10kb(self):
        """Test validate_message_content with exactly 10KB content."""
        exact_content = "x" * 10000  # Exactly 10KB
        assert validate_message_content(exact_content) is True

    def test_validate_message_content_unicode(self):
        """Test validate_message_content with unicode characters."""
        unicode_content = "Hello 世界! 🌍"
        assert validate_message_content(unicode_content) is True

    def test_validate_message_content_with_newlines(self):
        """Test validate_message_content with newlines."""
        content_with_newlines = "Line 1\nLine 2\nLine 3"
        assert validate_message_content(content_with_newlines) is True

    def test_validate_message_content_single_character(self):
        """Test validate_message_content with single character."""
        assert validate_message_content("a") is True

    def test_validate_message_content_stripped_empty(self):
        """Test validate_message_content with content that becomes empty after stripping."""
        assert validate_message_content("   \n\t   ") is False


class TestValidateProfileData:
    """Test validate_profile_data function."""

    def test_validate_profile_data_valid(self):
        """Test validate_profile_data with valid profile data."""
        valid_profile = {
            "first_name": "John",
            "last_name": "Doe",
            "profile_picture_url": "https://example.com/photo.jpg",
            "default_location": "New York",
            "style_preferences": {"casual": True, "formal": False},
            "size_info": {"height": "5'10", "weight": "160lbs"},
            "travel_patterns": {"frequency": "monthly"},
            "currency_preferences": {"USD": True, "EUR": False},
        }
        assert validate_profile_data(valid_profile) is True

    def test_validate_profile_data_empty_dict(self):
        """Test validate_profile_data with empty dictionary."""
        assert validate_profile_data({}) is True

    def test_validate_profile_data_none(self):
        """Test validate_profile_data with None."""
        assert validate_profile_data(None) is False

    def test_validate_profile_data_wrong_type(self):
        """Test validate_profile_data with wrong type."""
        assert validate_profile_data("not a dict") is False
        assert validate_profile_data([]) is False
        assert validate_profile_data(123) is False

    def test_validate_profile_data_with_unknown_fields(self):
        """Test validate_profile_data with unknown fields (should still pass)."""
        profile_with_unknown = {
            "first_name": "John",
            "last_name": "Doe",
            "unknown_field": "should be ignored",
            "another_unknown": {"nested": "data"},
        }
        assert validate_profile_data(profile_with_unknown) is True

    def test_validate_profile_data_partial_fields(self):
        """Test validate_profile_data with only some allowed fields."""
        partial_profile = {
            "first_name": "Jane",
            "style_preferences": {"minimalist": True},
        }
        assert validate_profile_data(partial_profile) is True

    def test_validate_profile_data_nested_structures(self):
        """Test validate_profile_data with nested data structures."""
        nested_profile = {
            "first_name": "Alice",
            "style_preferences": {
                "colors": ["blue", "green"],
                "styles": {"casual": True, "business": False},
            },
            "size_info": {
                "measurements": {"chest": "40", "waist": "32"},
                "preferences": {"fit": "regular"},
            },
        }
        assert validate_profile_data(nested_profile) is True

    def test_validate_profile_data_all_allowed_fields(self):
        """Test validate_profile_data with all allowed fields."""
        complete_profile = {
            "first_name": "Bob",
            "last_name": "Smith",
            "profile_picture_url": "https://example.com/bob.jpg",
            "default_location": "Los Angeles",
            "style_preferences": {"modern": True},
            "size_info": {"shoe_size": "10"},
            "travel_patterns": {"destinations": ["Europe", "Asia"]},
            "currency_preferences": {"JPY": True},
        }
        assert validate_profile_data(complete_profile) is True

    def test_validate_profile_data_mixed_allowed_and_unknown(self):
        """Test validate_profile_data with mix of allowed and unknown fields."""
        mixed_profile = {
            "first_name": "Charlie",
            "last_name": "Brown",
            "allowed_field": "style_preferences",
            "unknown_field": "should be ignored",
            "another_allowed": "size_info",
            "currency_preferences": {"GBP": True},
        }
        assert validate_profile_data(mixed_profile) is True

    def test_validate_profile_data_empty_values(self):
        """Test validate_profile_data with empty values."""
        empty_values_profile = {
            "first_name": "",
            "last_name": None,
            "profile_picture_url": "",
            "default_location": "   ",
            "style_preferences": {},
            "size_info": None,
            "travel_patterns": [],
            "currency_preferences": {},
        }
        assert validate_profile_data(empty_values_profile) is True
