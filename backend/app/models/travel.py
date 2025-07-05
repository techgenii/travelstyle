"""
Travel-related models for TravelStyle AI application.
Defines Pydantic models for travel context, style preferences, and recommendations.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

class PackingMethod(str, Enum):
    """Supported packing methods from the PRD"""
    FIVE_FOUR_THREE_TWO_ONE = "5-4-3-2-1"  # 5 tops, 4 bottoms, 3 shoes, 2 jackets, 1 dress
    THREE_BY_THREE = "3x3x3"  # 3 tops, 3 bottoms, 3 layers
    RULE_OF_THREES = "rule_of_3s"  # 3 of each essential category
    TEN_BY_TEN = "10x10"  # 10 pieces, 10 days
    TWELVE_PIECE = "12-piece"  # 12-piece travel capsule
    FOUR_BY_FOUR = "4x4"  # 4x4 wardrobe grid
    ONE_TWO_THREE_FOUR_FIVE_SIX = "1-2-3-4-5-6"  # Smart packing list

class TravelContext(str, Enum):
    """Travel context/occasion types"""
    LEISURE = "leisure"
    BUSINESS = "business"
    FORMAL = "formal"
    ACTIVE = "active"
    BEACH = "beach"
    URBAN = "urban"
    MOUNTAIN = "mountain"

class StyleCategory(str, Enum):
    """Supported style categories from the PRD"""
    CALIFORNIA_CASUAL = "california_casual"
    BUSINESS_PROFESSIONAL = "business_professional"
    SMART_CASUAL = "smart_casual"
    RESORT_WEAR = "resort_wear"
    URBAN_CHIC = "urban_chic"
    CONSERVATIVE_FORMAL = "conservative_formal"
    BEACH_COASTAL = "beach_coastal"
    MOUNTAIN_OUTDOOR = "mountain_outdoor"

class TripContext(BaseModel):
    """Trip context and details"""
    destination: str
    travel_dates: Optional[List[str]] = None
    duration_days: Optional[int] = None
    context: TravelContext = TravelContext.LEISURE
    packing_method: Optional[PackingMethod] = None
    budget_range: Optional[str] = None
    activities: Optional[List[str]] = None
    accommodation_type: Optional[str] = None

class StylePreferences(BaseModel):
    """User style preferences"""
    preferred_colors: Optional[List[str]] = None
    style_categories: Optional[List[StyleCategory]] = None
    formality_level: Optional[str] = None  # casual, smart_casual, business, formal
    body_type: Optional[str] = None
    size_info: Optional[Dict[str, Any]] = None
    budget_range: Optional[str] = None
    climate_preferences: Optional[Dict[str, Any]] = None

class WeatherData(BaseModel):
    """Weather information for destination"""
    temperature: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    visibility: Optional[float] = None
    pressure: int
    forecast: Optional[Dict[str, Any]] = None
    clothing_recommendations: Optional[Dict[str, Any]] = None

class CulturalInsights(BaseModel):
    """Cultural insights and etiquette"""
    dress_codes: List[str] = []
    color_preferences: List[str] = []
    style_norms: List[str] = []
    taboos: List[str] = []
    formality_level: str = "moderate"
    seasonal_considerations: List[str] = []
    cultural_significance: List[str] = []

class PackingRecommendation(BaseModel):
    """Packing recommendation structure"""
    method: PackingMethod
    framework: Dict[str, Any]
    specific_items: Optional[List[str]] = None
    cultural_notes: Optional[List[str]] = None
    weather_considerations: Optional[List[str]] = None
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)

class CurrencyInfo(BaseModel):
    """Currency conversion information"""
    base_currency: str
    target_currency: str
    rate: float
    converted_amount: Optional[float] = None
    original_amount: Optional[float] = None
    last_updated: str

class ChatSession(BaseModel):
    """Chat session information"""
    session_id: str
    user_id: str
    trip_context: Optional[TripContext] = None
    style_preferences: Optional[StylePreferences] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class ConversationMessage(BaseModel):
    """Individual conversation message"""
    message_id: str
    session_id: str
    user_id: str
    message_type: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class RecommendationHistory(BaseModel):
    """Track recommendation quality and usage"""
    recommendation_id: str
    user_id: str
    destination: str
    recommendation_type: str  # "wardrobe", "cultural", "weather", "currency"
    content: Dict[str, Any]
    user_feedback: Optional[str] = None
    created_at: datetime
    used_at: Optional[datetime] = None
