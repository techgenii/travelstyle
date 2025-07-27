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
User utility functions for TravelStyle AI application.
"""


def extract_user_profile(user):
    """Extract user profile information from a Supabase user object or user_profile_view row."""
    if not user:
        return None

    # Get names and selected_style_names from user metadata if available, else use direct attributes
    first_name = None
    last_name = None
    selected_style_names = None
    if hasattr(user, "user_metadata") and user.user_metadata:
        if isinstance(user.user_metadata, dict):
            first_name = user.user_metadata.get("first_name")
            last_name = user.user_metadata.get("last_name")
            selected_style_names = user.user_metadata.get("selected_style_names")
        else:
            first_name = getattr(user.user_metadata, "first_name", None)
            last_name = getattr(user.user_metadata, "last_name", None)
            selected_style_names = getattr(user.user_metadata, "selected_style_names", None)
    else:
        first_name = getattr(user, "first_name", None)
        last_name = getattr(user, "last_name", None)
        selected_style_names = getattr(user, "selected_style_names", None)

    return {
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", None),
        "first_name": first_name,
        "last_name": last_name,
        "profile_completed": getattr(user, "profile_completed", None),
        "profile_picture_url": getattr(user, "profile_picture_url", None),
        "style_preferences": getattr(user, "style_preferences", None),
        "size_info": getattr(user, "size_info", None),
        "travel_patterns": getattr(user, "travel_patterns", None),
        "quick_reply_preferences": getattr(user, "quick_reply_preferences", None),
        "packing_methods": getattr(user, "packing_methods", None),
        "currency_preferences": getattr(user, "currency_preferences", None),
        "created_at": getattr(user, "created_at", None),
        "updated_at": getattr(user, "updated_at", None),
        "last_login": getattr(user, "last_login", None),
        "email_confirmed_at": getattr(user, "email_confirmed_at", None),
        "last_sign_in_at": getattr(user, "last_sign_in_at", None),
        "selected_style_names": selected_style_names if selected_style_names is not None else [],
    }
