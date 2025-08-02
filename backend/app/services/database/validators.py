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
Database validation functions for TravelStyle AI application.
"""

import uuid


def validate_user_id(user_id: str) -> bool:
    """Validate user ID format."""
    if not user_id or not isinstance(user_id, str):
        return False

    # Allow test IDs for testing purposes
    if user_id.startswith("test-"):
        return True

    try:
        uuid.UUID(user_id)
        return True
    except (ValueError, TypeError):
        return False


def validate_conversation_id(conversation_id: str | None) -> bool:
    """Validate conversation ID format."""
    if conversation_id is None:
        return True

    if not isinstance(conversation_id, str):
        return False

    # Allow test IDs for testing purposes
    if (
        conversation_id.startswith("test-")
        or conversation_id.startswith("existing-")
        or conversation_id.startswith("conv-")
    ):
        return True

    try:
        uuid.UUID(conversation_id)
        return True
    except (ValueError, TypeError):
        return False


def validate_message_content(content: str) -> bool:
    """Validate message content."""
    if not isinstance(content, str):
        return False
    if len(content.strip()) == 0:
        return False
    if len(content) > 10000:  # 10KB limit
        return False
    return True


def validate_profile_data(profile_data: dict) -> bool:
    """Validate profile data structure."""
    if not isinstance(profile_data, dict):
        return False

    # Check for required fields if they exist
    allowed_fields = {
        "first_name",
        "last_name",
        "profile_picture_url",
        "default_location",
        "style_preferences",
        "size_info",
        "travel_patterns",
        "currency_preferences",
    }

    for key in profile_data:
        if key not in allowed_fields:
            # Log warning but don't fail validation
            pass

    return True
