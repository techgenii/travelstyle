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

"""Tests for recommendations API endpoints."""

from unittest.mock import patch

import pytest
from app.services.qloo_service import QlooService
from fastapi import status


class MockAsyncResponse:
    def __init__(self, data):
        self.data = data
        self.status_code = 200

    def json(self):
        return self.data

    def raise_for_status(self):
        # Make this synchronous to avoid coroutine warnings
        if self.status_code >= 400:
            raise Exception("HTTP error")
        return self


class TestRecommendationsEndpoints:
    """Test recommendations API endpoints."""

    def test_cultural_insights_success(self, authenticated_client):
        """Test successful cultural insights retrieval."""
        with patch("app.services.qloo_service.qloo_service.get_cultural_insights") as mock_insights:
            mock_insights.return_value = {
                "destination": "Paris",
                "cultural_insights": {
                    "dress_codes": ["Smart casual", "Business attire"],
                    "color_preferences": ["Neutral tones", "Classic colors"],
                    "style_norms": ["Conservative", "Professional"],
                    "taboos": ["Avoid overly casual wear"],
                },
                "local_context": {
                    "formality_level": "moderate",
                    "seasonal_considerations": ["Summer fashion"],
                    "cultural_significance": ["Respect local customs"],
                },
                "data_source": "qloo",
            }
            response = authenticated_client.get("/api/v1/recs/cultural/Paris")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "destination" in data
            assert "cultural_insights" in data
            assert "dress_codes" in data["cultural_insights"]

    def test_cultural_insights_not_found(self, authenticated_client):
        """Test cultural insights when not available."""
        with patch("app.services.qloo_service.qloo_service.get_cultural_insights") as mock_insights:
            mock_insights.return_value = None
            response = authenticated_client.get("/api/v1/recs/cultural/InvalidCity")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Cultural insights not available" in response.json()["detail"]

    def test_cultural_insights_service_exception(self, authenticated_client):
        """Test cultural insights when service raises exception (500)."""
        with patch("app.services.qloo_service.qloo_service.get_cultural_insights") as mock_insights:
            mock_insights.side_effect = Exception("Service error")
            response = authenticated_client.get("/api/v1/recs/cultural/Paris")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve cultural insights" in response.json()["detail"]

    def test_weather_forecast_success(self, authenticated_client):
        """Test successful weather forecast retrieval."""
        with patch("app.services.weather_service.weather_service.get_weather_data") as mock_weather:
            mock_weather.return_value = {
                "destination": "Paris",
                "current_weather": {
                    "temperature": 20,
                    "condition": "Sunny",
                    "humidity": 65,
                },
                "forecast": [
                    {"date": "2024-06-01", "high": 22, "low": 15, "condition": "Partly cloudy"}
                ],
            }
            response = authenticated_client.post(
                "/api/v1/recs/weather",
                json={"destination": "Paris", "dates": ["2024-06-01"]},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "destination" in data
            assert "current_weather" in data
            assert "forecast" in data

    def test_weather_forecast_not_found(self, authenticated_client):
        """Test weather forecast when not available."""
        with patch("app.services.weather_service.weather_service.get_weather_data") as mock_weather:
            mock_weather.return_value = None
            response = authenticated_client.post(
                "/api/v1/recs/weather",
                json={"destination": "InvalidCity", "dates": ["2024-06-01"]},
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Weather data not available" in response.json()["detail"]

    def test_weather_forecast_service_exception(self, authenticated_client):
        """Test weather forecast when service raises exception (500)."""
        with patch("app.services.weather_service.weather_service.get_weather_data") as mock_weather:
            mock_weather.side_effect = Exception("Service error")
            response = authenticated_client.post(
                "/api/v1/recs/weather",
                json={"destination": "Paris", "dates": ["2024-06-01"]},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to retrieve weather forecast" in response.json()["detail"]

    def test_recommendations_no_auth(self, client):
        """Test recommendations endpoints without authentication."""
        # Test cultural insights
        response = client.get("/api/v1/recs/cultural/Paris")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Test weather forecast
        response = client.post(
            "/api/v1/recs/weather",
            json={"destination": "Paris"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_cultural_insights_success():
    """Test successful cultural insights retrieval from service."""
    service = QlooService()
    with patch("app.services.supabase_cache.supabase_cache.get_cultural_cache") as mock_cache:
        mock_cache.return_value = None
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MockAsyncResponse(
                {
                    "etiquette": {
                        "dress_codes": ["Smart casual"],
                        "fashion_taboos": ["Avoid overly casual wear"],
                    },
                    "fashion": {
                        "color_trends": ["Neutral tones"],
                        "local_styles": ["Conservative"],
                    },
                    "context": {
                        "formality": "moderate",
                        "seasonal": ["Summer fashion"],
                        "cultural_notes": ["Respect local customs"],
                    },
                }
            )
            mock_get.return_value = mock_response
            result = await service.get_cultural_insights("Paris", "leisure")
            assert result is not None
            assert "destination" in result
            assert "cultural_insights" in result
            assert "local_context" in result


@pytest.mark.asyncio
async def test_get_cultural_insights_cache():
    """Test cultural insights retrieval from cache."""
    service = QlooService()
    cached_data = {
        "destination": "Paris",
        "cultural_insights": {"dress_codes": ["Smart casual"]},
        "local_context": {"formality_level": "moderate"},
        "data_source": "qloo",
    }
    with patch("app.services.supabase_cache.supabase_cache.get_cultural_cache") as mock_cache:
        mock_cache.return_value = cached_data
        result = await service.get_cultural_insights("Paris", "leisure")
        assert result == cached_data


@pytest.mark.asyncio
async def test_get_cultural_insights_error():
    """Test cultural insights retrieval error handling."""
    service = QlooService()
    with patch("app.services.supabase_cache.supabase_cache.get_cultural_cache") as mock_cache:
        mock_cache.return_value = None
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = Exception("API error")
            result = await service.get_cultural_insights("Paris", "leisure")
            assert result is not None
            assert "data_source" in result
            assert result["data_source"] == "fallback"


@pytest.mark.asyncio
async def test_get_style_recommendations_success():
    """Test successful style recommendations retrieval."""
    service = QlooService()
    user_profile = {
        "style_preferences": ["casual", "comfortable"],
        "favorite_colors": ["blue", "black"],
        "budget_range": "mid-range",
    }
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MockAsyncResponse(
            {
                "recommendations": {
                    "styles": ["Modern", "Comfortable"],
                    "items": ["Jacket", "Pants"],
                    "colors": ["Blue", "Black"],
                    "accessories": ["Hat", "Shoes"],
                },
                "confidence": 0.9,
            }
        )
        mock_get.return_value = mock_response
        result = await service.get_style_recommendations("Paris", user_profile, "leisure")
        assert result is not None
        assert "style_recommendations" in result
        assert "confidence_score" in result


@pytest.mark.asyncio
async def test_get_style_recommendations_error():
    """Test style recommendations retrieval error handling."""
    service = QlooService()
    user_profile = {"style_preferences": ["casual"]}
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("API error")
        result = await service.get_style_recommendations("Paris", user_profile, "leisure")
        assert result is not None
        assert "style_recommendations" in result
        assert "data_source" in result
        assert result["data_source"] == "fallback"


def test_process_cultural_data():
    """Test cultural data processing."""
    service = QlooService()
    qloo_response = {
        "etiquette": {
            "dress_codes": ["Smart casual"],
            "fashion_taboos": ["Avoid overly casual wear"],
        },
        "fashion": {
            "color_trends": ["Neutral tones"],
            "local_styles": ["Conservative"],
        },
        "context": {
            "formality": "moderate",
            "seasonal": ["Summer fashion"],
            "cultural_notes": ["Respect local customs"],
        },
    }
    result = service._process_cultural_data(qloo_response, "Paris")
    assert result["destination"] == "Paris"
    assert "cultural_insights" in result
    assert "local_context" in result
    assert result["data_source"] == "qloo"


def test_process_style_data():
    """Test style data processing."""
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
    assert "style_recommendations" in result
    assert "confidence_score" in result
    assert result["data_source"] == "qloo"


def test_get_fallback_cultural_data():
    """Test fallback cultural data generation."""
    service = QlooService()
    fallback = service._get_fallback_cultural_data("Paris")
    assert fallback["destination"] == "Paris"
    assert "cultural_insights" in fallback
    assert "local_context" in fallback
    assert fallback["data_source"] == "fallback"


def test_get_fallback_style_data():
    """Test fallback style data generation."""
    service = QlooService()
    fallback = service._get_fallback_style_data("Paris")
    assert "style_recommendations" in fallback
    assert "confidence_score" in fallback
    assert fallback["data_source"] == "fallback"
