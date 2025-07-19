"""
Tests for recommendations API endpoints.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.responses import ChatResponse, ConversationContext
from app.services.currency_service import CurrencyService, currency_service
from app.services.openai_service import openai_service
from app.services.orchestrator import TravelOrchestratorService, orchestrator_service
from app.services.qloo_service import QlooService, qloo_service
from app.services.weather_service import weather_service
from fastapi import status
from httpx import RequestError


class MockAsyncResponse:
    def __init__(self, data):
        self._data = data
        self.raise_for_status = MagicMock(return_value=None)  # Make this a mock

    def json(self):
        return self._data

    async def raise_for_status(self):
        return None


class TestRecommendationsEndpoints:
    """Test cases for recommendations endpoints."""

    def test_cultural_insights_success(self, authenticated_client):
        """Test successful cultural insights retrieval."""
        with patch(
            "app.services.qloo_service.qloo_service.get_cultural_insights"
        ) as mock_get_insights:
            mock_get_insights.return_value = {
                "dress_codes": ["Smart casual", "Business attire"],
                "color_preferences": ["Neutral tones", "Classic colors"],
                "style_norms": ["Conservative", "Professional"],
                "formality_level": "moderate",
            }
            response = authenticated_client.get(
                "/api/v1/recommendations/cultural/Paris?context=business"
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "dress_codes" in data
            assert "color_preferences" in data
            assert "formality_level" in data

    def test_cultural_insights_not_found(self, authenticated_client):
        """Test cultural insights when destination not found."""
        with patch(
            "app.services.qloo_service.qloo_service.get_cultural_insights"
        ) as mock_get_insights:
            mock_get_insights.return_value = None
            response = authenticated_client.get("/api/v1/recommendations/cultural/UnknownCity")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Cultural insights not available" in response.json()["detail"]

    def test_cultural_insights_service_exception(self, authenticated_client):
        """Test cultural insights when service raises exception (500)."""
        with patch(
            "app.services.qloo_service.qloo_service.get_cultural_insights"
        ) as mock_get_insights:
            mock_get_insights.side_effect = Exception("Service error")
            response = authenticated_client.get("/api/v1/recommendations/cultural/Paris")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve cultural insights" in response.json()["detail"]

    def test_weather_forecast_success(self, authenticated_client):
        """Test successful weather forecast retrieval."""
        with patch(
            "app.services.weather_service.weather_service.get_weather_data"
        ) as mock_get_weather:
            mock_get_weather.return_value = {
                "temperature": 22.5,
                "feels_like": 24.0,
                "humidity": 65,
                "description": "Partly cloudy",
                "wind_speed": 12.0,
                "pressure": 1013,
                "clothing_recommendations": ["Light jacket", "Comfortable shoes"],
            }
            response = authenticated_client.post(
                "/api/v1/recommendations/weather",
                json={"destination": "Paris", "dates": ["2024-06-01", "2024-06-02"]},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "temperature" in data
            assert "description" in data
            assert "clothing_recommendations" in data

    def test_weather_forecast_not_found(self, authenticated_client):
        """Test weather forecast when destination not found."""
        with patch(
            "app.services.weather_service.weather_service.get_weather_data"
        ) as mock_get_weather:
            mock_get_weather.return_value = None
            response = authenticated_client.post(
                "/api/v1/recommendations/weather",
                json={"destination": "UnknownCity"},
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Weather data not available" in response.json()["detail"]

    def test_weather_forecast_service_exception(self, authenticated_client):
        """Test weather forecast when service raises exception (500)."""
        with patch(
            "app.services.weather_service.weather_service.get_weather_data"
        ) as mock_get_weather:
            mock_get_weather.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/recommendations/weather",
                json={"destination": "Paris"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve weather forecast" in response.json()["detail"]

    def test_exchange_rates_success(self, authenticated_client):
        """Test successful exchange rates retrieval."""
        with patch(
            "app.services.currency_service.currency_service.get_exchange_rates"
        ) as mock_get_rates:
            mock_get_rates.return_value = {
                "base_currency": "USD",
                "rates": {"EUR": 0.85, "GBP": 0.73, "JPY": 110.50},
                "last_updated": "2024-01-01T12:00:00Z",
            }
            response = authenticated_client.get("/api/v1/recommendations/currency/USD")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "base_currency" in data
            assert "rates" in data
            assert "EUR" in data["rates"]

    def test_exchange_rates_not_found(self, authenticated_client):
        """Test exchange rates when not available."""
        with patch(
            "app.services.currency_service.currency_service.get_exchange_rates"
        ) as mock_get_rates:
            mock_get_rates.return_value = None
            response = authenticated_client.get("/api/v1/recommendations/currency/INVALID")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Exchange rates not available" in response.json()["detail"]

    def test_exchange_rates_service_exception(self, authenticated_client):
        """Test exchange rates when service raises exception (500)."""
        with patch(
            "app.services.currency_service.currency_service.get_exchange_rates"
        ) as mock_get_rates:
            mock_get_rates.side_effect = Exception("Service error")
            response = authenticated_client.get("/api/v1/recommendations/currency/USD")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve exchange rates" in response.json()["detail"]

    def test_currency_conversion_success(self, authenticated_client):
        """Test successful currency conversion."""
        with patch(
            "app.services.currency_service.currency_service.convert_currency"
        ) as mock_convert:
            mock_convert.return_value = {
                "original_amount": 100.0,
                "converted_amount": 85.0,
                "from_currency": "USD",
                "to_currency": "EUR",
                "rate": 0.85,
                "last_updated": "2024-01-01T12:00:00Z",
            }
            response = authenticated_client.post(
                "/api/v1/recommendations/currency/convert",
                json={"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "original_amount" in data
            assert "converted_amount" in data
            assert data["from_currency"] == "USD"
            assert data["to_currency"] == "EUR"

    def test_currency_conversion_failure(self, authenticated_client):
        """Test currency conversion when it fails."""
        with patch(
            "app.services.currency_service.currency_service.convert_currency"
        ) as mock_convert:
            mock_convert.return_value = None
            response = authenticated_client.post(
                "/api/v1/recommendations/currency/convert",
                json={"amount": 100.0, "from_currency": "INVALID", "to_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Currency conversion failed" in response.json()["detail"]

    def test_currency_conversion_service_exception(self, authenticated_client):
        """Test currency conversion when service raises exception (500)."""
        with patch(
            "app.services.currency_service.currency_service.convert_currency"
        ) as mock_convert:
            mock_convert.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/recommendations/currency/convert",
                json={"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to convert currency" in response.json()["detail"]

    def test_recommendations_no_auth(self, client):
        """Test recommendations endpoints without authentication."""
        # Test cultural insights
        response = client.get("/api/v1/recommendations/cultural/Paris")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Test weather forecast
        response = client.post(
            "/api/v1/recommendations/weather",
            json={"destination": "Paris"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Test exchange rates
        response = client.get("/api/v1/recommendations/currency/USD")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Test currency conversion
        response = client.post("/api/v1/recommendations/currency/convert")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_exchange_rates_success():
    service = CurrencyService()
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(
                return_value=MockAsyncResponse(
                    {
                        "base_code": "USD",
                        "conversion_rates": {"EUR": 0.85, "GBP": 0.73},
                        "time_last_update_unix": 1234567890,
                        "time_last_update_utc": "2024-01-01T12:00:00Z",
                    }
                )
            ),
        ),
        patch("app.services.supabase_cache.supabase_cache.set_currency_cache", new=AsyncMock()),
    ):
        rates = await service.get_exchange_rates("USD")
        assert rates is not None
        assert rates["base_code"] == "USD"
        assert "EUR" in rates["conversion_rates"]


@pytest.mark.asyncio
async def test_get_exchange_rates_cache():
    service = CurrencyService()
    with patch(
        "app.services.supabase_cache.supabase_cache.get_currency_cache",
        new=AsyncMock(return_value={"cached": True}),
    ):
        rates = await service.get_exchange_rates("USD")
        assert rates is not None
        assert rates["cached"] is True


@pytest.mark.asyncio
async def test_get_exchange_rates_error():
    service = CurrencyService()
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_currency_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.get", new=AsyncMock(side_effect=RequestError("fail", request=None))
        ),
    ):
        result = await service.get_exchange_rates("USD")
        assert result is None


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_success():
    service = CurrencyService()
    with patch(
        "httpx.AsyncClient.get",
        new=AsyncMock(
            return_value=MockAsyncResponse(
                {
                    "result": "success",
                    "base_code": "USD",
                    "target_code": "EUR",
                    "conversion_rate": 0.85,
                    "time_last_update_unix": 1234567890,
                    "time_last_update_utc": "2024-01-01T12:00:00Z",
                }
            )
        ),
    ):
        result = await service.get_pair_exchange_rate("USD", "EUR")
        assert result is not None
        assert result["base_code"] == "USD"
        assert result["target_code"] == "EUR"
        assert result["rate"] == 0.85


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_error():
    service = CurrencyService()
    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=Exception("fail"))):
        result = await service.get_pair_exchange_rate("USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_endpoint_success(authenticated_client):
    """Test successful pair exchange rate retrieval (endpoint)."""
    with patch(
        "app.services.currency_service.currency_service.get_pair_exchange_rate"
    ) as mock_get_pair:
        mock_get_pair.return_value = {
            "base_currency": "USD",
            "target_currency": "EUR",
            "rate": 0.85,
            "last_updated": "2024-01-01T12:00:00Z",
        }
        response = authenticated_client.post(
            "/api/v1/recommendations/currency/pair",
            json={"base_currency": "USD", "target_currency": "EUR"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["base_currency"] == "USD"
        assert data["target_currency"] == "EUR"
        assert data["rate"] == 0.85


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_endpoint_not_found(authenticated_client):
    """Test pair exchange rate not found (404, endpoint)."""
    with patch(
        "app.services.currency_service.currency_service.get_pair_exchange_rate"
    ) as mock_get_pair:
        mock_get_pair.return_value = None
        response = authenticated_client.post(
            "/api/v1/recommendations/currency/pair",
            json={"base_currency": "USD", "target_currency": "INVALID"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Exchange rate not available" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_pair_exchange_rate_endpoint_service_exception(authenticated_client):
    """Test pair exchange rate when service raises exception (500, endpoint)."""
    from unittest.mock import AsyncMock

    with patch(
        "app.services.currency_service.currency_service.get_pair_exchange_rate",
        new_callable=AsyncMock,
    ) as mock_get_pair:
        mock_get_pair.side_effect = Exception("Service error")
        response = authenticated_client.post(
            "/api/v1/recommendations/currency/pair",
            json={"base_currency": "USD", "target_currency": "EUR"},
        )
        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to retrieve pair exchange rate"


@pytest.mark.asyncio
async def test_convert_currency_success():
    service = CurrencyService()
    with patch.object(
        service,
        "get_pair_exchange_rate",
        new=AsyncMock(
            return_value={
                "base_code": "USD",
                "target_code": "EUR",
                "rate": 0.85,
                "last_updated_unix": 1234567890,
                "last_updated_utc": "2024-01-01T12:00:00Z",
            }
        ),
    ):
        result = await service.convert_currency(100, "USD", "EUR")
        assert result is not None
        assert result["original"]["amount"] == 100
        assert result["converted"]["amount"] == 85.0
        assert result["rate"] == 0.85


@pytest.mark.asyncio
async def test_convert_currency_error():
    service = CurrencyService()
    with patch.object(service, "get_pair_exchange_rate", new=AsyncMock(return_value=None)):
        result = await service.convert_currency(100, "USD", "EUR")
        assert result is None


@pytest.mark.asyncio
async def test_generate_travel_recommendations_success():
    orchestrator = TravelOrchestratorService()
    with (
        patch(
            "app.services.qloo_service.qloo_service.get_cultural_insights",
            new=AsyncMock(return_value={"culture": "ok"}),
        ),
        patch(
            "app.services.weather_service.weather_service.get_weather_data",
            new=AsyncMock(return_value={"weather": "ok"}),
        ),
        patch(
            "app.services.qloo_service.qloo_service.get_style_recommendations",
            new=AsyncMock(return_value={"style": "ok"}),
        ),
        patch(
            "app.services.currency_service.currency_service.get_exchange_rates",
            new=AsyncMock(return_value={"currency": "ok"}),
        ),
        patch(
            "app.services.openai_service.openai_service.generate_response",
            new=AsyncMock(
                return_value=ChatResponse(
                    message="AI response", quick_replies=[], suggestions=[], confidence_score=1.0
                )
            ),
        ),
    ):
        context = ConversationContext(
            user_id="test-user",
            destination="Paris",
            travel_dates=["2024-06-01"],
            trip_purpose="leisure",
        )
        result = await orchestrator.generate_travel_recommendations(
            user_message="I'm going to Paris!",
            context=context,
            conversation_history=[],
            user_profile={"home_currency": "USD"},
        )
        assert isinstance(result, ChatResponse)
        assert "AI response" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_error():
    orchestrator = TravelOrchestratorService()
    with (
        patch(
            "app.services.qloo_service.qloo_service.get_cultural_insights",
            new=AsyncMock(side_effect=Exception("fail")),
        ),
        patch(
            "app.services.weather_service.weather_service.get_weather_data",
            new=AsyncMock(return_value={}),
        ),
        patch(
            "app.services.qloo_service.qloo_service.get_style_recommendations",
            new=AsyncMock(return_value={}),
        ),
        patch(
            "app.services.currency_service.currency_service.get_exchange_rates",
            new=AsyncMock(return_value={}),
        ),
        patch(
            "app.services.openai_service.openai_service.generate_response",
            new=AsyncMock(side_effect=Exception("fail")),
        ),
    ):
        context = ConversationContext(
            user_id="test-user", destination="", travel_dates=[], trip_purpose="leisure"
        )
        result = await orchestrator.generate_travel_recommendations(
            user_message="No destination",
            context=context,
            conversation_history=[],
            user_profile=None,
        )
        assert isinstance(result, ChatResponse)
        assert "trouble processing your request" in result.message
        assert result.confidence_score == 0.0


def test_parse_trip_context():
    orchestrator = TravelOrchestratorService()
    context = ConversationContext(
        user_id="test-user", destination=None, travel_dates=None, trip_purpose=None
    )
    trip = orchestrator._parse_trip_context("I'm going to Paris for business", context)
    assert trip["destination"] == "Paris"
    assert trip["context"] == "business"
    assert trip["occasion"] == "business"
    trip2 = orchestrator._parse_trip_context("Let's go hiking in Denver", context)
    assert trip2["context"] == "active"
    assert trip2["occasion"] == "active"


def test_enhance_response():
    orchestrator = TravelOrchestratorService()
    ai_response = ChatResponse(
        message="msg", quick_replies=[], suggestions=[], confidence_score=1.0
    )
    context = {
        "weather_conditions": {"weather": "ok"},
        "cultural_intelligence": {"culture": "ok"},
        "currency_info": {"currency": "ok"},
        "trip_context": {"destination": "Paris"},
        "user_profile": {"home_currency": "USD"},
    }
    result = orchestrator._enhance_response(ai_response, context)
    assert any(qr.text == "More weather details" for qr in result.quick_replies)
    assert any(qr.text == "Cultural tips" for qr in result.quick_replies)
    assert any(qr.text == "Currency help" for qr in result.quick_replies)
    assert "Get packing checklist" in result.suggestions
    assert "Local shopping tips" in result.suggestions
    assert "Emergency contact info" in result.suggestions


@pytest.mark.asyncio
async def test_get_cultural_insights_success():
    service = QlooService()
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_cultural_cache",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "httpx.AsyncClient.post",
            new=AsyncMock(
                return_value=MockAsyncResponse(
                    {
                        "etiquette": {"dress_codes": ["Smart"]},
                        "fashion": {"color_trends": ["Blue"], "local_styles": ["Modern"]},
                        "context": {
                            "formality": "casual",
                            "seasonal": ["summer"],
                            "cultural_notes": ["note"],
                        },
                    }
                )
            ),
        ),
        patch("app.services.supabase_cache.supabase_cache.set_cultural_cache", new=AsyncMock()),
    ):
        mock_post = AsyncMock()
        mock_post.json.return_value = {
            "etiquette": {"dress_codes": ["Smart"]},
            "fashion": {"color_trends": ["Blue"], "local_styles": ["Modern"]},
            "context": {"formality": "casual", "seasonal": ["summer"], "cultural_notes": ["note"]},
        }
        mock_post.raise_for_status.return_value = None
        result = await service.get_cultural_insights("Paris")
        assert result is not None
        assert "cultural_insights" in result
        assert result["destination"] == "Paris"


@pytest.mark.asyncio
async def test_get_cultural_insights_cache():
    service = QlooService()
    with patch(
        "app.services.supabase_cache.supabase_cache.get_cultural_cache",
        new=AsyncMock(return_value={"cached": True}),
    ):
        result = await service.get_cultural_insights("Paris")
        assert result is not None
        assert result["cached"] is True


@pytest.mark.asyncio
async def test_get_cultural_insights_error():
    service = QlooService()
    with (
        patch(
            "app.services.supabase_cache.supabase_cache.get_cultural_cache",
            new=AsyncMock(return_value=None),
        ),
        patch("httpx.AsyncClient.post", new=AsyncMock(side_effect=Exception("fail"))),
    ):
        result = await service.get_cultural_insights("Paris")
        assert result is not None
        assert "cultural_insights" in result
        assert result["data_source"] == "fallback"


@pytest.mark.asyncio
async def test_get_style_recommendations_success():
    service = QlooService()
    with patch(
        "httpx.AsyncClient.post",
        new=AsyncMock(
            return_value=MockAsyncResponse(
                {
                    "recommendations": {
                        "styles": ["Modern"],
                        "items": ["Jacket"],
                        "colors": ["Blue"],
                        "accessories": ["Hat"],
                    },
                    "confidence": 0.9,
                }
            )
        ),
    ):
        result = await service.get_style_recommendations("Paris", {"style": {}}, "leisure")
        assert result is not None
        assert "style_recommendations" in result
        assert result["confidence_score"] == 0.9


@pytest.mark.asyncio
async def test_get_style_recommendations_error():
    service = QlooService()
    with patch("httpx.AsyncClient.post", new=AsyncMock(side_effect=Exception("fail"))):
        result = await service.get_style_recommendations("Paris", {"style": {}}, "leisure")
        assert result is not None
        assert "style_recommendations" in result
        assert result["data_source"] == "fallback"


def test_process_cultural_data():
    service = QlooService()
    qloo_response = {
        "etiquette": {"dress_codes": ["Smart"]},
        "fashion": {"color_trends": ["Blue"], "local_styles": ["Modern"]},
        "context": {"formality": "casual", "seasonal": ["summer"], "cultural_notes": ["note"]},
    }
    result = service._process_cultural_data(qloo_response, "Paris")
    assert result["cultural_insights"]["dress_codes"] == ["Smart"]
    assert result["local_context"]["formality_level"] == "casual"
    assert result["destination"] == "Paris"


def test_process_style_data():
    service = QlooService()
    qloo_response = {
        "recommendations": {
            "styles": ["Modern"],
            "items": ["Jacket"],
            "colors": ["Blue"],
            "accessories": ["Hat"],
        },
        "confidence": 0.9,
    }
    result = service._process_style_data(qloo_response)
    assert result["style_recommendations"]["recommended_styles"] == ["Modern"]
    assert result["confidence_score"] == 0.9


def test_get_fallback_cultural_data():
    service = QlooService()
    result = service._get_fallback_cultural_data("Paris")
    assert result["destination"] == "Paris"
    assert result["data_source"] == "fallback"


def test_get_fallback_style_data():
    service = QlooService()
    result = service._get_fallback_style_data("Paris")
    assert result["data_source"] == "fallback"
    assert "style_recommendations" in result


@pytest.mark.asyncio
async def test_generate_travel_recommendations_orchestration_error():
    """Test generate_travel_recommendations when orchestration raises an exception."""
    orchestrator_service = TravelOrchestratorService()
    with patch.object(
        orchestrator_service, "_parse_trip_context", side_effect=Exception("Parse error")
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I want to go to Paris",
            ConversationContext(
                user_id="user-1",
                destination="Paris",
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            {"id": "user-1"},
        )
        assert result.confidence_score == 0.0
        assert "I apologize, but I'm having trouble processing" in result.message


@pytest.mark.asyncio
async def test_safe_api_call_exception():
    """Test _safe_api_call when API function raises an exception."""
    orchestrator_service = TravelOrchestratorService()

    async def failing_api():
        raise Exception("API error")

    result = await orchestrator_service._safe_api_call(failing_api)
    assert result is None


@pytest.mark.asyncio
async def test_parse_trip_context_destination_extraction():
    """Test _parse_trip_context with destination extraction from message."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1", destination=None, travel_dates=["2024-06-01"], trip_purpose="leisure"
    )
    result = orchestrator_service._parse_trip_context("I want to go to Tokyo", context)
    assert result["destination"] == "Tokyo"


@pytest.mark.asyncio
async def test_parse_trip_context_destination_extraction_visiting():
    """Test _parse_trip_context with 'visiting' keyword."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1", destination=None, travel_dates=["2024-06-01"], trip_purpose="leisure"
    )
    result = orchestrator_service._parse_trip_context("I'm visiting London next week", context)
    assert result["destination"] == "London"


@pytest.mark.asyncio
async def test_parse_trip_context_destination_extraction_in():
    """Test _parse_trip_context with 'in' keyword."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1", destination=None, travel_dates=["2024-06-01"], trip_purpose="leisure"
    )
    result = orchestrator_service._parse_trip_context("I'll be in New York", context)
    assert result["destination"] == "New York"


@pytest.mark.asyncio
async def test_parse_trip_context_business_context():
    """Test _parse_trip_context with business keywords."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1", destination="Berlin", travel_dates=["2024-06-01"], trip_purpose="leisure"
    )
    result = orchestrator_service._parse_trip_context(
        "I have a business meeting in Berlin", context
    )
    assert result["context"] == "business"
    assert result["occasion"] == "business"


@pytest.mark.asyncio
async def test_parse_trip_context_formal_context():
    """Test _parse_trip_context with formal keywords."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1", destination="Rome", travel_dates=["2024-06-01"], trip_purpose="leisure"
    )
    result = orchestrator_service._parse_trip_context(
        "I'm attending a formal dinner in Rome", context
    )
    assert result["context"] == "formal"
    assert result["occasion"] == "formal"


@pytest.mark.asyncio
async def test_parse_trip_context_active_context():
    """Test _parse_trip_context with active/adventure keywords."""
    orchestrator_service = TravelOrchestratorService()
    context = ConversationContext(
        user_id="user-1",
        destination="Switzerland",
        travel_dates=["2024-06-01"],
        trip_purpose="leisure",
    )
    result = orchestrator_service._parse_trip_context("I'm going hiking in Switzerland", context)
    assert result["context"] == "active"
    assert result["occasion"] == "active"


@pytest.mark.asyncio
async def test_enhance_response_with_all_context():
    """Test _enhance_response with all context data available."""
    orchestrator_service = TravelOrchestratorService()
    ai_response = ChatResponse(
        message="Here are your travel recommendations",
        confidence_score=0.9,
        quick_replies=[],
        suggestions=[],
    )

    context = {
        "weather_conditions": {"temperature": 25},
        "cultural_intelligence": {"customs": "data"},
        "currency_info": {"rates": "data"},
        "trip_context": {"destination": "Paris"},
    }

    result = orchestrator_service._enhance_response(ai_response, context)

    # Check that quick replies were added
    quick_reply_texts = [qr.text for qr in result.quick_replies]
    assert "More weather details" in quick_reply_texts
    assert "Cultural tips" in quick_reply_texts
    assert "Currency help" in quick_reply_texts

    # Check that suggestions were added
    assert "Get packing checklist" in result.suggestions
    assert "Local shopping tips" in result.suggestions
    assert "Emergency contact info" in result.suggestions


@pytest.mark.asyncio
async def test_enhance_response_with_partial_context():
    """Test _enhance_response with only some context data available."""
    orchestrator_service = TravelOrchestratorService()
    ai_response = ChatResponse(
        message="Here are your travel recommendations",
        confidence_score=0.9,
        quick_replies=[],
        suggestions=[],
    )

    context = {
        "weather_conditions": {"temperature": 25},
        "cultural_intelligence": None,
        "currency_info": None,
        "trip_context": {"destination": "Paris"},
    }

    result = orchestrator_service._enhance_response(ai_response, context)

    # Check that only weather quick reply was added
    quick_reply_texts = [qr.text for qr in result.quick_replies]
    assert "More weather details" in quick_reply_texts
    assert "Cultural tips" not in quick_reply_texts
    assert "Currency help" not in quick_reply_texts

    # Check that suggestions were still added
    assert "Get packing checklist" in result.suggestions


@pytest.mark.asyncio
async def test_enhance_response_with_no_destination():
    """Test _enhance_response when no destination is specified."""
    orchestrator_service = TravelOrchestratorService()
    ai_response = ChatResponse(
        message="Here are your travel recommendations",
        confidence_score=0.9,
        quick_replies=[],
        suggestions=[],
    )

    context = {
        "weather_conditions": {"temperature": 25},
        "cultural_intelligence": {"customs": "data"},
        "currency_info": {"rates": "data"},
        "trip_context": {"destination": None},
    }

    result = orchestrator_service._enhance_response(ai_response, context)

    # Check that quick replies were added
    quick_reply_texts = [qr.text for qr in result.quick_replies]
    assert "More weather details" in quick_reply_texts
    assert "Cultural tips" in quick_reply_texts
    assert "Currency help" in quick_reply_texts

    # Check that no suggestions were added (no destination)
    assert len(result.suggestions) == 0


@pytest.mark.asyncio
async def test_generate_travel_recommendations_no_destination():
    """Test generate_travel_recommendations when no destination is specified."""
    with (
        patch.object(qloo_service, "get_cultural_insights", new=AsyncMock(return_value=None)),
        patch.object(weather_service, "get_weather_data", new=AsyncMock(return_value=None)),
        patch.object(qloo_service, "get_style_recommendations", new=AsyncMock(return_value=None)),
        patch.object(
            currency_service, "get_exchange_rates", new=AsyncMock(return_value={"USD": 1.0})
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(
                return_value=ChatResponse(
                    message="Here are your recommendations", confidence_score=0.8
                )
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I need travel advice",
            ConversationContext(
                user_id="user-1",
                destination=None,
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            {"id": "user-1", "home_currency": "USD"},
        )
        assert result.confidence_score == 0.8
        assert "Here are your recommendations" in result.message


@pytest.mark.asyncio
async def test_generate_travel_recommendations_no_user_profile():
    """Test generate_travel_recommendations when no user profile is provided."""
    with (
        patch.object(
            qloo_service, "get_cultural_insights", new=AsyncMock(return_value={"insights": "data"})
        ),
        patch.object(
            weather_service, "get_weather_data", new=AsyncMock(return_value={"weather": "data"})
        ),
        patch.object(
            currency_service, "get_exchange_rates", new=AsyncMock(return_value={"USD": 1.0})
        ),
        patch.object(
            openai_service,
            "generate_response",
            new=AsyncMock(
                return_value=ChatResponse(
                    message="Here are your recommendations", confidence_score=0.8
                )
            ),
        ),
    ):
        result = await orchestrator_service.generate_travel_recommendations(
            "I want to go to Paris",
            ConversationContext(
                user_id="user-1",
                destination="Paris",
                travel_dates=["2024-06-01"],
                trip_purpose="leisure",
            ),
            [],
            None,  # No user profile
        )
        assert result.confidence_score == 0.8
        assert "Here are your recommendations" in result.message
