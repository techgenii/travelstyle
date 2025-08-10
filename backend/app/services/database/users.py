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
User-related database operations for TravelStyle AI application.
"""

import asyncio
import logging
from datetime import UTC, datetime

from app.services.database.constants import DatabaseTables
from app.services.database.validators import (
    validate_profile_data,
    validate_user_id,
)
from app.services.rate_limiter import db_rate_limiter

logger = logging.getLogger(__name__)


class UserOperations:
    """Handles user-related database operations."""

    def __init__(self, client):
        self.client = client

    async def get_user_profile(self, user_id: str) -> dict:
        """Retrieve user profile from user_profile_view."""
        if not validate_user_id(user_id):
            logger.error(f"Invalid user_id format: {user_id}")
            return {}

        if not await db_rate_limiter.acquire("read"):
            logger.warning("Rate limited: get_user_profile")
            return {}

        try:
            # First try to get from user_profile_view
            response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.USER_PROFILE_VIEW)
                    .select("*")
                    .eq("id", user_id)
                    .execute()
                )
            )

            if response.data:
                return response.data[0]

            # If user_profile_view returns no data, fall back to basic user data
            logger.info(
                f"User profile view returned no data for user {user_id}, falling back to basic user query"
            )

            # Get basic user data from users table
            user_response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.USERS).select("*").eq("id", user_id).execute()
                )
            )

            if not user_response.data:
                logger.error(f"User {user_id} not found in users table")
                return {}

            user_data = user_response.data[0]

            # Get user preferences if they exist
            prefs_response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.USER_PREFERENCES)
                    .select("*")
                    .eq("user_id", user_id)
                    .execute()
                )
            )

            preferences_data = prefs_response.data[0] if prefs_response.data else {}

            # Combine user data with preferences
            profile_data = {
                **user_data,
                "style_preferences": preferences_data.get("style_preferences", {}),
                "size_info": preferences_data.get("size_info", {}),
                "travel_patterns": preferences_data.get("travel_patterns", {}),
                "quick_reply_preferences": preferences_data.get("quick_reply_preferences", {}),
                "packing_methods": preferences_data.get("packing_methods", {}),
                "currency_preferences": preferences_data.get("currency_preferences", {}),
                "selected_style_names": preferences_data.get("style_preferences", {}).get(
                    "selected_styles", []
                ),
            }

            return profile_data

        except Exception as e:
            logger.error(f"Error retrieving user profile: {e}")
            return {}

    async def save_user_profile(self, user_id: str, profile_data: dict) -> dict | None:
        """Save user profile data using the user_profile_view."""
        if not validate_user_id(user_id):
            logger.error(f"Invalid user_id format: {user_id}")
            return None

        if not validate_profile_data(profile_data):
            logger.error("Invalid profile data format")
            return None

        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: save_user_profile")
            return None

        try:
            # Check if user exists
            user_response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.USERS).select("id").eq("id", user_id).execute()
                )
            )

            if not user_response.data:
                logger.error(f"User {user_id} not found")
                return None

            # Add updated_at timestamp
            profile_data["updated_at"] = datetime.now(UTC).isoformat()

            # Update through the user_profile_view - the triggers will handle data separation
            response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.USER_PROFILE_VIEW)
                    .update(profile_data)
                    .eq("id", user_id)
                    .execute()
                )
            )

            if response.data:
                logger.info(f"Updated profile for user {user_id} via user_profile_view")
                return response.data[0]
            else:
                logger.error(f"Failed to update profile for user {user_id}")
                return None

        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return None

    async def update_user_preferences(self, user_id: str, preferences: dict) -> bool:
        """Update user preferences."""
        if not validate_user_id(user_id):
            logger.error(f"Invalid user_id format: {user_id}")
            return False

        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: update_user_preferences")
            return False

        try:
            # Check if preferences exist
            existing_response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.USER_PREFERENCES)
                    .select("id")
                    .eq("user_id", user_id)
                    .execute()
                )
            )

            # Prepare the update data with proper field names
            update_data = {
                "updated_at": datetime.now(UTC).isoformat(),
            }

            # Map preference keys to the correct column names
            if "style_preferences" in preferences:
                update_data["style_preferences"] = preferences["style_preferences"]
            if "size_info" in preferences:
                update_data["size_info"] = preferences["size_info"]
            if "travel_patterns" in preferences:
                update_data["travel_patterns"] = preferences["travel_patterns"]
            if "quick_reply_preferences" in preferences:
                update_data["quick_reply_preferences"] = preferences["quick_reply_preferences"]
            if "packing_methods" in preferences:
                update_data["packing_methods"] = preferences["packing_methods"]
            if "currency_preferences" in preferences:
                update_data["currency_preferences"] = preferences["currency_preferences"]

            if existing_response.data:
                # Update existing preferences
                await asyncio.to_thread(
                    lambda: (
                        self.client.table(DatabaseTables.USER_PREFERENCES)
                        .update(update_data)
                        .eq("user_id", user_id)
                        .execute()
                    )
                )
            else:
                # Create new preferences with default values
                insert_data = {
                    "user_id": user_id,
                    "style_preferences": preferences.get("style_preferences", {}),
                    "size_info": preferences.get("size_info", {}),
                    "travel_patterns": preferences.get("travel_patterns", {}),
                    "quick_reply_preferences": preferences.get(
                        "quick_reply_preferences", {"enabled": True}
                    ),
                    "packing_methods": preferences.get("packing_methods", {}),
                    "currency_preferences": preferences.get("currency_preferences", {}),
                    "created_at": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat(),
                }
                await asyncio.to_thread(
                    lambda: (
                        self.client.table(DatabaseTables.USER_PREFERENCES)
                        .insert(insert_data)
                        .execute()
                    )
                )

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
        """Save recommendation feedback."""
        if not validate_user_id(user_id):
            logger.error(f"Invalid user_id format: {user_id}")
            return False

        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: save_recommendation_feedback")
            return False

        try:
            feedback_data = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_id": message_id,
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "ai_response_content": ai_response_content,
                "created_at": datetime.now(UTC).isoformat(),
            }

            await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.RESPONSE_FEEDBACK)
                    .insert(feedback_data)
                    .execute()
                )
            )

            logger.info(f"Saved feedback for message {message_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving recommendation feedback: {e}")
            return False

    async def save_destination(
        self, user_id: str, destination_name: str, destination_data: dict | None = None
    ) -> bool:
        """Save user destination."""
        if not validate_user_id(user_id):
            logger.error(f"Invalid user_id format: {user_id}")
            return False

        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: save_destination")
            return False

        try:
            # Check if destination already exists
            existing_response = await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.USER_DESTINATIONS)
                    .select("id")
                    .eq("user_id", user_id)
                    .eq("destination_name", destination_name)
                    .execute()
                )
            )

            if existing_response.data:
                # Update existing destination
                await asyncio.to_thread(
                    lambda: (
                        self.client.table(DatabaseTables.USER_DESTINATIONS)
                        .update(
                            {
                                "destination_data": destination_data or {},
                                "updated_at": datetime.now(UTC).isoformat(),
                            }
                        )
                        .eq("user_id", user_id)
                        .eq("destination_name", destination_name)
                        .execute()
                    )
                )
            else:
                # Create new destination
                await asyncio.to_thread(
                    lambda: (
                        self.client.table(DatabaseTables.USER_DESTINATIONS)
                        .insert(
                            {
                                "user_id": user_id,
                                "destination_name": destination_name,
                                "destination_data": destination_data or {},
                                "created_at": datetime.now(UTC).isoformat(),
                                "updated_at": datetime.now(UTC).isoformat(),
                            }
                        )
                        .execute()
                    )
                )

            logger.info(f"Saved destination {destination_name} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving destination: {e}")
            return False

    async def update_user_profile_picture_url(self, user_id: str, profile_picture_url: str) -> bool:
        """Update user's profile picture URL."""
        if not validate_user_id(user_id):
            logger.error(f"Invalid user_id format: {user_id}")
            return False

        if not await db_rate_limiter.acquire("write"):
            logger.warning("Rate limited: update_user_profile_picture_url")
            return False

        try:
            await asyncio.to_thread(
                lambda: (
                    self.client.table(DatabaseTables.USERS)
                    .update(
                        {
                            "profile_picture_url": profile_picture_url,
                            "updated_at": datetime.now(UTC).isoformat(),
                        }
                    )
                    .eq("id", user_id)
                    .execute()
                )
            )

            logger.info(f"Updated profile picture for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating profile picture: {e}")
            return False
