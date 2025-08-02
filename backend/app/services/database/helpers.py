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
Main database helpers for TravelStyle AI application.
Provides a unified interface for all database operations.
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.services.database.constants import DatabaseTables
from app.services.database.conversations import ConversationOperations
from app.services.database.users import UserOperations
from app.services.supabase import get_supabase_client
from supabase import Client

logger = logging.getLogger(__name__)


class DatabaseHelpers:
    """Main database helper class that provides unified access to all database operations."""

    def __init__(self, supabase_client: Client | None = None):
        # Use the provided client, shared client, or create a new one
        if supabase_client:
            self.client = supabase_client
        else:
            # Use the shared client for better connection pooling
            self.client = get_supabase_client()

        # Initialize operation classes
        self.conversations = ConversationOperations(self.client)
        self.users = UserOperations(self.client)

    # Conversation operations - delegate to ConversationOperations
    async def get_conversation_history(
        self, user_id: str, conversation_id: str | None
    ) -> list[dict]:
        """Retrieve conversation history from database."""
        return await self.conversations.get_conversation_history(user_id, conversation_id)

    async def save_conversation_message(
        self,
        user_id: str,
        conversation_id: str | None,
        user_message: str,
        ai_response: str,
        conversation_type: str = "mixed",
        message_metadata: dict | None = None,
    ) -> dict[str, Any] | None:
        """Save conversation message to database."""
        return await self.conversations.save_conversation_message(
            user_id, conversation_id, user_message, ai_response, conversation_type, message_metadata
        )

    async def get_user_conversations(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get user's recent conversations."""
        return await self.conversations.get_user_conversations(user_id, limit)

    async def archive_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Archive a conversation."""
        return await self.conversations.archive_conversation(user_id, conversation_id)

    async def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Delete a conversation and all its messages."""
        return await self.conversations.delete_conversation(user_id, conversation_id)

    # User operations - delegate to UserOperations
    async def get_user_profile(self, user_id: str) -> dict:
        """Retrieve user profile from user_profile_view."""
        return await self.users.get_user_profile(user_id)

    async def save_user_profile(self, user_id: str, profile_data: dict) -> dict | None:
        """Save user profile data."""
        return await self.users.save_user_profile(user_id, profile_data)

    async def update_user_preferences(self, user_id: str, preferences: dict) -> bool:
        """Update user preferences."""
        return await self.users.update_user_preferences(user_id, preferences)

    async def save_recommendation_feedback(
        self,
        user_id: str,
        conversation_id: str,
        message_id: str,
        feedback_type: str,
        feedback_text: str | None = None,
        ai_response_content: str | None = None,
    ) -> bool:
        """Save recommendation feedback."""
        return await self.users.save_recommendation_feedback(
            user_id, conversation_id, message_id, feedback_type, feedback_text, ai_response_content
        )

    async def save_destination(
        self, user_id: str, destination_name: str, destination_data: dict | None = None
    ) -> bool:
        """Save user destination."""
        return await self.users.save_destination(user_id, destination_name, destination_data)

    async def update_user_profile_picture_url(self, user_id: str, profile_picture_url: str) -> bool:
        """Update user's profile picture URL."""
        return await self.users.update_user_profile_picture_url(user_id, profile_picture_url)

    # Legacy methods for backward compatibility
    async def save_conversation_message_with_transaction(
        self,
        user_id: str,
        conversation_id: str | None,
        user_message: str,
        ai_response: str,
        conversation_type: str = "mixed",
        message_metadata: dict | None = None,
    ) -> dict[str, Any] | None:
        """Legacy method - delegates to save_conversation_message."""
        return await self.save_conversation_message(
            user_id, conversation_id, user_message, ai_response, conversation_type, message_metadata
        )

    async def create_chat_session(
        self, user_id: str, conversation_id: str, destination: str | None = None
    ) -> dict:
        """Create a chat session - legacy method for backward compatibility."""
        try:
            session_data = {
                "id": conversation_id,
                "user_id": user_id,
                "destination": destination,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }

            response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.CONVERSATIONS).insert(session_data).execute()
                )
            )

            # Return a clean session object without datetime objects
            if response.data and len(response.data) > 0:
                session = response.data[0]
                # Convert datetime objects to ISO format strings for JSON serialization
                if "created_at" in session and isinstance(session["created_at"], datetime):
                    session["created_at"] = session["created_at"].isoformat()
                if "updated_at" in session and isinstance(session["updated_at"], datetime):
                    session["updated_at"] = session["updated_at"].isoformat()
                return session
            return {}

        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            return {}
