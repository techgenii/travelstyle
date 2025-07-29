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

"""
Tests for main FastAPI app endpoints.
"""

from unittest.mock import MagicMock, patch

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
    from app.travelstyle import lifespan

    # Mock logger to capture log messages
    with patch("app.travelstyle.logger") as mock_logger:
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
    """Test that the main module exists and can be executed."""
    # Import the main module to verify it loads correctly
    from app.travelstyle import travelstyle_app as app

    # Verify the app was created successfully
    assert app is not None
    assert hasattr(app, "title")
    assert app.title == "TravelStyle AI"

    # Verify the Lambda handler function exists (for AWS Lambda deployment)
    import app.travelstyle

    assert hasattr(app.travelstyle, "handler")
    assert callable(app.travelstyle.handler)

    # Verify the lifespan function exists
    assert hasattr(app.travelstyle, "lifespan")
    assert callable(app.travelstyle.lifespan)

    # Verify the app has the expected routers
    assert len(app.travelstyle.travelstyle_app.routes) > 0


def test_handler_success():
    """Test Lambda handler with successful event."""
    from app.travelstyle import handler

    # Mock event and context
    event = {
        "path": "/",
        "httpMethod": "GET",
        "queryStringParameters": None,
        "headers": {},
        "body": None,
        "isBase64Encoded": False,
    }
    context = MagicMock()

    # Mock logger to capture log messages
    with patch("app.travelstyle.logger") as mock_logger:
        # Mock Mangum to return a successful response
        with patch("app.travelstyle.Mangum") as mock_mangum:
            mock_mangum_instance = MagicMock()
            mock_mangum_instance.return_value = {
                "statusCode": 200,
                "body": '{"message": "Welcome to TravelStyle AI API"}',
                "headers": {"Content-Type": "application/json"},
            }
            mock_mangum.return_value = mock_mangum_instance

            # Call the handler
            response = handler(event, context)

            # Verify the response
            assert response["statusCode"] == 200
            assert "Welcome to TravelStyle AI API" in response["body"]

            # Verify logging was called
            assert mock_logger.info.call_count >= 4  # Multiple log calls
            mock_logger.info.assert_any_call(
                "Lambda invoked with event: {'path': '/', 'httpMethod': 'GET', 'queryStringParameters': None, 'headers': {}, 'body': None, 'isBase64Encoded': False}"
            )
            mock_logger.info.assert_any_call("Event path: /")
            mock_logger.info.assert_any_call("Event httpMethod: GET")
            mock_logger.info.assert_any_call("Event queryStringParameters: None")


def test_handler_with_query_parameters():
    """Test Lambda handler with query parameters."""
    from app.travelstyle import handler

    # Mock event with query parameters
    event = {
        "path": "/health",
        "httpMethod": "GET",
        "queryStringParameters": {"param1": "value1", "param2": "value2"},
        "headers": {},
        "body": None,
        "isBase64Encoded": False,
    }
    context = MagicMock()

    # Mock logger to capture log messages
    with patch("app.travelstyle.logger") as mock_logger:
        # Mock Mangum to return a successful response
        with patch("app.travelstyle.Mangum") as mock_mangum:
            mock_mangum_instance = MagicMock()
            mock_mangum_instance.return_value = {
                "statusCode": 200,
                "body": '{"status": "healthy"}',
                "headers": {"Content-Type": "application/json"},
            }
            mock_mangum.return_value = mock_mangum_instance

            # Call the handler
            response = handler(event, context)

            # Verify the response
            assert response["statusCode"] == 200

            # Verify logging was called with query parameters
            mock_logger.info.assert_any_call(
                "Event queryStringParameters: {'param1': 'value1', 'param2': 'value2'}"
            )


def test_handler_with_missing_path():
    """Test Lambda handler with missing path in event."""
    from app.travelstyle import handler

    # Mock event without path
    event = {
        "httpMethod": "GET",
        "queryStringParameters": None,
        "headers": {},
        "body": None,
        "isBase64Encoded": False,
    }
    context = MagicMock()

    # Mock logger to capture log messages
    with patch("app.travelstyle.logger") as mock_logger:
        # Mock Mangum to return a successful response
        with patch("app.travelstyle.Mangum") as mock_mangum:
            mock_mangum_instance = MagicMock()
            mock_mangum_instance.return_value = {
                "statusCode": 200,
                "body": '{"message": "test"}',
                "headers": {"Content-Type": "application/json"},
            }
            mock_mangum.return_value = mock_mangum_instance

            # Call the handler
            response = handler(event, context)

            # Verify the response
            assert response["statusCode"] == 200

            # Verify logging was called with NO_PATH
            mock_logger.info.assert_any_call("Event path: NO_PATH")


def test_handler_with_missing_http_method():
    """Test Lambda handler with missing httpMethod in event."""
    from app.travelstyle import handler

    # Mock event without httpMethod
    event = {
        "path": "/",
        "queryStringParameters": None,
        "headers": {},
        "body": None,
        "isBase64Encoded": False,
    }
    context = MagicMock()

    # Mock logger to capture log messages
    with patch("app.travelstyle.logger") as mock_logger:
        # Mock Mangum to return a successful response
        with patch("app.travelstyle.Mangum") as mock_mangum:
            mock_mangum_instance = MagicMock()
            mock_mangum_instance.return_value = {
                "statusCode": 200,
                "body": '{"message": "test"}',
                "headers": {"Content-Type": "application/json"},
            }
            mock_mangum.return_value = mock_mangum_instance

            # Call the handler
            response = handler(event, context)

            # Verify the response
            assert response["statusCode"] == 200

            # Verify logging was called with NO_METHOD
            mock_logger.info.assert_any_call("Event httpMethod: NO_METHOD")


def test_handler_with_missing_query_parameters():
    """Test Lambda handler with missing queryStringParameters in event."""
    from app.travelstyle import handler

    # Mock event without queryStringParameters
    event = {
        "path": "/",
        "httpMethod": "GET",
        "headers": {},
        "body": None,
        "isBase64Encoded": False,
    }
    context = MagicMock()

    # Mock logger to capture log messages
    with patch("app.travelstyle.logger") as mock_logger:
        # Mock Mangum to return a successful response
        with patch("app.travelstyle.Mangum") as mock_mangum:
            mock_mangum_instance = MagicMock()
            mock_mangum_instance.return_value = {
                "statusCode": 200,
                "body": '{"message": "test"}',
                "headers": {"Content-Type": "application/json"},
            }
            mock_mangum.return_value = mock_mangum_instance

            # Call the handler
            response = handler(event, context)

            # Verify the response
            assert response["statusCode"] == 200

            # Verify logging was called with NO_QUERY
            mock_logger.info.assert_any_call("Event queryStringParameters: NO_QUERY")


def test_handler_exception():
    """Test Lambda handler with exception handling."""
    from app.travelstyle import handler

    # Mock event and context
    event = {
        "path": "/",
        "httpMethod": "GET",
        "queryStringParameters": None,
        "headers": {},
        "body": None,
        "isBase64Encoded": False,
    }
    context = MagicMock()

    # Mock logger to capture log messages
    with patch("app.travelstyle.logger") as mock_logger:
        # Mock Mangum to raise an exception
        with patch("app.travelstyle.Mangum") as mock_mangum:
            mock_mangum_instance = MagicMock()
            mock_mangum_instance.side_effect = Exception("Test exception")
            mock_mangum.return_value = mock_mangum_instance

            # Call the handler and expect it to raise the exception
            with patch("builtins.print") as mock_print:
                try:
                    handler(event, context)
                    assert False, "Expected exception to be raised"
                except Exception as e:
                    assert str(e) == "Test exception"

                    # Verify error logging was called
                    mock_logger.error.assert_called_once_with(
                        "Lambda handler error: Test exception"
                    )
                    mock_print.assert_called_once_with("Lambda handler error: Test exception")


def test_handler_with_post_request():
    """Test Lambda handler with POST request."""
    from app.travelstyle import handler

    # Mock event for POST request
    event = {
        "path": "/api/v1/chat",
        "httpMethod": "POST",
        "queryStringParameters": None,
        "headers": {"Content-Type": "application/json"},
        "body": '{"message": "test message"}',
        "isBase64Encoded": False,
    }
    context = MagicMock()

    # Mock logger to capture log messages
    with patch("app.travelstyle.logger") as mock_logger:
        # Mock Mangum to return a successful response
        with patch("app.travelstyle.Mangum") as mock_mangum:
            mock_mangum_instance = MagicMock()
            mock_mangum_instance.return_value = {
                "statusCode": 200,
                "body": '{"response": "test response"}',
                "headers": {"Content-Type": "application/json"},
            }
            mock_mangum.return_value = mock_mangum_instance

            # Call the handler
            response = handler(event, context)

            # Verify the response
            assert response["statusCode"] == 200
            assert "test response" in response["body"]

            # Verify logging was called
            mock_logger.info.assert_any_call("Event path: /api/v1/chat")
            mock_logger.info.assert_any_call("Event httpMethod: POST")


def test_handler_with_base64_encoded_body():
    """Test Lambda handler with base64 encoded body."""
    from app.travelstyle import handler

    # Mock event with base64 encoded body
    event = {
        "path": "/api/v1/chat",
        "httpMethod": "POST",
        "queryStringParameters": None,
        "headers": {"Content-Type": "application/json"},
        "body": "eyJtZXNzYWdlIjogInRlc3QgbWVzc2FnZSJ9",  # base64 encoded JSON
        "isBase64Encoded": True,
    }
    context = MagicMock()

    # Mock logger to capture log messages
    with patch("app.travelstyle.logger") as mock_logger:
        # Mock Mangum to return a successful response
        with patch("app.travelstyle.Mangum") as mock_mangum:
            mock_mangum_instance = MagicMock()
            mock_mangum_instance.return_value = {
                "statusCode": 200,
                "body": '{"response": "test response"}',
                "headers": {"Content-Type": "application/json"},
            }
            mock_mangum.return_value = mock_mangum_instance

            # Call the handler
            response = handler(event, context)

            # Verify the response
            assert response["statusCode"] == 200

            # Verify logging was called
            mock_logger.info.assert_any_call("Event path: /api/v1/chat")
            mock_logger.info.assert_any_call("Event httpMethod: POST")


def test_handler_logging_and_print():
    """Test that handler logs and prints response information."""
    from app.travelstyle import handler

    # Mock event and context
    event = {
        "path": "/",
        "httpMethod": "GET",
        "queryStringParameters": None,
        "headers": {},
        "body": None,
        "isBase64Encoded": False,
    }
    context = MagicMock()

    # Mock logger and print to capture output
    with patch("app.travelstyle.logger") as mock_logger:
        with patch("builtins.print") as mock_print:
            # Mock Mangum to return a successful response
            with patch("app.travelstyle.Mangum") as mock_mangum:
                mock_mangum_instance = MagicMock()
                mock_response = {
                    "statusCode": 200,
                    "body": '{"message": "test"}',
                    "headers": {"Content-Type": "application/json"},
                }
                mock_mangum_instance.return_value = mock_response
                mock_mangum.return_value = mock_mangum_instance

                # Call the handler
                response = handler(event, context)

                # Verify logging and print were called with response
                mock_logger.info.assert_any_call(f"Lambda response: {mock_response}")
                mock_print.assert_any_call(f"Lambda response: {mock_response}")

                # Verify the response is returned
                assert response == mock_response
