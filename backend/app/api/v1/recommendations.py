"""
Recommendations API endpoints for TravelStyle AI application.
Provides cultural insights, weather forecasts, and currency services.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user
from app.models.travel import CurrencyConvertRequest, CurrencyPairRequest, WeatherRequest
from app.services.currency_service import currency_service
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


@router.get("/currency/{base_currency}")
@rate_limit(calls=10, period=60)
async def get_exchange_rates(
    base_currency: str = "USD", current_user: dict = current_user_dependency
):
    """Get current exchange rates"""

    try:
        rates = await currency_service.get_exchange_rates(base_currency.upper())

        if not rates:
            raise HTTPException(status_code=404, detail="Exchange rates not available")

        return rates

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Exchange rates error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to retrieve exchange rates") from e


@router.post("/currency/convert")
@rate_limit(calls=15, period=60)
async def convert_currency(
    payload: CurrencyConvertRequest,
    current_user: dict = current_user_dependency,
):
    """Convert currency amounts"""

    try:
        conversion = await currency_service.convert_currency(
            amount=payload.amount,
            from_currency=payload.from_currency.strip().upper(),
            to_currency=payload.to_currency.strip().upper(),
        )

        if not conversion:
            raise HTTPException(status_code=400, detail="Currency conversion failed")

        return conversion

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Currency conversion error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to convert currency") from e


@router.post("/currency/pair")
@rate_limit(calls=10, period=60)
async def get_pair_exchange_rate(
    payload: CurrencyPairRequest,
    current_user: dict = current_user_dependency,
):
    try:
        result = await currency_service.get_pair_exchange_rate(
            payload.base_currency, payload.target_currency
        )
        if not result:
            raise HTTPException(status_code=404, detail="Exchange rate not available")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Pair exchange rate error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to retrieve pair exchange rate") from e
