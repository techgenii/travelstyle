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
TravelStyle AI FastAPI main application entrypoint.
Initializes the FastAPI app, middleware, routers, and error handlers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from mangum import Mangum

from app.api.v1 import auth, chat, currency, recommendations, user
from app.core.config import settings
from app.utils.error_handlers import custom_http_exception_handler

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("TravelStyle AI application starting...")


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):  # pylint: disable=unused-argument
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting TravelStyle AI application...")
    yield
    # Shutdown
    logger.info("Shutting down TravelStyle AI application...")


# Create FastAPI application
travelstyle_app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered travel wardrobe consultant with cultural intelligence",
    lifespan=lifespan,
)

# Create app variable for uvicorn
app = travelstyle_app

# Middleware
# Parse CORS origins from environment variable
if settings.CORS_ORIGINS == "*":
    cors_origins = ["*"]
    cors_origin_regex = None
    allow_creds = False
elif settings.TS_ENVIRONMENT == "development":
    # In development, allow specific origins + regex patterns for dynamic URLs
    origins_list = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    explicit_origins = [o for o in origins_list if not o.startswith("pattern:")]

    # Build regex from patterns (if any)
    patterns = [o.replace("pattern:", "") for o in origins_list if o.startswith("pattern:")]

    # Add default development patterns for Bolt.new and localhost
    default_patterns = [
        r".*\.webcontainer-api\.io$",  # Bolt.new dev URLs
        r".*\.bolt\.new$",              # Bolt.new production
        r"http://localhost:\d+$",       # Local dev
    ]
    patterns.extend(default_patterns)

    cors_origin_regex = "|".join([f"({p})" for p in patterns]) if patterns else None
    cors_origins = explicit_origins
    allow_creds = True
else:
    # Production: only explicit origins
    cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    cors_origin_regex = None
    allow_creds = True

cors_kwargs = {
    "allow_origins": cors_origins,
    "allow_credentials": allow_creds,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

if cors_origin_regex:
    cors_kwargs["allow_origin_regex"] = cors_origin_regex

travelstyle_app.add_middleware(
    CORSMiddleware,
    **cors_kwargs
)

travelstyle_app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Configure appropriately for production
)

# Exception handlers
travelstyle_app.add_exception_handler(HTTPException, custom_http_exception_handler)

# Include routers
travelstyle_app.include_router(
    auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"]
)
travelstyle_app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
travelstyle_app.include_router(
    recommendations.router,
    prefix=f"{settings.API_V1_STR}/recs",
    tags=["recommendations"],
)
travelstyle_app.include_router(user.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
travelstyle_app.include_router(
    currency.router, prefix=f"{settings.API_V1_STR}/currency", tags=["currency"]
)


@travelstyle_app.get("/")
async def root():
    """Root endpoint returning API welcome message and version."""
    return {"message": "Welcome to TravelStyle AI API", "version": settings.VERSION}


@travelstyle_app.get("/health")
async def health_check():
    """Health check endpoint for monitoring API status."""
    return {"status": "healthy", "cache": "supabase"}


def handler(event, context):
    logger.info(f"Lambda invoked with event: {event}")
    logger.info(f"Event path: {event.get('path', 'NO_PATH')}")
    logger.info(f"Event httpMethod: {event.get('httpMethod', 'NO_METHOD')}")
    logger.info(f"Event queryStringParameters: {event.get('queryStringParameters', 'NO_QUERY')}")

    try:
        # Check if required environment variables are set
        from app.core.config import settings

        logger.info(f"SUPABASE_URL set: {bool(settings.SUPABASE_URL)}")
        logger.info(f"SUPABASE_KEY set: {bool(settings.SUPABASE_KEY)}")

        # Use Mangum to handle the FastAPI app
        mangum_handler = Mangum(travelstyle_app)
        response = mangum_handler(event, context)
        logger.info(f"Lambda response: {response}")
        print(f"Lambda response: {response}")
        return response
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {e}")
        print(f"Lambda handler error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e}")

        # Return a proper error response instead of raising
        # Get the origin from the request if available
        origin = "*"
        request_origin = None
        if isinstance(event, dict):
            headers = event.get("headers", {}) or {}
            # Headers can be dict or list of tuples
            if isinstance(headers, dict):
                request_origin = headers.get("origin") or headers.get("Origin")
            elif isinstance(headers, list):
                for key, value in headers:
                    if key.lower() == "origin":
                        request_origin = value
                        break

        # Determine allowed origin based on CORS settings
        if settings.CORS_ORIGINS == "*":
            origin = "*"
            allow_creds = False
        elif settings.TS_ENVIRONMENT == "development":
            # In development, check if origin matches patterns
            import re
            patterns = [
                r".*\.webcontainer-api\.io$",
                r".*\.bolt\.new$",
                r"http://localhost:\d+$",
            ]
            if request_origin:
                for pattern in patterns:
                    if re.match(pattern, request_origin):
                        origin = request_origin
                        break
            # Fallback to first explicit origin if no match
            if origin == "*" and settings.CORS_ORIGINS:
                origins_list = [o.strip() for o in settings.CORS_ORIGINS.split(",") if not o.startswith("pattern:")]
                if origins_list:
                    origin = origins_list[0]
            allow_creds = True
        else:
            # Production: use first allowed origin or request origin if in list
            if request_origin and settings.CORS_ORIGINS:
                allowed_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
                if request_origin in allowed_origins:
                    origin = request_origin
                elif allowed_origins:
                    origin = allowed_origins[0]
            allow_creds = True

        headers = {
            "content-type": "application/json",
            "access-control-allow-origin": origin,
        }

        # Only add credentials header if not using wildcard
        if allow_creds:
            headers["access-control-allow-credentials"] = "true"

        return {
            "statusCode": 500,
            "body": f'{{"detail":"Internal server error: {str(e)}","status_code":500}}',
            "headers": headers,
            "isBase64Encoded": False,
        }
