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
Database package for TravelStyle AI application.
Provides modular database operations for conversations, users, and validation.
"""

from app.services.database.constants import DatabaseTables
from app.services.database.exceptions import DatabaseOperationError, DatabaseValidationError
from app.services.database.helpers import DatabaseHelpers
from app.services.database.models import ConversationMessage
from app.services.database.validators import (
    validate_conversation_id,
    validate_message_content,
    validate_profile_data,
    validate_user_id,
)

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
