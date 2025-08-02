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
Database helper functions for TravelStyle AI application.
Handles all database operations using Supabase.

This module is maintained for backward compatibility.
For new code, use the modular structure in app.services.database.*
"""

# Import everything from the new modular structure
from app.services.database import (
    ConversationMessage,
    DatabaseHelpers,
    DatabaseOperationError,
    DatabaseTables,
    DatabaseValidationError,
    validate_conversation_id,
    validate_message_content,
    validate_profile_data,
    validate_user_id,
)

# Re-export for backward compatibility
__all__ = [
    "DatabaseHelpers",
    "DatabaseTables",
    "DatabaseValidationError",
    "DatabaseOperationError",
    "ConversationMessage",
    "validate_user_id",
    "validate_conversation_id",
    "validate_message_content",
    "validate_profile_data",
]

# Create a singleton instance for backward compatibility
db_helpers = DatabaseHelpers()
