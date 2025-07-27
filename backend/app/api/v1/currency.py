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
from app.services.currency_conversion_service import currency_conversion_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Local dependency to avoid linter warnings
current_user_dependency = Depends(get_current_user)


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

        # Handle the currency request
        result = await currency_conversion_service.handle_currency_request(user_message)

        if result["type"] == "currency_rate":
            quick_replies = [
                QuickReply(text="Convert different amount", action="currency_convert"),
                QuickReply(text="Other currencies", action="currency_list"),
            ]

            # Add specific quick reply if amount was provided
            if result.get("amount", 0) > 0:
                quick_replies.insert(
                    0, QuickReply(text="Show rate only", action="currency_rate_only")
                )

            return ChatResponse(
                message=result["message"], confidence_score=0.9, quick_replies=quick_replies
            )
        else:
            return ChatResponse(message=result["message"], confidence_score=0.0)

    except Exception as e:
        logger.error("Currency conversion error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to process currency request") from e


@router.get("/supported")
async def get_supported_currencies(current_user: dict = current_user_dependency):
    """Get list of supported currencies"""
    try:
        currencies = currency_conversion_service.get_supported_currencies()
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

        is_valid = currency_conversion_service.validate_currency_code(currency_code)

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

        parsed_data = await currency_conversion_service.parse_currency_request(user_message)

        return {
            "parsed_data": parsed_data,
            "is_valid": all(
                [
                    parsed_data.get("first_country"),
                    parsed_data.get("second_country"),
                    currency_conversion_service.validate_currency_code(
                        parsed_data.get("first_country", "")
                    ),
                    currency_conversion_service.validate_currency_code(
                        parsed_data.get("second_country", "")
                    ),
                ]
            ),
        }

    except Exception as e:
        logger.error("Currency parsing error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to parse currency message") from e
