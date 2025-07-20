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
        """Retrieve user profile from database"""
        try:
            # Get user basic info
            user_response = self.client.table("users").select("*").eq("id", user_id).execute()

            if not user_response.data:
                return {}

            user_data = user_response.data[0]

            # Get user preferences
            preferences_response = (
                self.client.table("user_preferences").select("*").eq("user_id", user_id).execute()
            )

            # Get saved destinations
            destinations_response = (
                self.client.table("saved_destinations")
                .select("*")
                .eq("user_id", user_id)
                .order("last_used", desc=True)
                .execute()
            )

            # Get currency favorites
            currency_favorites_response = (
                self.client.table("currency_favorites")
                .select("*")
                .eq("user_id", user_id)
                .order("last_used", desc=True)
                .execute()
            )

            # Combine all data into user profile
            profile = {
                "id": user_data["id"],
                "email": user_data["email"],
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "profile_completed": user_data.get("profile_completed", False),
                "last_login": user_data.get("last_login"),
                "preferences": user_data.get("preferences", {}),
                "ui_preferences": user_data.get("ui_preferences", {}),
                "created_at": user_data["created_at"],
                "updated_at": user_data["updated_at"],
            }

            # Add detailed preferences if available
            if preferences_response.data:
                pref_data = preferences_response.data[0]
                profile["detailed_preferences"] = {
                    "style_preferences": pref_data.get("style_preferences", {}),
                    "size_info": pref_data.get("size_info", {}),
                    "travel_patterns": pref_data.get("travel_patterns", {}),
                    "quick_reply_preferences": pref_data.get("quick_reply_preferences", {}),
                    "packing_methods": pref_data.get("packing_methods", {}),
                    "currency_preferences": pref_data.get("currency_preferences", {}),
                }

            # Add saved destinations
            if destinations_response.data:
                profile["saved_destinations"] = destinations_response.data

            # Add currency favorites
            if currency_favorites_response.data:
                profile["currency_favorites"] = currency_favorites_response.data

            return profile

        except Exception as e:
            logger.error(f"Error retrieving user profile: {e}")
            return {}

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
            current_time = datetime.now(UTC)

            # If no conversation_id provided, create a new conversation
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

                # Create new conversation
                conversation_data = {
                    "id": conversation_id,
                    "user_id": user_id,
                    "type": conversation_type,
                    "title": user_message[:100] + "..."
                    if len(user_message) > 100
                    else user_message,
                    "messages": [],
                    "created_at": current_time,
                    "updated_at": current_time,
                }

                self.client.table("conversations").insert(conversation_data).execute()

            # Generate message IDs
            user_message_id = str(uuid.uuid4())
            ai_message_id = str(uuid.uuid4())

            # Prepare message data
            messages_to_insert = [
                {
                    "id": str(uuid.uuid4()),
                    "conversation_id": conversation_id,
                    "message_id": user_message_id,
                    "role": "user",
                    "content": user_message,
                    "metadata": message_metadata or {},
                    "message_type": "text",
                    "created_at": current_time,
                },
                {
                    "id": str(uuid.uuid4()),
                    "conversation_id": conversation_id,
                    "message_id": ai_message_id,
                    "role": "assistant",
                    "content": ai_response,
                    "metadata": message_metadata or {},
                    "message_type": "text",
                    "created_at": current_time,
                },
            ]

            # Insert messages
            self.client.table("conversation_messages").insert(messages_to_insert).execute()

            # Update conversation's updated_at timestamp
            self.client.table("conversations").update({"updated_at": current_time}).eq(
                "id", conversation_id
            ).execute()

            logger.info(
                f"Saved conversation message for user {user_id}, conversation {conversation_id}"
            )

            return {
                "conversation_id": conversation_id,
                "user_message_id": user_message_id,
                "ai_message_id": ai_message_id,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error saving conversation message: {e}")
            return {"success": False, "error": str(e)}

    async def create_chat_session(
        self, user_id: str, conversation_id: str, destination: str | None = None
    ) -> dict:
        """Create a new chat session"""
        try:
            session_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "conversation_id": conversation_id,
                "destination": destination,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }

            response = self.client.table("chat_sessions").insert(session_data).execute()
            return response.data[0] if response.data else {}

        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            return {}

    async def update_user_preferences(self, user_id: str, preferences: dict) -> bool:
        """Update user preferences"""
        try:
            # Check if preferences exist
            existing = (
                self.client.table("user_preferences").select("id").eq("user_id", user_id).execute()
            )

            if existing.data:
                # Update existing preferences
                self.client.table("user_preferences").update(
                    {**preferences, "updated_at": datetime.now(UTC)}
                ).eq("user_id", user_id).execute()
            else:
                # Create new preferences
                pref_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    **preferences,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                }
                self.client.table("user_preferences").insert(pref_data).execute()

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
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_id": message_id,
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "ai_response_content": ai_response_content,
                "created_at": datetime.now(UTC),
            }

            self.client.table("response_feedback").insert(feedback_data).execute()
            logger.info(f"Saved feedback for user {user_id}, message {message_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return False

    async def save_destination(
        self, user_id: str, destination_name: str, destination_data: dict | None = None
    ) -> bool:
        """Save a destination to user's saved destinations"""
        try:
            # Check if destination already exists for user
            existing = (
                self.client.table("saved_destinations")
                .select("id, visit_count")
                .eq("user_id", user_id)
                .eq("destination_name", destination_name)
                .execute()
            )

            current_time = datetime.now(UTC)

            if existing.data:
                # Update existing destination
                current_count = existing.data[0]["visit_count"]
                self.client.table("saved_destinations").update(
                    {
                        "visit_count": current_count + 1,
                        "last_used": current_time,
                        "destination_data": destination_data or {},
                    }
                ).eq("id", existing.data[0]["id"]).execute()
            else:
                # Create new saved destination
                destination_record = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "destination_name": destination_name,
                    "destination_data": destination_data or {},
                    "visit_count": 1,
                    "last_used": current_time,
                    "created_at": current_time,
                }
                self.client.table("saved_destinations").insert(destination_record).execute()

            logger.info(f"Saved destination {destination_name} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving destination: {e}")
            return False

    async def get_user_conversations(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get all conversations for a user"""
        try:
            response = (
                self.client.table("conversations")
                .select("id, title, type, created_at, updated_at, destination")
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


# Create a singleton instance
db_helpers = DatabaseHelpers()


# Standalone functions that use the class instance
async def get_conversation_history(user_id: str, conversation_id: str | None) -> list[dict]:
    """Retrieve conversation history from database"""
    return await db_helpers.get_conversation_history(user_id, conversation_id)


async def get_user_profile(user_id: str) -> dict:
    """Retrieve user profile from database"""
    return await db_helpers.get_user_profile(user_id)


async def save_conversation_message(
    user_id: str,
    conversation_id: str | None,
    user_message: str,
    ai_response: str,
    conversation_type: str = "mixed",
    message_metadata: dict | None = None,
):
    """Save conversation message to database"""
    return await db_helpers.save_conversation_message(
        user_id, conversation_id, user_message, ai_response, conversation_type, message_metadata
    )


async def update_user_preferences(user_id: str, preferences: dict) -> bool:
    """Update user preferences"""
    return await db_helpers.update_user_preferences(user_id, preferences)


async def save_recommendation_feedback(
    user_id: str,
    conversation_id: str,
    message_id: str,
    feedback_type: str,
    feedback_text: str | None = None,
    ai_response_content: str | None = None,
) -> bool:
    """Save user feedback on AI responses"""
    return await db_helpers.save_recommendation_feedback(
        user_id, conversation_id, message_id, feedback_type, feedback_text, ai_response_content
    )
