"""
User-related models for TravelStyle AI application.
Defines Pydantic models for user profiles, preferences, and activity tracking.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, EmailStr

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

class UserProfile(BaseModel):
    """User profile information"""
    id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None

class UserPreferences(BaseModel):
    """User preferences for travel and style"""
    user_id: str
    style_preferences: Optional[Dict[str, Any]] = None
    size_info: Optional[Dict[str, Any]] = None
    travel_patterns: Optional[Dict[str, Any]] = None
    preferred_packing_methods: Optional[List[str]] = None
    budget_preferences: Optional[Dict[str, Any]] = None
    climate_preferences: Optional[Dict[str, Any]] = None
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
    last_used: Optional[datetime] = None

class UserActivity(BaseModel):
    """User activity tracking"""
    activity_id: str
    user_id: str
    activity_type: str  # "login", "chat", "recommendation", "preference_update"
    description: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class UserSession(BaseModel):
    """User session information"""
    session_id: str
    user_id: str
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
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
    comment: Optional[str] = None
    helpful: Optional[bool] = None
    created_at: datetime

class UserUsageStats(BaseModel):
    """User usage statistics"""
    user_id: str
    total_chat_sessions: int = 0
    total_recommendations: int = 0
    total_currency_conversions: int = 0
    favorite_destinations: Optional[List[str]] = None
    most_used_packing_method: Optional[str] = None
    last_activity: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
