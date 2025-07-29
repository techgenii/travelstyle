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
Recommendations API endpoints for TravelStyle AI application.
Provides cultural insights and weather forecasts.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user
from app.models.travel import WeatherRequest
from app.services.qloo_service import qloo_service
from app.services.weather_service import weather_service
from app.utils.rate_limiter import rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)

# Local dependency to avoid linter warnings
current_user_dependency = Depends(get_current_user)

# Query parameter defaults
context_query = Query("leisure", description="Travel context: leisure, business, formal, active")
dates_query = Query(None, description="Travel dates in YYYY-MM-DD format")


@router.get("/cultural/{destination}")
@rate_limit(calls=20, period=60)
async def get_cultural_insights(
    destination: str,
    context: str = context_query,
    current_user: dict = current_user_dependency,
):
    """Get cultural insights for a destination"""

    try:
        insights = await qloo_service.get_cultural_insights(destination, context)

        if not insights:
            raise HTTPException(
                status_code=404, detail=f"Cultural insights not available for {destination}"
            )

        return insights

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Cultural insights error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to retrieve cultural insights") from e


@router.post("/weather")
@rate_limit(calls=30, period=60)
async def get_weather_forecast(
    request: WeatherRequest,
    current_user: dict = current_user_dependency,
):
    """Get weather forecast for destination"""

    try:
        weather_data = await weather_service.get_weather_data(request.destination, request.dates)

        if not weather_data:
            raise HTTPException(
                status_code=404, detail=f"Weather data not available for {request.destination}"
            )

        return weather_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Weather forecast error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to retrieve weather forecast") from e
