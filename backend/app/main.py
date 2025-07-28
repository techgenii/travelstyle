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

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

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
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered travel wardrobe consultant with cultural intelligence",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Configure appropriately for production
)

# Exception handlers
app.add_exception_handler(HTTPException, custom_http_exception_handler)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(
    recommendations.router,
    prefix=f"{settings.API_V1_STR}/recs",
    tags=["recommendations"],
)
app.include_router(user.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(currency.router, prefix=f"{settings.API_V1_STR}/currency", tags=["currency"])


@app.get("/")
async def root():
    """Root endpoint returning API welcome message and version."""
    return {"message": "Welcome to TravelStyle AI API", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring API status."""
    return {"status": "healthy", "cache": "supabase"}


if __name__ == "__main__":
    # Note: Binding to 0.0.0.0 is necessary for development server
    # In production, use proper host configuration
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104

# Expose the FastAPI app as the handler
handler = app
