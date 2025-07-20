"""
Tests for main FastAPI app endpoints.
"""

from unittest.mock import patch

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


def test_lifespan_startup_and_shutdown():
    """Test lifespan function startup and shutdown behavior."""
    from app.main import lifespan

    # Mock logger to capture log messages
    with patch("app.main.logger") as mock_logger:
        # Test the lifespan context manager
        async def test_lifespan():
            async with lifespan(None):
                # This simulates the application running
                pass

        # Run the lifespan test
        import asyncio

        asyncio.run(test_lifespan())

        # Verify startup and shutdown logs were called
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call("Starting TravelStyle AI application...")
        mock_logger.info.assert_any_call("Shutting down TravelStyle AI application...")


def test_main_block_exists():
    """Test that the main block exists and can be executed."""
    # Import the main module to verify it loads correctly
    from app.main import app

    # Verify the app was created successfully
    assert app is not None
    assert hasattr(app, "title")
    assert app.title == "TravelStyle AI"

    # Verify the main block code exists by checking if uvicorn is imported
    import app.main

    assert hasattr(app.main, "uvicorn")
