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

"""Currency conversion API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.responses import ChatResponse, QuickReply
from app.models.travel import CurrencyConvertRequest, CurrencyPairRequest
from app.services.currency import CurrencyService
from app.utils.rate_limiter import rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)

# Local dependency to avoid linter warnings
current_user_dependency = Depends(get_current_user)

# Create a single instance of the modular currency service
currency_service = CurrencyService()


@router.get("/rates/{base_currency}")
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


@router.post("/convert-amount")
@rate_limit(calls=15, period=60)
async def convert_currency_amount(
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


@router.post("/pair")
@rate_limit(calls=10, period=60)
async def get_pair_exchange_rate(
    payload: CurrencyPairRequest,
    current_user: dict = current_user_dependency,
):
    """Get exchange rate for a specific currency pair"""
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


@router.post("/convert", response_model=ChatResponse)
async def convert_currency(
    request: dict,
    current_user: dict = current_user_dependency,
):
    """
    Convert currency endpoint using OpenAI parsing
    """
    try:
        user_message = request.get("message", "")

        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Handle the currency request using the unified service
        result = await currency_service.handle_currency_request(user_message)

        # Handle case where result is None (service error)
        if result is None:
            return ChatResponse(
                message="Sorry, I couldn't process that currency conversion request.",
                confidence_score=0.0,
            )

        # Check if this is the new format (with success field)
        if isinstance(result, dict) and result.get("success"):
            # New format - handle structured response
            request_type = result.get("request_type", "conversion")

            if request_type == "conversion" and "data" in result:
                # Handle conversion response
                conversion_data = result["data"]
                original = conversion_data.get("original", {})
                converted = conversion_data.get("converted", {})
                rate = conversion_data.get("rate")

                if all([original, converted, rate is not None]):
                    message = (
                        f"{original.get('amount', 0):.2f} {original.get('currency', '')} = "
                        f"{converted.get('amount', 0):.2f} {converted.get('currency', '')} "
                        f"(Rate: {rate:.4f})"
                    )

                    quick_replies = [
                        QuickReply(text="Convert different amount", action="currency_convert"),
                        QuickReply(text="Other currencies", action="currency_list"),
                    ]

                    # Add specific quick reply if amount was provided
                    if original.get("amount", 0) > 0:
                        quick_replies.insert(
                            0, QuickReply(text="Show rate only", action="currency_rate_only")
                        )

                    return ChatResponse(
                        message=message, confidence_score=0.9, quick_replies=quick_replies
                    )

            elif request_type == "rate" and "data" in result:
                # Handle rate response
                rate_data = result["data"]
                base_code = rate_data.get("base_code", "")
                target_code = rate_data.get("target_code", "")
                rate = rate_data.get("rate")

                if all([base_code, target_code, rate is not None]):
                    message = f"Exchange rate: 1 {base_code} = {rate:.4f} {target_code}"

                    quick_replies = [
                        QuickReply(text="Convert amount", action="currency_convert"),
                        QuickReply(text="Other currencies", action="currency_list"),
                    ]

                    return ChatResponse(
                        message=message, confidence_score=0.9, quick_replies=quick_replies
                    )

            elif request_type == "help":
                # Handle help response
                message = result.get("message", "Currency conversion help")
                quick_replies = [
                    QuickReply(text="Convert currency", action="currency_convert"),
                    QuickReply(text="Check rates", action="currency_rates"),
                ]

                return ChatResponse(
                    message=message, confidence_score=0.9, quick_replies=quick_replies
                )

            # Fallback for other successful responses
            return ChatResponse(
                message=result.get("message", "Currency request processed successfully"),
                confidence_score=0.8,
            )
        else:
            # Handle failed requests
            error_message = (
                result.get("message", "Sorry, I couldn't process that currency conversion request.")
                if isinstance(result, dict)
                else "Sorry, I couldn't process that currency conversion request."
            )

            return ChatResponse(
                message=error_message,
                confidence_score=0.0,
            )

    except Exception as e:
        logger.error("Currency conversion error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to process currency request") from e


@router.get("/supported")
async def get_supported_currencies(current_user: dict = current_user_dependency):
    """Get list of supported currencies"""
    try:
        currencies = currency_service.get_supported_currencies()
        return {"currencies": currencies}
    except Exception as e:
        logger.error("Get supported currencies error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to get supported currencies") from e


@router.post("/validate")
async def validate_currency_code(
    request: dict,
    current_user: dict = current_user_dependency,
):
    """Validate a currency code"""
    try:
        currency_code = request.get("currency_code", "")

        if not currency_code:
            raise HTTPException(status_code=400, detail="Currency code is required")

        is_valid = currency_service.validate_currency_code(currency_code)

        return {"currency_code": currency_code.upper(), "is_valid": is_valid, "supported": is_valid}

    except Exception as e:
        logger.error("Currency validation error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to validate currency") from e


@router.post("/parse")
async def parse_currency_message(
    request: dict,
    current_user: dict = current_user_dependency,
):
    """Parse currency message using OpenAI (for testing/debugging)"""
    try:
        user_message = request.get("message", "")

        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        parsed_data = await currency_service.parse_currency_request(user_message)

        return {
            "parsed_data": parsed_data,
            "is_valid": all(
                [
                    parsed_data.get("first_country"),
                    parsed_data.get("second_country"),
                    currency_service.validate_currency_code(parsed_data.get("first_country", "")),
                    currency_service.validate_currency_code(parsed_data.get("second_country", "")),
                ]
            ),
        }

    except Exception as e:
        logger.error("Currency parsing error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to parse currency message") from e
