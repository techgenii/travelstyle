from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import logging

from app.services.qloo_service import qloo_service
from app.services.weather_service import weather_service
from app.services.currency_service import currency_service
from app.api.deps import get_current_user
from app.utils.rate_limiter import rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/cultural/{destination}")
@rate_limit(calls=20, period=60)
async def get_cultural_insights(
    destination: str,
    context: str = Query("leisure", description="Travel context: leisure, business, formal, active"),
    current_user: dict = Depends(get_current_user)
):
    """Get cultural insights for a destination"""
    
    try:
        insights = await qloo_service.get_cultural_insights(destination, context)
        
        if not insights:
            raise HTTPException(
                status_code=404,
                detail=f"Cultural insights not available for {destination}"
            )
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cultural insights error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve cultural insights"
        )

@router.get("/weather/{destination}")
@rate_limit(calls=30, period=60)
async def get_weather_forecast(
    destination: str,
    dates: Optional[List[str]] = Query(None, description="Travel dates in YYYY-MM-DD format"),
    current_user: dict = Depends(get_current_user)
):
    """Get weather forecast for destination"""
    
    try:
        weather_data = await weather_service.get_weather_data(destination, dates)
        
        if not weather_data:
            raise HTTPException(
                status_code=404,
                detail=f"Weather data not available for {destination}"
            )
        
        return weather_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weather forecast error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve weather forecast"
        )

@router.get("/currency/{base_currency}")
@rate_limit(calls=10, period=60)
async def get_exchange_rates(
    base_currency: str = "USD",
    current_user: dict = Depends(get_current_user)
):
    """Get current exchange rates"""
    
    try:
        rates = await currency_service.get_exchange_rates(base_currency.upper())
        
        if not rates:
            raise HTTPException(
                status_code=404,
                detail="Exchange rates not available"
            )
        
        return rates
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exchange rates error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve exchange rates"
        )

@router.post("/currency/convert")
@rate_limit(calls=15, period=60)
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    current_user: dict = Depends(get_current_user)
):
    """Convert currency amounts"""
    
    try:
        conversion = await currency_service.convert_currency(
            amount=amount,
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper()
        )
        
        if not conversion:
            raise HTTPException(
                status_code=400,
                detail="Currency conversion failed"
            )
        
        return conversion
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Currency conversion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to convert currency"
        ) 