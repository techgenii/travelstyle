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
Configuration settings for Supabase services.
Centralizes all Supabase-related configuration and constants.
"""

from dataclasses import dataclass

from app.core.config import settings


@dataclass
class SupabaseTableConfig:
    """Configuration for a Supabase table."""

    name: str
    primary_key: str = "id"
    unique_constraints: list[str] = None
    indexes: list[str] = None
    rls_enabled: bool = True

    def __post_init__(self):
        if self.unique_constraints is None:
            self.unique_constraints = []
        if self.indexes is None:
            self.indexes = []


@dataclass
class SupabaseViewConfig:
    """Configuration for a Supabase view."""

    name: str
    security_invoker: bool = False
    rls_enabled: bool = True


class SupabaseConfig:
    """Configuration class for Supabase settings."""

    # Connection settings
    URL = settings.SUPABASE_URL
    KEY = settings.SUPABASE_KEY

    # Connection pooling settings
    MAX_CONNECTIONS = 10
    CONNECTION_TIMEOUT = 30
    HEALTH_CHECK_INTERVAL = 300  # 5 minutes

    # Cache settings
    DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds
    WEATHER_CACHE_TTL = 3600  # 1 hour
    CULTURAL_CACHE_TTL = 86400  # 24 hours
    CURRENCY_CACHE_TTL = 3600  # 1 hour

    # Rate limiting settings
    CACHE_RATE_LIMIT = 100  # requests per minute
    DB_RATE_LIMIT = 1000  # requests per minute

    # Table configurations
    TABLES = {
        # Cache tables
        "weather_cache": SupabaseTableConfig(
            name="weather_cache",
            unique_constraints=["destination"],
            indexes=["destination", "expires_at"],
        ),
        "cultural_insights_cache": SupabaseTableConfig(
            name="cultural_insights_cache",
            unique_constraints=["destination"],
            indexes=["destination", "expires_at"],
        ),
        "currency_rates_cache": SupabaseTableConfig(
            name="currency_rates_cache",
            unique_constraints=["base_currency"],
            indexes=["base_currency", "expires_at"],
        ),
        # Core user tables
        "users": SupabaseTableConfig(
            name="users",
            unique_constraints=["email", "auth_id"],
            indexes=["email", "auth_id", "created_at"],
        ),
        "user_preferences": SupabaseTableConfig(
            name="user_preferences",
            unique_constraints=["user_id"],
            indexes=["user_id", "created_at"],
        ),
        "user_auth_tokens": SupabaseTableConfig(
            name="user_auth_tokens",
            indexes=["user_id", "token_type", "expires_at"],
        ),
        "system_settings": SupabaseTableConfig(
            name="system_settings",
            unique_constraints=["setting_key"],
            indexes=["setting_key", "is_public"],
        ),
        # Chat and conversation tables
        "conversations": SupabaseTableConfig(
            name="conversations",
            indexes=["user_id", "created_at", "type", "destination"],
        ),
        "chat_sessions": SupabaseTableConfig(
            name="chat_sessions",
            indexes=["user_id", "conversation_id", "is_active", "expires_at"],
        ),
        "conversation_messages": SupabaseTableConfig(
            name="conversation_messages",
            indexes=["conversation_id", "created_at", "role", "message_type"],
        ),
        "chat_bookmarks": SupabaseTableConfig(
            name="chat_bookmarks",
            indexes=["user_id", "conversation_id", "created_at"],
        ),
        # User data tables
        "currency_favorites": SupabaseTableConfig(
            name="currency_favorites",
            indexes=["user_id", "from_currency", "to_currency", "is_primary"],
        ),
        "packing_templates": SupabaseTableConfig(
            name="packing_templates",
            indexes=["user_id", "packing_method", "destination_type", "climate_type"],
        ),
        "saved_destinations": SupabaseTableConfig(
            name="saved_destinations",
            indexes=["user_id", "destination_name", "is_favorite"],
        ),
        # Style and fashion tables
        "clothing_styles": SupabaseTableConfig(
            name="clothing_styles",
            unique_constraints=["style_name"],
            indexes=["category", "region_applicability", "qloo_entity_id"],
        ),
        "user_style_preferences": SupabaseTableConfig(
            name="user_style_preferences",
            unique_constraints=["user_id", "style_id"],
            indexes=["user_id", "style_id", "preference_level"],
        ),
        # Analytics and tracking tables
        "api_request_logs": SupabaseTableConfig(
            name="api_request_logs",
            indexes=["user_id", "session_id", "endpoint", "created_at", "response_status"],
        ),
        "api_usage_tracking": SupabaseTableConfig(
            name="api_usage_tracking",
            indexes=["user_id", "api_name", "date", "endpoint"],
        ),
        "recommendation_history": SupabaseTableConfig(
            name="recommendation_history",
            indexes=["user_id", "conversation_id", "recommendation_type", "was_used", "created_at"],
        ),
        "response_feedback": SupabaseTableConfig(
            name="response_feedback",
            indexes=["user_id", "conversation_id", "feedback_type", "created_at"],
        ),
        "ui_analytics": SupabaseTableConfig(
            name="ui_analytics",
            indexes=["user_id", "session_id", "event_type", "created_at"],
        ),
    }

    # View configurations
    VIEWS = {
        "user_profile_view": SupabaseViewConfig(
            name="user_profile_view",
            security_invoker=True,
        ),
        "user_style_preferences_summary": SupabaseViewConfig(
            name="user_style_preferences_summary",
            security_invoker=True,
        ),
        "api_performance_summary": SupabaseViewConfig(
            name="api_performance_summary",
            security_invoker=False,
        ),
    }

    # Query limits
    DEFAULT_QUERY_LIMIT = 1000
    MAX_QUERY_LIMIT = 10000

    # Error messages
    ERROR_MESSAGES = {
        "connection_failed": "Failed to connect to Supabase",
        "invalid_credentials": "Invalid Supabase credentials",
        "table_not_found": "Table not found",
        "rate_limited": "Rate limit exceeded",
        "permission_denied": "Permission denied",
        "validation_error": "Data validation failed",
    }

    @classmethod
    def get_table_config(cls, table_name: str) -> SupabaseTableConfig:
        """Get configuration for a specific table."""
        return cls.TABLES.get(table_name, SupabaseTableConfig(name=table_name))

    @classmethod
    def get_view_config(cls, view_name: str) -> SupabaseViewConfig:
        """Get configuration for a specific view."""
        return cls.VIEWS.get(view_name, SupabaseViewConfig(name=view_name))

    @classmethod
    def validate_connection_settings(cls) -> bool:
        """Validate that connection settings are properly configured."""
        return bool(cls.URL and cls.KEY)

    @classmethod
    def get_cache_ttl(cls, cache_type: str) -> int:
        """Get TTL for a specific cache type."""
        ttl_map = {
            "weather": cls.WEATHER_CACHE_TTL,
            "cultural": cls.CULTURAL_CACHE_TTL,
            "currency": cls.CURRENCY_CACHE_TTL,
        }
        return ttl_map.get(cache_type, cls.DEFAULT_CACHE_TTL)

    @classmethod
    def get_rate_limit(cls, operation_type: str) -> int:
        """Get rate limit for a specific operation type."""
        rate_limits = {
            "cache": cls.CACHE_RATE_LIMIT,
            "database": cls.DB_RATE_LIMIT,
        }
        return rate_limits.get(operation_type, cls.DB_RATE_LIMIT)


# Export configuration instance
supabase_config = SupabaseConfig()
