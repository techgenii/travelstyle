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
"""

import logging
import uuid
from datetime import UTC, datetime

from app.core.config import settings
from supabase import Client, create_client

logger = logging.getLogger(__name__)


class DatabaseHelpers:
    """Database helper class for conversation and user management"""

    def __init__(self, supabase_client: Client | None = None):
        # Fix: Use the provided client or create a new one
        if supabase_client:
            self.client = supabase_client
        else:
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    async def get_conversation_history(
        self, user_id: str, conversation_id: str | None
    ) -> list[dict]:
        """Retrieve conversation history from database"""
        try:
            if conversation_id:
                # Get messages for a specific conversation
                response = (
                    self.client.table("conversation_messages")
                    .select("*")
                    .eq("conversation_id", conversation_id)
                    .order("created_at", desc=False)
                    .execute()
                )

                return response.data if response.data else []
            else:
                # Get recent conversations for the user
                conversations_response = (
                    self.client.table("conversations")
                    .select("id, title, messages, created_at, updated_at")
                    .eq("user_id", user_id)
                    .eq("is_archived", False)
                    .order("updated_at", desc=True)
                    .limit(10)
                    .execute()
                )

                return conversations_response.data if conversations_response.data else []

        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []

    async def get_user_profile(self, user_id: str) -> dict:
        """Retrieve user profile from user_profile_view"""
        try:
            response = (
                self.client.table("user_profile_view").select("*").eq("id", user_id).execute()
            )
            if not response.data or len(response.data) == 0:
                return {}
            return response.data[0]
        except Exception as e:
            logger.error(f"Error retrieving user profile: {e}")
            return {}

    async def save_user_profile(self, user_id: str, profile_data: dict) -> dict | None:
        """Save user profile data via user_profile_view.

        This function updates the user_profile_view directly, which uses database
        triggers to update the underlying users and user_preferences tables.

        Args:
            user_id: The user ID to update
            profile_data: Dictionary containing profile fields to update

        Returns:
            Updated profile data or None if error
        """
        try:
            # First, check if the user exists in the users table
            user_response = self.client.table("users").select("id").eq("id", user_id).execute()

            if not user_response.data or len(user_response.data) == 0:
                logger.error(f"User {user_id} not found in users table")
                return None

            # Ensure user_preferences record exists
            preferences_response = (
                self.client.table("user_preferences")
                .select("user_id")
                .eq("user_id", user_id)
                .execute()
            )

            if not preferences_response.data or len(preferences_response.data) == 0:
                # Create user_preferences record if it doesn't exist
                logger.info(f"Creating user_preferences record for user {user_id}")
                self.client.table("user_preferences").insert(
                    {
                        "user_id": user_id,
                        "style_preferences": {},
                        "size_info": {},
                        "travel_patterns": {},
                        "quick_reply_preferences": {"enabled": True},
                        "packing_methods": {},
                        "currency_preferences": {},
                    }
                ).execute()

            # Update the user_profile_view
            response = (
                self.client.table("user_profile_view")
                .update(profile_data)
                .eq("id", user_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                logger.info(f"Successfully updated profile for user {user_id}")
                return response.data[0]
            else:
                logger.warning(f"No profile found for user {user_id} in user_profile_view")
                return None

        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return None

    async def save_conversation_message(
        self,
        user_id: str,
        conversation_id: str | None,
        user_message: str,
        ai_response: str,
        conversation_type: str = "mixed",
        message_metadata: dict | None = None,
    ):
        """Save conversation message to database"""
        try:
            # Create conversation if it doesn't exist
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                conversation_data = {
                    "id": conversation_id,
                    "user_id": user_id,
                    "title": user_message[:50] + "..." if len(user_message) > 50 else user_message,
                    "messages": 1,
                    "conversation_type": conversation_type,
                    "created_at": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat(),
                }

                self.client.table("conversations").insert(conversation_data).execute()
            else:
                # Update existing conversation
                self.client.table("conversations").update(
                    {
                        "messages": self.client.rpc(
                            "increment_messages", {"conv_id": conversation_id}
                        ),
                        "updated_at": datetime.now(UTC).isoformat(),
                    }
                ).eq("id", conversation_id).execute()

            # Save the message
            message_data = {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "message_metadata": message_metadata or {},
                "created_at": datetime.now(UTC).isoformat(),
            }

            self.client.table("conversation_messages").insert(message_data).execute()

            logger.info(f"Saved message for conversation {conversation_id}")
            return conversation_id

        except Exception as e:
            logger.error(f"Error saving conversation message: {e}")
            return None

    async def create_chat_session(
        self, user_id: str, conversation_id: str, destination: str | None = None
    ) -> dict:
        """Create a new chat session"""
        try:
            session_data = {
                "id": conversation_id,
                "user_id": user_id,
                "destination": destination,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }

            response = self.client.table("conversations").insert(session_data).execute()

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

    async def update_user_preferences(self, user_id: str, preferences: dict) -> bool:
        """Update user preferences"""
        try:
            self.client.table("user_preferences").update(preferences).eq(
                "user_id", user_id
            ).execute()
            logger.info(f"Updated preferences for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False

    async def save_recommendation_feedback(
        self,
        user_id: str,
        conversation_id: str,
        message_id: str,
        feedback_type: str,
        feedback_text: str | None = None,
        ai_response_content: str | None = None,
    ) -> bool:
        """Save user feedback on AI responses"""
        try:
            feedback_data = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_id": message_id,
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "ai_response_content": ai_response_content,
                "created_at": datetime.now(UTC),
            }

            self.client.table("recommendation_feedback").insert(feedback_data).execute()
            logger.info(f"Saved feedback for message {message_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving recommendation feedback: {e}")
            return False

    async def save_destination(
        self, user_id: str, destination_name: str, destination_data: dict | None = None
    ) -> bool:
        """Save destination information for a user"""
        try:
            destination_record = {
                "user_id": user_id,
                "destination_name": destination_name,
                "destination_data": destination_data or {},
                "created_at": datetime.now(UTC),
            }

            # Check if destination already exists for this user
            existing = (
                self.client.table("user_destinations")
                .select("*")
                .eq("user_id", user_id)
                .eq("destination_name", destination_name)
                .execute()
            )

            if existing.data:
                # Update existing destination
                self.client.table("user_destinations").update(destination_record).eq(
                    "user_id", user_id
                ).eq("destination_name", destination_name).execute()
            else:
                # Insert new destination
                self.client.table("user_destinations").insert(destination_record).execute()

            logger.info(f"Saved destination {destination_name} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving destination: {e}")
            return False

    async def get_user_conversations(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get user's recent conversations"""
        try:
            response = (
                self.client.table("conversations")
                .select("id, title, messages, created_at, updated_at, destination")
                .eq("user_id", user_id)
                .eq("is_archived", False)
                .order("updated_at", desc=True)
                .limit(limit)
                .execute()
            )

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error retrieving user conversations: {e}")
            return []

    async def archive_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Archive a conversation"""
        try:
            self.client.table("conversations").update(
                {"is_archived": True, "updated_at": datetime.now(UTC)}
            ).eq("id", conversation_id).eq("user_id", user_id).execute()

            logger.info(f"Archived conversation {conversation_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error archiving conversation: {e}")
            return False

    async def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        try:
            # Delete messages first (due to foreign key constraints)
            self.client.table("conversation_messages").delete().eq(
                "conversation_id", conversation_id
            ).execute()

            # Delete conversation
            self.client.table("conversations").delete().eq("id", conversation_id).eq(
                "user_id", user_id
            ).execute()

            logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False

    async def update_user_profile_picture_url(self, user_id: str, profile_picture_url: str) -> bool:
        """Update just the profile picture URL in the users table."""
        try:
            # Update the users table directly
            response = (
                self.client.table("users")
                .update({"profile_picture_url": profile_picture_url})
                .eq("id", user_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                logger.info(f"Successfully updated profile picture URL for user {user_id}")
                return True
            else:
                logger.warning(f"No user found for user {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error updating profile picture URL: {e}")
            return False


# Create a singleton instance
db_helpers = DatabaseHelpers()
