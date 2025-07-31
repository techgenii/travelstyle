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
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


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
