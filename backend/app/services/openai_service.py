import openai
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import json
import logging
from app.core.config import settings
from app.models.responses import ChatResponse, QuickReply

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            organization=settings.OPENAI_ORG_ID
        )
        self.model = "gpt-4"
        self.temperature = 0.7
        self.max_tokens = 1000
        
    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        cultural_context: Optional[Dict[str, Any]] = None,
        weather_context: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Generate AI response with full context"""
        
        try:
            system_prompt = self._build_system_prompt()
            context_prompt = self._build_context_prompt(
                cultural_context, weather_context, user_profile
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": context_prompt}
            ]
            
            # Add conversation history (last 10 messages)
            messages.extend(conversation_history[-10:])
            messages.append({"role": "user", "content": user_message})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            ai_message = response.choices[0].message.content
            
            # Process response to extract quick replies and suggestions
            return self._process_response(ai_message)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return ChatResponse(
                message="I apologize, but I'm having trouble processing your request right now. Please try again.",
                confidence_score=0.0
            )
    
    def _build_system_prompt(self) -> str:
        return """
You are TravelStyle AI, an expert travel wardrobe consultant with cultural intelligence.

CAPABILITIES:
- Wardrobe planning with cultural awareness
- Local etiquette and dress code guidance  
- Weather-appropriate recommendations
- Currency conversion assistance

PERSONALITY:
- Friendly, professional, culturally sensitive
- Practical and actionable advice
- Concise but comprehensive responses

RESPONSE FORMAT:
- Always include cultural context when relevant
- Suggest quick-reply options when appropriate (format: [QUICK: option text])
- Reference weather conditions in recommendations
- Be specific about clothing items and styles

CULTURAL SENSITIVITY:
- Respect local customs and dress codes
- Provide context for cultural recommendations
- Avoid stereotypes, focus on practical guidance
- Include both traditional and modern perspectives

For quick replies, use format: [QUICK: "Tell me about colors"] [QUICK: "Show accessories"]
"""
    
    def _build_context_prompt(
        self,
        cultural_context: Optional[Dict[str, Any]],
        weather_context: Optional[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]]
    ) -> str:
        context_parts = ["CURRENT CONTEXT:"]
        
        if cultural_context:
            context_parts.append(f"Cultural insights: {json.dumps(cultural_context, indent=2)}")
        
        if weather_context:
            context_parts.append(f"Weather conditions: {json.dumps(weather_context, indent=2)}")
        
        if user_profile:
            context_parts.append(f"User preferences: {json.dumps(user_profile, indent=2)}")
        
        return "\n".join(context_parts)
    
    def _process_response(self, ai_message: str) -> ChatResponse:
        """Extract quick replies and clean up response"""
        
        # Extract quick replies
        quick_replies = []
        import re
        
        quick_reply_pattern = r'\[QUICK:\s*"([^"]+)"\]'
        matches = re.findall(quick_reply_pattern, ai_message)
        
        for match in matches:
            quick_replies.append(QuickReply(text=match))
        
        # Remove quick reply markers from message
        cleaned_message = re.sub(quick_reply_pattern, '', ai_message).strip()
        
        # Extract suggestions (simple heuristic)
        suggestions = []
        if "would you like" in cleaned_message.lower():
            suggestions.append("Get more details")
        if "also consider" in cleaned_message.lower():
            suggestions.append("Show alternatives")
        
        return ChatResponse(
            message=cleaned_message,
            quick_replies=quick_replies,
            suggestions=suggestions,
            confidence_score=0.85
        )

# Singleton instance
openai_service = OpenAIService() 