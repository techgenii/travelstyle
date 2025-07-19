"""
Response models for TravelStyle AI application.
Defines Pydantic models for API requests and responses.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class QuickReply(BaseModel):
    """Quick reply option for chat responses."""

    text: str
    action: str | None = None


class ChatResponse(BaseModel):
    """Response model for chat interactions."""

    message: str
    quick_replies: list[QuickReply] = []
    suggestions: list[str] = []
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConversationContext(BaseModel):
    """Context information for conversation state."""

    user_id: str
    destination: str | None = None
    travel_dates: list[str] | None = None
    trip_purpose: str | None = None
    style_preferences: dict[str, Any] | None = None
    budget_range: str | None = None


class ChatRequest(BaseModel):
    """Request model for chat interactions."""

    message: str
    context: ConversationContext | None = None
    conversation_id: str | None = None
