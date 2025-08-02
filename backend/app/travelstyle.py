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
travelstyle_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        return {
            "statusCode": 500,
            "body": f'{{"detail":"Internal server error: {str(e)}","status_code":500}}',
            "headers": {
                "content-type": "application/json",
                "access-control-allow-origin": "*",
                "access-control-allow-credentials": "true",
            },
            "isBase64Encoded": False,
        }
