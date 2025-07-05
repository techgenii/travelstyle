"""
Tests for recommendations API endpoints.
"""
from unittest.mock import patch
from fastapi import status

class TestRecommendationsEndpoints:
    """Test cases for recommendations endpoints."""

    def test_cultural_insights_success(self, authenticated_client):
        """Test successful cultural insights retrieval."""
        with patch(
            'app.services.qloo_service.qloo_service.get_cultural_insights'
        ) as mock_get_insights:
            mock_get_insights.return_value = {
                "dress_codes": ["Smart casual", "Business attire"],
                "color_preferences": ["Neutral tones", "Classic colors"],
                "style_norms": ["Conservative", "Professional"],
                "formality_level": "moderate"
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
            'app.services.qloo_service.qloo_service.get_cultural_insights'
        ) as mock_get_insights:
            mock_get_insights.return_value = None
            response = authenticated_client.get(
                "/api/v1/recommendations/cultural/UnknownCity"
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Cultural insights not available" in response.json()["detail"]

    def test_weather_forecast_success(self, authenticated_client):
        """Test successful weather forecast retrieval."""
        with patch(
            'app.services.weather_service.weather_service.get_weather_data'
        ) as mock_get_weather:
            mock_get_weather.return_value = {
                "temperature": 22.5,
                "feels_like": 24.0,
                "humidity": 65,
                "description": "Partly cloudy",
                "wind_speed": 12.0,
                "pressure": 1013,
                "clothing_recommendations": ["Light jacket", "Comfortable shoes"]
            }
            response = authenticated_client.get(
                "/api/v1/recommendations/weather/Paris?dates=2024-06-01&dates=2024-06-02"
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "temperature" in data
            assert "description" in data
            assert "clothing_recommendations" in data

    def test_weather_forecast_not_found(self, authenticated_client):
        """Test weather forecast when destination not found."""
        with patch(
            'app.services.weather_service.weather_service.get_weather_data'
        ) as mock_get_weather:
            mock_get_weather.return_value = None
            response = authenticated_client.get(
                "/api/v1/recommendations/weather/UnknownCity"
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Weather data not available" in response.json()["detail"]

    def test_exchange_rates_success(self, authenticated_client):
        """Test successful exchange rates retrieval."""
        with patch(
            'app.services.currency_service.currency_service.get_exchange_rates'
        ) as mock_get_rates:
            mock_get_rates.return_value = {
                "base_currency": "USD",
                "rates": {
                    "EUR": 0.85,
                    "GBP": 0.73,
                    "JPY": 110.50
                },
                "last_updated": "2024-01-01T12:00:00Z"
            }
            response = authenticated_client.get(
                "/api/v1/recommendations/currency/USD"
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "base_currency" in data
            assert "rates" in data
            assert "EUR" in data["rates"]

    def test_exchange_rates_not_found(self, authenticated_client):
        """Test exchange rates when not available."""
        with patch(
            'app.services.currency_service.currency_service.get_exchange_rates'
        ) as mock_get_rates:
            mock_get_rates.return_value = None
            response = authenticated_client.get(
                "/api/v1/recommendations/currency/INVALID"
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Exchange rates not available" in response.json()["detail"]

    def test_currency_conversion_success(self, authenticated_client):
        """Test successful currency conversion."""
        with patch(
            'app.services.currency_service.currency_service.convert_currency'
        ) as mock_convert:
            mock_convert.return_value = {
                "original_amount": 100.0,
                "converted_amount": 85.0,
                "from_currency": "USD",
                "to_currency": "EUR",
                "rate": 0.85,
                "last_updated": "2024-01-01T12:00:00Z"
            }
            response = authenticated_client.post(
                "/api/v1/recommendations/currency/convert",
                params={
                    "amount": 100.0,
                    "from_currency": "USD",
                    "to_currency": "EUR"
                }
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
            'app.services.currency_service.currency_service.convert_currency'
        ) as mock_convert:
            mock_convert.return_value = None
            response = authenticated_client.post(
                "/api/v1/recommendations/currency/convert",
                params={
                    "amount": 100.0,
                    "from_currency": "INVALID",
                    "to_currency": "EUR"
                }
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Currency conversion failed" in response.json()["detail"]

    def test_recommendations_no_auth(self, client):
        """Test recommendations endpoints without authentication."""
        # Test cultural insights
        response = client.get("/api/v1/recommendations/cultural/Paris")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Test weather forecast
        response = client.get("/api/v1/recommendations/weather/Paris")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Test exchange rates
        response = client.get("/api/v1/recommendations/currency/USD")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Test currency conversion
        response = client.post("/api/v1/recommendations/currency/convert")
        assert response.status_code == status.HTTP_403_FORBIDDEN
