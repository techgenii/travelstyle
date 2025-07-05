"""
Response models for TravelStyle AI application.
Defines Pydantic models for API requests and responses.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

class QuickReply(BaseModel):
    """Quick reply option for chat responses."""

    text: str
    action: Optional[str] = None

class ChatResponse(BaseModel):
    """Response model for chat interactions."""

    message: str
    quick_replies: List[QuickReply] = []
    suggestions: List[str] = []
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConversationContext(BaseModel):
    """Context information for conversation state."""

    user_id: str
    destination: Optional[str] = None
    travel_dates: Optional[List[str]] = None
    trip_purpose: Optional[str] = None
    style_preferences: Optional[Dict[str, Any]] = None
    budget_range: Optional[str] = None

class ChatRequest(BaseModel):
    """Request model for chat interactions."""

    message: str
    context: Optional[ConversationContext] = None
    conversation_id: Optional[str] = None
