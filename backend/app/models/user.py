"""
User-related models for TravelStyle AI application.
Defines Pydantic models for user profiles, preferences, and activity tracking.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User roles for the application"""

    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"


class UserStatus(str, Enum):
    """User account status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


# Pydantic models
class UserProfileBase(BaseModel):
    first_name: str | None = Field(None, description="User's first name")
    last_name: str | None = Field(None, description="User's last name")
    profile_completed: bool | None = Field(
        None, description="Whether the user's profile is complete"
    )
    style_preferences: dict[str, Any] | None = Field(
        None, description="User's style preferences (e.g., colors, brands, etc.)"
    )
    size_info: dict[str, Any] | None = Field(
        None, description="User's size information (e.g., height, weight, measurements)"
    )
    travel_patterns: dict[str, Any] | None = Field(
        None, description="User's travel patterns (e.g., frequent destinations)"
    )
    quick_reply_preferences: dict[str, Any] | None = Field(
        None, description="User's quick reply preferences for chat"
    )
    packing_methods: dict[str, Any] | None = Field(
        None, description="User's preferred packing methods"
    )
    currency_preferences: dict[str, Any] | None = Field(
        None, description="User's currency preferences"
    )
    selected_style_names: list[str] | None = Field(
        None, description="List of selected style names for the user"
    )


class UserProfileResponse(UserProfileBase):
    """User profile response matching user_profile_view structure"""

    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    profile_picture_url: str | None = Field(None, description="URL to the user's profile picture")
    created_at: str | None = Field(None, description="Timestamp when the user was created")
    updated_at: str | None = Field(None, description="Timestamp when the user was last updated")
    last_login: str | None = Field(None, description="Timestamp of the user's last login")


class UserProfile(BaseModel):
    """User profile information"""

    id: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None
    preferences: dict[str, Any] | None = None


class UserPreferences(BaseModel):
    """User preferences for travel and style"""

    user_id: str
    style_preferences: dict[str, Any] | None = None
    size_info: dict[str, Any] | None = None
    travel_patterns: dict[str, Any] | None = None
    preferred_packing_methods: list[str] | None = None
    budget_preferences: dict[str, Any] | None = None
    climate_preferences: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class UserAuthToken(BaseModel):
    """JWT token information"""

    token_id: str
    user_id: str
    token_hash: str
    expires_at: datetime
    is_revoked: bool = False
    created_at: datetime
    last_used: datetime | None = None


class UserActivity(BaseModel):
    """User activity tracking"""

    activity_id: str
    user_id: str
    activity_type: str  # "login", "chat", "recommendation", "preference_update"
    description: str
    metadata: dict[str, Any] | None = None
    created_at: datetime


class UserSession(BaseModel):
    """User session information"""

    session_id: str
    user_id: str
    device_info: dict[str, Any] | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    is_active: bool = True
    created_at: datetime
    last_activity: datetime
    expires_at: datetime


class UserFeedback(BaseModel):
    """User feedback on recommendations"""

    feedback_id: str
    user_id: str
    recommendation_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    helpful: bool | None = None
    created_at: datetime


class UserUsageStats(BaseModel):
    """User usage statistics"""

    user_id: str
    total_chat_sessions: int = 0
    total_recommendations: int = 0
    total_currency_conversions: int = 0
    favorite_destinations: list[str] | None = None
    most_used_packing_method: str | None = None
    last_activity: datetime | None = None
    created_at: datetime
    updated_at: datetime
