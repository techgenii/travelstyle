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
Custom error handlers for the TravelStyle AI application.
"""

import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def custom_http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Custom HTTP exception handler with logging."""
    if not isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error", "status_code": 500}
        )

    logger.error("HTTP %d: %s for %s", exc.status_code, exc.detail, request.url)
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail, "status_code": exc.status_code}
    )
