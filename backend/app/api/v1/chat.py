"""
Chat API endpoints for TravelStyle AI application.
Handles conversation management and AI-powered travel recommendations.
"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.responses import ChatRequest, ChatResponse, ConversationContext
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
        # Get conversation history (implement based on your storage)
        conversation_history = await get_conversation_history(
            user_id=current_user["id"], conversation_id=request.conversation_id
        )

        # Get user profile
        user_profile = await get_user_profile(current_user["id"])

        # Generate response using orchestrator
        response = await orchestrator_service.generate_travel_recommendations(
            user_message=request.message,
            context=request.context or ConversationContext(user_id=current_user["id"]),
            conversation_history=conversation_history,
            user_profile=user_profile,
        )

        # Save conversation in background
        background_tasks.add_task(
            save_conversation_message,
            user_id=current_user["id"],
            conversation_id=request.conversation_id,
            user_message=request.message,
            ai_response=response.message,
        )

        return response

    except Exception as e:
        logger.error("Chat endpoint error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to process chat request") from e


@router.get("/conversations/{conversation_id}/history")
async def get_conversation(conversation_id: str, current_user: dict = current_user_dependency):
    """Get conversation history"""

    try:
        history = await get_conversation_history(
            user_id=current_user["id"], conversation_id=conversation_id
        )

        return {"conversation_id": conversation_id, "history": history}

    except Exception as e:
        logger.error("Get conversation error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation") from e


# Helper functions (implement based on your database)
async def get_conversation_history(user_id: str, conversation_id: str | None) -> list[dict]:  # pylint: disable=unused-argument
    """Retrieve conversation history from database"""
    # Implement based on your database choice
    return []


async def get_user_profile(user_id: str) -> dict:  # pylint: disable=unused-argument
    """Retrieve user profile from database"""
    # Implement based on your database choice
    return {}


async def save_conversation_message(
    user_id: str,  # pylint: disable=unused-argument
    conversation_id: str | None,  # pylint: disable=unused-argument
    user_message: str,  # pylint: disable=unused-argument
    ai_response: str,  # pylint: disable=unused-argument
):
    """Save conversation message to database"""
    # Implement based on your database choice
