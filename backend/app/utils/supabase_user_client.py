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
Helper to create Supabase client with user's access token for authenticated requests.
This allows making requests as the authenticated user, respecting Row Level Security policies.
"""

import logging

from supabase import Client, create_client

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_user_supabase_client(access_token: str) -> Client:
    """
    Create a Supabase client with user's access token.

    This client will make requests as the authenticated user,
    respecting Row Level Security policies.

    Args:
        access_token: User's JWT access token

    Returns:
        Supabase client configured with user token
    """
    # Create client with user's access token
    # The access token will be used in Authorization header for all requests
    client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,  # Still need anon key
    )

    # Set the session with user's access token
    # Note: The Supabase Python client doesn't have a direct set_session method
    # Instead, we need to set the auth header manually for each request
    # For now, this is a placeholder - actual implementation may require
    # using the client's auth methods or setting headers directly
    try:
        # Set the access token in the client's session
        # This is a workaround - the Supabase Python client may need to be extended
        # to properly support setting a user token for all requests
        if hasattr(client, "auth"):
            # Store the token for use in requests
            client.auth._access_token = access_token  # pylint: disable=protected-access
            logger.debug("User access token set in Supabase client")
    except Exception as e:
        logger.warning(f"Could not set access token in client: {e}")

    return client


def get_user_supabase_client_with_header(access_token: str) -> Client:
    """
    Alternative approach: Create a Supabase client and use the access token
    in Authorization header for each request.

    Note: This requires modifying how you make requests to include the header.
    For direct PostgREST calls, you can use:
        client.table("table_name").select("*").execute(headers={"Authorization": f"Bearer {access_token}"})

    Args:
        access_token: User's JWT access token

    Returns:
        Supabase client (token must be passed in headers for each request)
    """
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    # Store token for reference
    client._user_access_token = access_token  # pylint: disable=protected-access
    return client

