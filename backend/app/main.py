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

from app.api.v1 import auth, chat, recommendations, user
from app.core.config import settings
from app.utils.error_handlers import custom_http_exception_handler

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    prefix=f"{settings.API_V1_STR}/recommendations",
    tags=["recommendations"],
)
app.include_router(user.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])


@app.get("/")
async def root():
    """Root endpoint returning API welcome message and version."""
    return {"message": "Welcome to TravelStyle AI API", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring API status."""
    return {"status": "healthy", "cache": "supabase"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Use localhost for development
        port=8000,
        reload=True,
        log_level="info",
    )
