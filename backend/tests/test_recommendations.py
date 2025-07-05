"""
Tests for recommendations API endpoints.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status

class TestRecommendationsEndpoints:
    """Test cases for recommendations endpoints."""

    def test_cultural_insights_success(self, client, mock_auth_headers):
        """Test successful cultural insights retrieval."""
        with patch('app.api.v1.recommendations.get_current_user') as mock_get_user, \
             patch('app.api.v1.recommendations.qloo_service.get_cultural_insights') as mock_get_insights:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            mock_get_insights.return_value = {
                "dress_codes": ["Smart casual", "Business attire"],
                "color_preferences": ["Neutral tones", "Classic colors"],
                "style_norms": ["Conservative", "Professional"],
                "formality_level": "moderate"
            }
            
            response = client.get(
                "/api/v1/recommendations/cultural/Paris?context=business",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "dress_codes" in data
            assert "color_preferences" in data
            assert "formality_level" in data

    def test_cultural_insights_not_found(self, client, mock_auth_headers):
        """Test cultural insights when destination not found."""
        with patch('app.api.v1.recommendations.get_current_user') as mock_get_user, \
             patch('app.api.v1.recommendations.qloo_service.get_cultural_insights') as mock_get_insights:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            mock_get_insights.return_value = None
            
            response = client.get(
                "/api/v1/recommendations/cultural/UnknownCity",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Cultural insights not available" in response.json()["detail"]

    def test_weather_forecast_success(self, client, mock_auth_headers):
        """Test successful weather forecast retrieval."""
        with patch('app.api.v1.recommendations.get_current_user') as mock_get_user, \
             patch('app.api.v1.recommendations.weather_service.get_weather_data') as mock_get_weather:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            mock_get_weather.return_value = {
                "temperature": 22.5,
                "feels_like": 24.0,
                "humidity": 65,
                "description": "Partly cloudy",
                "wind_speed": 12.0,
                "pressure": 1013,
                "clothing_recommendations": ["Light jacket", "Comfortable shoes"]
            }
            
            response = client.get(
                "/api/v1/recommendations/weather/Paris?dates=2024-06-01&dates=2024-06-02",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "temperature" in data
            assert "description" in data
            assert "clothing_recommendations" in data

    def test_weather_forecast_not_found(self, client, mock_auth_headers):
        """Test weather forecast when destination not found."""
        with patch('app.api.v1.recommendations.get_current_user') as mock_get_user, \
             patch('app.api.v1.recommendations.weather_service.get_weather_data') as mock_get_weather:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            mock_get_weather.return_value = None
            
            response = client.get(
                "/api/v1/recommendations/weather/UnknownCity",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Weather data not available" in response.json()["detail"]

    def test_exchange_rates_success(self, client, mock_auth_headers):
        """Test successful exchange rates retrieval."""
        with patch('app.api.v1.recommendations.get_current_user') as mock_get_user, \
             patch('app.api.v1.recommendations.currency_service.get_exchange_rates') as mock_get_rates:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            mock_get_rates.return_value = {
                "base_currency": "USD",
                "rates": {
                    "EUR": 0.85,
                    "GBP": 0.73,
                    "JPY": 110.50
                },
                "last_updated": "2024-01-01T12:00:00Z"
            }
            
            response = client.get(
                "/api/v1/recommendations/currency/USD",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "base_currency" in data
            assert "rates" in data
            assert "EUR" in data["rates"]

    def test_exchange_rates_not_found(self, client, mock_auth_headers):
        """Test exchange rates when not available."""
        with patch('app.api.v1.recommendations.get_current_user') as mock_get_user, \
             patch('app.api.v1.recommendations.currency_service.get_exchange_rates') as mock_get_rates:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            mock_get_rates.return_value = None
            
            response = client.get(
                "/api/v1/recommendations/currency/INVALID",
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Exchange rates not available" in response.json()["detail"]

    def test_currency_conversion_success(self, client, mock_auth_headers):
        """Test successful currency conversion."""
        with patch('app.api.v1.recommendations.get_current_user') as mock_get_user, \
             patch('app.api.v1.recommendations.currency_service.convert_currency') as mock_convert:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            mock_convert.return_value = {
                "original_amount": 100.0,
                "converted_amount": 85.0,
                "from_currency": "USD",
                "to_currency": "EUR",
                "rate": 0.85,
                "last_updated": "2024-01-01T12:00:00Z"
            }
            
            response = client.post(
                "/api/v1/recommendations/currency/convert",
                params={
                    "amount": 100.0,
                    "from_currency": "USD",
                    "to_currency": "EUR"
                },
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "original_amount" in data
            assert "converted_amount" in data
            assert data["from_currency"] == "USD"
            assert data["to_currency"] == "EUR"

    def test_currency_conversion_failure(self, client, mock_auth_headers):
        """Test currency conversion when it fails."""
        with patch('app.api.v1.recommendations.get_current_user') as mock_get_user, \
             patch('app.api.v1.recommendations.currency_service.convert_currency') as mock_convert:
            
            mock_get_user.return_value = {
                "id": "test-user-123",
                "email": "test@example.com",
                "is_active": True
            }
            
            mock_convert.return_value = None
            
            response = client.post(
                "/api/v1/recommendations/currency/convert",
                params={
                    "amount": 100.0,
                    "from_currency": "INVALID",
                    "to_currency": "EUR"
                },
                headers=mock_auth_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Currency conversion failed" in response.json()["detail"]

    def test_recommendations_no_auth(self, client):
        """Test recommendations endpoints without authentication."""
        # Test cultural insights
        response = client.get("/api/v1/recommendations/cultural/Paris")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test weather forecast
        response = client.get("/api/v1/recommendations/weather/Paris")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test exchange rates
        response = client.get("/api/v1/recommendations/currency/USD")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test currency conversion
        response = client.post("/api/v1/recommendations/currency/convert")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 