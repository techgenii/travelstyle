"""
Travel-related models for TravelStyle AI application.
Defines Pydantic models for travel context, style preferences, and recommendations.
"""

from datetime import datetime
from enum import Enum
from typing import Any

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
    travel_dates: list[str] | None = None
    duration_days: int | None = None
    context: TravelContext = TravelContext.LEISURE
    packing_method: PackingMethod | None = None
    budget_range: str | None = None
    activities: list[str] | None = None
    accommodation_type: str | None = None


class StylePreferences(BaseModel):
    """User style preferences"""

    preferred_colors: list[str] | None = None
    style_categories: list[StyleCategory] | None = None
    formality_level: str | None = None  # casual, smart_casual, business, formal
    body_type: str | None = None
    size_info: dict[str, Any] | None = None
    budget_range: str | None = None
    climate_preferences: dict[str, Any] | None = None


class WeatherData(BaseModel):
    """Weather information for destination"""

    temperature: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    visibility: float | None = None
    pressure: int
    forecast: dict[str, Any] | None = None
    clothing_recommendations: dict[str, Any] | None = None


class CulturalInsights(BaseModel):
    """Cultural insights and etiquette"""

    dress_codes: list[str] = []
    color_preferences: list[str] = []
    style_norms: list[str] = []
    taboos: list[str] = []
    formality_level: str = "moderate"
    seasonal_considerations: list[str] = []
    cultural_significance: list[str] = []


class PackingRecommendation(BaseModel):
    """Packing recommendation structure"""

    method: PackingMethod
    framework: dict[str, Any]
    specific_items: list[str] | None = None
    cultural_notes: list[str] | None = None
    weather_considerations: list[str] | None = None
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)


class CurrencyPairRequest(BaseModel):
    base_currency: str
    target_currency: str


class CurrencyConvertRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


class CurrencyInfo(BaseModel):
    """Currency conversion information"""

    base_currency: str
    target_currency: str
    rate: float
    converted_amount: float | None = None
    original_amount: float | None = None
    last_updated: str


class ChatSession(BaseModel):
    """Chat session information"""

    session_id: str
    user_id: str
    trip_context: TripContext | None = None
    style_preferences: StylePreferences | None = None
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
    metadata: dict[str, Any] | None = None


class RecommendationHistory(BaseModel):
    """Track recommendation quality and usage"""

    recommendation_id: str
    user_id: str
    destination: str
    recommendation_type: str  # "wardrobe", "cultural", "weather", "currency"
    content: dict[str, Any]
    user_feedback: str | None = None
    created_at: datetime
    used_at: datetime | None = None
