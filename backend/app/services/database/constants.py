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
Database constants for TravelStyle AI application.
"""


class DatabaseTables:
    """Constants for database table names"""

    # Core tables
    USERS = "users"
    USER_PREFERENCES = "user_preferences"
    USER_AUTH_TOKENS = "user_auth_tokens"
    SYSTEM_SETTINGS = "system_settings"

    # Chat and conversation tables
    CONVERSATIONS = "conversations"
    CHAT_SESSIONS = "chat_sessions"
    CONVERSATION_MESSAGES = "conversation_messages"
    CHAT_BOOKMARKS = "chat_bookmarks"

    # User data tables
    CURRENCY_FAVORITES = "currency_favorites"
    PACKING_TEMPLATES = "packing_templates"
    SAVED_DESTINATIONS = "saved_destinations"
    USER_DESTINATIONS = "saved_destinations"  # Alias for backward compatibility

    # Style and fashion tables
    CLOTHING_STYLES = "clothing_styles"
    USER_STYLE_PREFERENCES = "user_style_preferences"

    # Cache tables
    WEATHER_CACHE = "weather_cache"
    CULTURAL_INSIGHTS_CACHE = "cultural_insights_cache"
    CURRENCY_RATES_CACHE = "currency_rates_cache"

    # Analytics and tracking tables
    API_REQUEST_LOGS = "api_request_logs"
    API_USAGE_TRACKING = "api_usage_tracking"
    RECOMMENDATION_HISTORY = "recommendation_history"
    RESPONSE_FEEDBACK = "response_feedback"
    UI_ANALYTICS = "ui_analytics"

    # Views
    USER_PROFILE_VIEW = "user_profile_view"
    USER_STYLE_PREFERENCES_SUMMARY = "user_style_preferences_summary"
    API_PERFORMANCE_SUMMARY = "api_performance_summary"
