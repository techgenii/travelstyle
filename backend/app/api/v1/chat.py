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
Chat API endpoints for TravelStyle AI application.
Handles conversation management and AI-powered travel recommendations.
"""

import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.responses import ChatRequest, ChatResponse, ConversationContext
from app.services.database_helpers import db_helpers
from app.services.orchestrator import orchestrator_service
from app.utils.rate_limiter import rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)

# Local dependency to avoid linter warnings
current_user_dependency = Depends(get_current_user)


@router.post("/", response_model=ChatResponse)
@rate_limit(calls=30, period=60)  # 30 calls per minute
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = current_user_dependency,
):
    """
    Main chat endpoint for travel recommendations
    """

    try:
        # Get conversation history
        conversation_history = await db_helpers.get_conversation_history(
            user_id=current_user["id"], conversation_id=request.conversation_id
        )

        # Get user profile
        user_profile = await db_helpers.get_user_profile(current_user["id"])

        # Generate response using orchestrator
        response = await orchestrator_service.generate_travel_recommendations(
            user_message=request.message,
            context=request.context or ConversationContext(user_id=current_user["id"]),
            conversation_history=conversation_history,
            user_profile=user_profile,
        )

        # Save conversation in background
        background_tasks.add_task(
            db_helpers.save_conversation_message,
            user_id=current_user["id"],
            conversation_id=request.conversation_id,
            user_message=request.message,
            ai_response=response.message,
        )

        return response

    except Exception as e:
        logger.error("Chat endpoint error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to process chat request") from e


@router.get("/dialog/{conversation_id}/history")
async def get_conversation(conversation_id: str, current_user: dict = current_user_dependency):
    """Get conversation history"""

    try:
        history = await db_helpers.get_conversation_history(
            user_id=current_user["id"], conversation_id=conversation_id
        )

        return {"conversation_id": conversation_id, "history": history}

    except Exception as e:
        logger.error("Get conversation error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to retrieve dialog") from e


@router.get("/dialog")
async def get_user_conversations_endpoint(current_user: dict = current_user_dependency):
    """Get all user conversations"""
    try:
        conversations = await db_helpers.get_user_conversations(current_user["id"])
        return {"conversations": conversations}
    except Exception as e:
        logger.error("Get conversations error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to retrieve conversations") from e


@router.delete("/dialog/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: str, current_user: dict = current_user_dependency
):
    """Delete a conversation"""
    try:
        success = await db_helpers.delete_conversation(current_user["id"], conversation_id)
        if success:
            return {"message": "Conversation deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete conversation")
    except Exception as e:
        logger.error("Delete conversation error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to delete conversation") from e


@router.put("/dialog/{conversation_id}/archive")
async def archive_conversation_endpoint(
    conversation_id: str, current_user: dict = current_user_dependency
):
    """Archive a conversation"""
    try:
        success = await db_helpers.archive_conversation(current_user["id"], conversation_id)
        if success:
            return {"message": "Conversation archived successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to archive conversation")
    except Exception as e:
        logger.error("Archive conversation error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to archive conversation") from e


@router.post("/start")
async def start_conversation_endpoint(
    conversation_data: dict = None, current_user: dict = current_user_dependency
):
    """Start a new conversation without sending an initial message

    Creates a conversation and returns the conversation_id for future messages.
    """
    try:
        # Use empty dict if no data provided
        if conversation_data is None:
            conversation_data = {}

        # Auto-generate conversation_id if not provided
        conversation_id = conversation_data.get("conversation_id") or str(uuid.uuid4())

        # Create conversation with minimal data
        conversation = await db_helpers.create_chat_session(
            user_id=current_user["id"],
            conversation_id=conversation_id,
            destination=conversation_data.get("destination"),
        )

        return {
            "conversation_id": conversation_id,
            "conversation": conversation,
            "message": "Conversation started successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Start conversation error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to start conversation") from e


@router.post("/sessions/create")
async def create_session_endpoint(session_data: dict, current_user: dict = current_user_dependency):
    """Create a new chat session

    If conversation_id is not provided, one will be auto-generated.
    Returns the created session along with the conversation_id.
    """
    try:
        # Validate required fields
        if not session_data:
            raise HTTPException(status_code=400, detail="Session data is required")

        # Auto-generate conversation_id if not provided
        conversation_id = session_data.get("conversation_id") or str(uuid.uuid4())

        session = await db_helpers.create_chat_session(
            user_id=current_user["id"],
            conversation_id=conversation_id,
            destination=session_data.get("destination"),
        )
        return {"session": session, "conversation_id": conversation_id}
    except HTTPException:
        raise
    except KeyError as e:
        # Convert KeyError to proper HTTP error
        logger.error("Create session KeyError: %s", e)
        raise HTTPException(status_code=400, detail=f"Missing required field: {e}") from e
    except Exception as e:
        logger.error("Create session error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to create session") from e


@router.post("/feedback")
async def save_feedback_endpoint(feedback_data: dict, current_user: dict = current_user_dependency):
    """Save user feedback endpoint"""
    try:
        # Validate required fields
        required_fields = ["conversation_id", "message_id", "feedback_type"]
        missing_fields = [field for field in required_fields if field not in feedback_data]
        if missing_fields:
            raise HTTPException(
                status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}"
            )

        success = await db_helpers.save_recommendation_feedback(
            user_id=current_user["id"],
            conversation_id=feedback_data["conversation_id"],
            message_id=feedback_data["message_id"],
            feedback_type=feedback_data["feedback_type"],
            feedback_text=feedback_data.get("feedback_text"),
            ai_response_content=feedback_data.get("ai_response_content"),
        )
        if success:
            return {"message": "Feedback saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save feedback")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Save feedback error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to save feedback") from e
