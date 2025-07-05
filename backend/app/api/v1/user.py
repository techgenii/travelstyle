"""
User management API endpoints for TravelStyle AI application.
Handles user profiles and preferences management.
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends

from app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):  # pylint: disable=unused-argument
    """Get current user profile"""
    try:
        # In a real implementation, you'd fetch from Supabase
        return {
            "id": current_user["id"],
            "email": current_user.get("email"),
            "is_active": current_user.get("is_active", True)
        }
    except Exception as e:
        logger.error("Get user profile error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user profile"
        ) from e

@router.get("/preferences")
async def get_user_preferences(current_user: dict = Depends(get_current_user)):  # pylint: disable=unused-argument
    """Get user preferences"""
    try:
        # In a real implementation, you'd fetch from Supabase user_preferences table
        return {
            "style_preferences": {},
            "travel_patterns": {},
            "size_info": {}
        }
    except Exception as e:
        logger.error("Get user preferences error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user preferences"
        ) from e

@router.put("/preferences")
async def update_user_preferences(
    preferences: Dict[str, Any],  # pylint: disable=unused-argument
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        # In a real implementation, you'd update Supabase user_preferences table
        return {
            "message": "Preferences updated successfully",
            "user_id": current_user["id"]
        }
    except Exception as e:
        logger.error("Update user preferences error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to update user preferences"
        ) from e
