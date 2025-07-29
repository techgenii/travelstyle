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
User management API endpoints for TravelStyle AI application.
Handles user profiles, preferences, and saved destinations.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import UserProfileBase, UserProfileResponse
from app.services.database_helpers import db_helpers

router = APIRouter()
logger = logging.getLogger(__name__)

# Local dependency to avoid linter warnings
current_user_dependency = Depends(get_current_user)


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user: dict = current_user_dependency):
    """
    Get current user profile information.

    Returns profile data for the authenticated user from the user_profile_view.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        profile = await db_helpers.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get user profile error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile",
        ) from e


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    profile_update: UserProfileBase, current_user: dict = current_user_dependency
):
    """
    Update the current user's profile using the user_profile_view.

    Supports updating:
    - Basic profile fields (first_name, last_name, etc.)
    - Style preferences (selected_style_names)
    - Other profile-related fields

    The user_profile_view uses database triggers to update underlying tables.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        update_data = profile_update.model_dump(exclude_unset=True)

        # Validate that we have data to update
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields to update"
            )

        result = await db_helpers.save_user_profile(user_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found or update failed",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Update user profile error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile",
        ) from e


@router.get("/preferences")
async def get_current_user_preferences(current_user: dict = current_user_dependency):
    """
    Get user preferences.

    Returns user preferences including style preferences, travel patterns, and size info.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        prefs = get_preferences_data(user_id)
        return {
            "style_preferences": prefs.get("style_preferences", {}),
            "travel_patterns": prefs.get("travel_patterns", {}),
            "size_info": prefs.get("size_info", {}),
            "quick_reply_preferences": prefs.get("quick_reply_preferences", {}),
            "packing_methods": prefs.get("packing_methods", {}),
            "currency_preferences": prefs.get("currency_preferences", {}),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get user preferences error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user preferences",
        ) from e


@router.put("/preferences")
async def update_user_preferences_endpoint(
    preferences: dict[str, Any],
    current_user: dict = current_user_dependency,
):
    """
    Update user preferences.

    Updates user preference data including style preferences, travel patterns,
    size info, and other user-specific settings.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        # Validate that preferences is not empty
        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Preferences data is required"
            )

        # Only allow updating specific preference fields
        allowed_preferences = {
            "style_preferences": preferences.get("style_preferences"),
            "size_info": preferences.get("size_info"),
            "travel_patterns": preferences.get("travel_patterns"),
            "quick_reply_preferences": preferences.get("quick_reply_preferences"),
            "packing_methods": preferences.get("packing_methods"),
            "currency_preferences": preferences.get("currency_preferences"),
        }

        # Remove None values
        allowed_preferences = {k: v for k, v in allowed_preferences.items() if v is not None}

        if not allowed_preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid preference fields to update",
            )

        success = await db_helpers.update_user_preferences(user_id, allowed_preferences)
        if success:
            return {
                "message": "Preferences updated successfully",
                "user_id": user_id,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Update user preferences error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user preferences",
        ) from e


@router.post("/destinations/save")
async def save_destination_endpoint(
    destination_data: dict, current_user: dict = current_user_dependency
):
    """
    Save a destination to user's favorites.

    Saves destination information to the user's saved destinations list.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        # Validate required fields
        if "destination_name" not in destination_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="destination_name is required"
            )

        success = await db_helpers.save_destination(
            user_id=user_id,
            destination_name=destination_data["destination_name"],
            destination_data=destination_data.get("destination_data", {}),
        )
        if success:
            return {"message": "Destination saved successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save destination",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Save destination error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save destination",
        ) from e


def get_preferences_data(user_id=None):
    """Helper function to get user preferences data."""
    # Try to fetch real preferences if user_id is provided
    if user_id:
        try:
            prefs = db_helpers.get_user_preferences(user_id)
            if prefs:
                return prefs
        except Exception as e:
            logger.error("Error fetching user preferences for user_id %s: %s", user_id, e)
    # Fallback/default
    return {
        "style_preferences": {},
        "travel_patterns": {},
        "size_info": {},
        "quick_reply_preferences": {},
        "packing_methods": {},
        "currency_preferences": {},
    }
