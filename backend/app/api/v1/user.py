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

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.api.deps import get_current_user
from app.models.user import UserProfileBase, UserProfileResponse
from app.services.cloudinary_service import CloudinaryService
from app.services.database_helpers import db_helpers

router = APIRouter()
logger = logging.getLogger(__name__)

# Local dependency to avoid linter warnings
current_user_dependency = Depends(get_current_user)

# Create a single instance of CloudinaryService to reuse across endpoints
cloudinary_service = CloudinaryService()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user: dict = current_user_dependency):
    """
    Get current user profile information.

    Returns profile data for the authenticated user from the user_profile_view.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            logger.error("Invalid user ID in current_user: %s", current_user)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        profile = await db_helpers.get_user_profile(user_id)

        if not profile:
            logger.error("User profile not found for user_id: %s", user_id)
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


@router.post("/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),  # noqa: B008
    current_user: dict = current_user_dependency,
):
    """
    Upload a profile picture for the current user.

    Accepts image files (JPEG, PNG, GIF) and automatically resizes them to 300x300 using Cloudinary.
    Returns the public URL of the uploaded image.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image (JPEG, PNG, GIF)",
            )

        # Validate file size (max 10MB for original upload, will be optimized by Cloudinary)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File size must be less than 10MB"
            )

        # Upload file using Cloudinary (automatically resizes to 300x300)
        public_url = await cloudinary_service.upload_profile_picture(
            user_id, file_content, file.filename
        )

        if not public_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload profile picture",
            )

        # Update user profile with new picture URL
        update_data = {"profile_picture_url": public_url}
        result = await db_helpers.save_user_profile(user_id, update_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile with new picture URL",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Profile picture uploaded and automatically resized to 300x300",
                "profile_picture_url": public_url,
                "image_size": "300x300",
                "processor": "Cloudinary",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Upload profile picture error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile picture",
        ) from e


@router.delete("/me/profile-picture")
async def delete_profile_picture(current_user: dict = current_user_dependency):
    """
    Delete the current user's profile picture.

    Removes the file from Supabase Storage and clears the profile_picture_url.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        # Get current profile to find existing picture URL
        profile = await db_helpers.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        current_picture_url = profile.get("profile_picture_url")

        if current_picture_url:
            # Delete from Cloudinary
            await cloudinary_service.delete_profile_picture(current_picture_url)

        # Clear the profile picture URL
        update_data = {"profile_picture_url": None}
        result = await db_helpers.save_user_profile(user_id, update_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear profile picture URL",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Profile picture deleted successfully"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delete profile picture error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile picture",
        ) from e


@router.get("/me/profile-picture/initials")
async def get_initials_avatar(current_user: dict = current_user_dependency):
    """
    Generate an initials avatar for the current user.

    Returns a base64 encoded image with the user's initials.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        # Get user profile
        profile = await db_helpers.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        first_name = profile.get("first_name", "")
        last_name = profile.get("last_name", "")

        # Generate initials avatar
        initials_avatar = cloudinary_service.generate_initials_avatar(first_name, last_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "initials_avatar": initials_avatar,
                "initials": (
                    f"{first_name[0] if first_name else ''}{last_name[0] if last_name else ''}"
                ),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get initials avatar error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate initials avatar",
        ) from e


@router.patch("/me/profile-picture-url")
async def update_profile_picture_url(
    profile_update: dict, current_user: dict = current_user_dependency
):
    """
    Update just the profile picture URL for the current user.
    This is a simpler endpoint that doesn't require the full user profile view.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

        profile_picture_url = profile_update.get("profile_picture_url")
        if not profile_picture_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Profile picture URL is required"
            )

        # Update just the profile picture URL in the users table
        result = await db_helpers.update_user_profile_picture_url(user_id, profile_picture_url)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile picture URL",
            )

        return {"message": "Profile picture URL updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Update profile picture URL error: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile picture URL",
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
