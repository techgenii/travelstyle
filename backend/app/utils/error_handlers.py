"""
Custom error handlers for the TravelStyle AI application.
"""
import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom HTTP exception handler with logging."""
    logger.error("HTTP %d: %s for %s", exc.status_code, exc.detail, request.url)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )
