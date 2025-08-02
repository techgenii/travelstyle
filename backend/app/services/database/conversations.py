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
Conversation-related database operations for TravelStyle AI application.
"""

import asyncio
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from app.services.database.constants import DatabaseTables
from app.services.database.validators import (
    validate_conversation_id,
    validate_message_content,
    validate_user_id,
)
from app.services.rate_limiter import db_rate_limiter

logger = logging.getLogger(__name__)


class ConversationOperations:
    """Handles conversation-related database operations."""

    def __init__(self, client):
        self.client = client

    async def get_conversation_history(
        self, user_id: str, conversation_id: str | None
    ) -> list[dict]:
        """Retrieve conversation history from database."""
        # Validate inputs
        if not validate_user_id(user_id):
            logger.error(f"Invalid user_id format: {user_id}")
            return []

        if not validate_conversation_id(conversation_id):
            logger.error(f"Invalid conversation_id format: {conversation_id}")
            return []

        # Apply rate limiting for read operations
        if not await db_rate_limiter.acquire("read"):
            logger.warning("Rate limited: get_conversation_history")
            return []

        try:
            if conversation_id:
                # Get messages for a specific conversation
                response = await asyncio.to_thread(
                    lambda: (
                        self.client.table(DatabaseTables.CONVERSATION_MESSAGES)
                        .select("*")
                        .eq("conversation_id", conversation_id)
                        .order("created_at", desc=False)
                        .execute()
                    )
                )

                return response.data if response.data else []
            else:
                # Get recent conversations for the user
                conversations_response = await asyncio.to_thread(
                    lambda: (
                        self.client.table(DatabaseTables.CONVERSATIONS)
                        .select("id, title, messages, created_at, updated_at")
                        .eq("user_id", user_id)
                        .eq("is_archived", False)
                        .order("updated_at", desc=True)
                        .limit(10)
                        .execute()
                    )
                )

                return conversations_response.data if conversations_response.data else []

        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []

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
        # Validate inputs
        if not validate_user_id(user_id):
            logger.error(f"Invalid user_id format: {user_id}")
            return None

        if not validate_conversation_id(conversation_id):
            logger.error(f"Invalid conversation_id format: {conversation_id}")
            return None

        if not validate_message_content(user_message):
            logger.error(f"Invalid user_message content: {user_message}")
            return None

        if not validate_message_content(ai_response):
            logger.error(f"Invalid ai_response content: {ai_response}")
            return None

        # Apply rate limiting for write operations
        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: save_conversation_message")
            return None

        try:
            # Create conversation if it doesn't exist
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                conversation_data = {
                    "id": conversation_id,
                    "user_id": user_id,
                    "title": user_message[:50] + "..." if len(user_message) > 50 else user_message,
                    "messages": 1,
                    "type": conversation_type,
                    "created_at": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat(),
                }

                await asyncio.to_thread(
                    lambda: (
                        self.client.table(DatabaseTables.CONVERSATIONS)
                        .insert(conversation_data)
                        .execute()
                    )
                )
            else:
                # Update existing conversation with atomic increment
                current_response = await asyncio.to_thread(
                    lambda: (
                        self.client.table(DatabaseTables.CONVERSATIONS)
                        .select("messages")
                        .eq("id", conversation_id)
                        .execute()
                    )
                )

                current_count = (
                    current_response.data[0].get("messages", 0) if current_response.data else 0
                )

                await asyncio.to_thread(
                    lambda: (
                        self.client.table(DatabaseTables.CONVERSATIONS)
                        .update(
                            {
                                "messages": current_count + 1,
                                "updated_at": datetime.now(UTC).isoformat(),
                            }
                        )
                        .eq("id", conversation_id)
                        .execute()
                    )
                )

            # Save the user message
            user_message_data = {
                "conversation_id": conversation_id,
                "message_id": str(uuid.uuid4()),
                "role": "user",
                "content": user_message,
                "metadata": message_metadata or {},
                "created_at": datetime.now(UTC).isoformat(),
            }

            await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.CONVERSATION_MESSAGES)
                    .insert(user_message_data)
                    .execute()
                )
            )

            # Save the AI response message
            ai_message_data = {
                "conversation_id": conversation_id,
                "message_id": str(uuid.uuid4()),
                "role": "assistant",
                "content": ai_response,
                "metadata": message_metadata or {},
                "created_at": datetime.now(UTC).isoformat(),
            }

            await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.CONVERSATION_MESSAGES)
                    .insert(ai_message_data)
                    .execute()
                )
            )

            logger.info(f"Saved message for conversation {conversation_id}")

            return conversation_id

        except Exception as e:
            logger.error(f"Error saving conversation message: {e}")
            return None

    async def get_user_conversations(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get user's recent conversations."""
        if not validate_user_id(user_id):
            logger.error(f"Invalid user_id format: {user_id}")
            return []

        if not await db_rate_limiter.acquire("read"):
            logger.warning("Rate limited: get_user_conversations")
            return []

        try:
            response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.CONVERSATIONS)
                    .select("*")
                    .eq("user_id", user_id)
                    .eq("is_archived", False)
                    .order("updated_at", desc=True)
                    .limit(limit)
                    .execute()
                )
            )

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []

    async def archive_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Archive a conversation."""
        if not validate_user_id(user_id) or not validate_conversation_id(conversation_id):
            logger.error("Invalid user_id or conversation_id format")
            return False

        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: archive_conversation")
            return False

        try:
            await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.CONVERSATIONS)
                    .update({"is_archived": True, "updated_at": datetime.now(UTC).isoformat()})
                    .eq("id", conversation_id)
                    .eq("user_id", user_id)
                    .execute()
                )
            )

            logger.info(f"Archived conversation {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error archiving conversation: {e}")
            return False

    async def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Delete a conversation and all its messages."""
        if not validate_user_id(user_id) or not validate_conversation_id(conversation_id):
            logger.error("Invalid user_id or conversation_id format")
            return False

        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: delete_conversation")
            return False

        try:
            # Delete all messages in the conversation
            await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.CONVERSATION_MESSAGES)
                    .delete()
                    .eq("conversation_id", conversation_id)
                    .execute()
                )
            )

            # Delete the conversation
            await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.CONVERSATIONS)
                    .delete()
                    .eq("id", conversation_id)
                    .eq("user_id", user_id)
                    .execute()
                )
            )

            logger.info(f"Deleted conversation {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
