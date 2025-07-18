"""
Tests for main FastAPI app endpoints.
"""

from fastapi import status


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Welcome to TravelStyle AI API"


def test_health(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


def test_docs(client):
    """Test docs endpoint."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
    assert "Swagger UI" in response.text


def test_openapi(client):
    """Test OpenAPI schema endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["openapi"].startswith("3.")


def test_redoc(client):
    """Test ReDoc endpoint."""
    response = client.get("/redoc")
    assert response.status_code == status.HTTP_200_OK
    assert "ReDoc" in response.text
