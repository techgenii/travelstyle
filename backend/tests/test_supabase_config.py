"""
Tests for app/services/supabase/supabase_config.py
"""

from unittest.mock import patch

from app.services.supabase.supabase_config import (
    SupabaseConfig,
    SupabaseTableConfig,
    SupabaseViewConfig,
    supabase_config,
)


class TestSupabaseViewConfig:
    """Test SupabaseViewConfig dataclass."""

    def test_supabase_view_config_default_values(self):
        """Test SupabaseViewConfig with default values."""
        config = SupabaseViewConfig(name="test_view")

        assert config.name == "test_view"
        assert config.security_invoker is False
        assert config.rls_enabled is True

    def test_supabase_view_config_custom_values(self):
        """Test SupabaseViewConfig with custom values."""
        config = SupabaseViewConfig(
            name="custom_view",
            security_invoker=True,
            rls_enabled=False,
        )

        assert config.name == "custom_view"
        assert config.security_invoker is True
        assert config.rls_enabled is False


class TestSupabaseTableConfig:
    """Test SupabaseTableConfig dataclass."""

    def test_supabase_table_config_default_values(self):
        """Test SupabaseTableConfig with default values."""
        config = SupabaseTableConfig(name="test_table")

        assert config.name == "test_table"
        assert config.primary_key == "id"
        assert config.unique_constraints == []
        assert config.indexes == []
        assert config.rls_enabled is True

    def test_supabase_table_config_custom_values(self):
        """Test SupabaseTableConfig with custom values."""
        config = SupabaseTableConfig(
            name="custom_table",
            primary_key="uuid",
            unique_constraints=["email", "username"],
            indexes=["email_idx", "username_idx"],
            rls_enabled=False,
        )

        assert config.name == "custom_table"
        assert config.primary_key == "uuid"
        assert config.unique_constraints == ["email", "username"]
        assert config.indexes == ["email_idx", "username_idx"]
        assert config.rls_enabled is False

    def test_supabase_table_config_post_init_none_values(self):
        """Test __post_init__ method handles None values correctly."""
        # This tests the missing line 42 in coverage
        config = SupabaseTableConfig(name="test")

        # Verify that None values are converted to empty lists
        assert config.unique_constraints == []
        assert config.indexes == []

    def test_supabase_table_config_post_init_existing_values(self):
        """Test __post_init__ method preserves existing values."""
        config = SupabaseTableConfig(
            name="test", unique_constraints=["existing"], indexes=["existing_idx"]
        )

        # Verify that existing values are preserved
        assert config.unique_constraints == ["existing"]
        assert config.indexes == ["existing_idx"]


class TestSupabaseConfig:
    """Test SupabaseConfig class."""

    def test_supabase_config_constants(self):
        """Test that SupabaseConfig constants are properly defined."""
        assert SupabaseConfig.MAX_CONNECTIONS == 10
        assert SupabaseConfig.CONNECTION_TIMEOUT == 30
        assert SupabaseConfig.HEALTH_CHECK_INTERVAL == 300
        assert SupabaseConfig.DEFAULT_CACHE_TTL == 3600
        assert SupabaseConfig.WEATHER_CACHE_TTL == 3600
        assert SupabaseConfig.CULTURAL_CACHE_TTL == 86400
        assert SupabaseConfig.CURRENCY_CACHE_TTL == 3600
        assert SupabaseConfig.CACHE_RATE_LIMIT == 100
        assert SupabaseConfig.DB_RATE_LIMIT == 1000
        assert SupabaseConfig.DEFAULT_QUERY_LIMIT == 1000
        assert SupabaseConfig.MAX_QUERY_LIMIT == 10000

    def test_supabase_config_tables_structure(self):
        """Test that TABLES dictionary contains expected table configs."""
        expected_tables = [
            "weather_cache",
            "cultural_insights_cache",
            "currency_rates_cache",
            "users",
            "user_preferences",
            "user_auth_tokens",
            "system_settings",
            "conversations",
            "chat_sessions",
            "conversation_messages",
            "chat_bookmarks",
            "currency_favorites",
            "packing_templates",
            "saved_destinations",
            "clothing_styles",
            "user_style_preferences",
            "api_request_logs",
            "api_usage_tracking",
            "recommendation_history",
            "response_feedback",
            "ui_analytics",
        ]

        for table_name in expected_tables:
            assert table_name in SupabaseConfig.TABLES
            table_config = SupabaseConfig.TABLES[table_name]
            assert isinstance(table_config, SupabaseTableConfig)
            assert table_config.name == table_name

    def test_supabase_config_views_structure(self):
        """Test that VIEWS dictionary contains expected view configs."""
        expected_views = [
            "user_profile_view",
            "user_style_preferences_summary",
            "api_performance_summary",
        ]

        for view_name in expected_views:
            assert view_name in SupabaseConfig.VIEWS
            view_config = SupabaseConfig.VIEWS[view_name]
            assert isinstance(view_config, SupabaseViewConfig)
            assert view_config.name == view_name

    def test_supabase_config_error_messages(self):
        """Test that ERROR_MESSAGES contains expected error types."""
        expected_errors = [
            "connection_failed",
            "invalid_credentials",
            "table_not_found",
            "rate_limited",
            "permission_denied",
            "validation_error",
        ]

        for error_type in expected_errors:
            assert error_type in SupabaseConfig.ERROR_MESSAGES
            assert isinstance(SupabaseConfig.ERROR_MESSAGES[error_type], str)

    def test_get_table_config_existing_table(self):
        """Test get_table_config method returns existing table config."""
        # This tests the missing line 116 in coverage
        weather_config = SupabaseConfig.get_table_config("weather_cache")

        assert isinstance(weather_config, SupabaseTableConfig)
        assert weather_config.name == "weather_cache"
        assert "destination" in weather_config.unique_constraints
        assert "destination" in weather_config.indexes
        assert "expires_at" in weather_config.indexes

    def test_get_table_config_nonexistent_table(self):
        """Test get_table_config method returns default config for nonexistent table."""
        default_config = SupabaseConfig.get_table_config("nonexistent_table")

        assert isinstance(default_config, SupabaseTableConfig)
        assert default_config.name == "nonexistent_table"
        assert default_config.primary_key == "id"
        assert default_config.unique_constraints == []
        assert default_config.indexes == []
        assert default_config.rls_enabled is True

    def test_get_view_config_existing_view(self):
        """Test get_view_config method returns existing view config."""
        user_profile_config = SupabaseConfig.get_view_config("user_profile_view")

        assert isinstance(user_profile_config, SupabaseViewConfig)
        assert user_profile_config.name == "user_profile_view"
        assert user_profile_config.security_invoker is True

    def test_get_view_config_nonexistent_view(self):
        """Test get_view_config method returns default config for nonexistent view."""
        default_config = SupabaseConfig.get_view_config("nonexistent_view")

        assert isinstance(default_config, SupabaseViewConfig)
        assert default_config.name == "nonexistent_view"
        assert default_config.security_invoker is False
        assert default_config.rls_enabled is True

    @patch("app.services.supabase.supabase_config.settings")
    def test_validate_connection_settings_both_present(self, mock_settings):
        """Test validate_connection_settings returns True when both URL and KEY are present."""
        # This tests the missing line 121 in coverage
        mock_settings.SUPABASE_URL = "https://test.supabase.co"
        mock_settings.SUPABASE_KEY = "test_key"

        result = SupabaseConfig.validate_connection_settings()
        assert result is True

    @patch("app.services.supabase.supabase_config.settings")
    def test_validate_connection_settings_missing_url(self, mock_settings):
        """Test validate_connection_settings returns False when URL is missing."""
        mock_settings.SUPABASE_URL = None
        mock_settings.SUPABASE_KEY = "test_key"

        # Need to patch the class attributes directly since they're class variables
        with patch.object(SupabaseConfig, "URL", None):
            with patch.object(SupabaseConfig, "KEY", "test_key"):
                result = SupabaseConfig.validate_connection_settings()
                assert result is False

    @patch("app.services.supabase.supabase_config.settings")
    def test_validate_connection_settings_missing_key(self, mock_settings):
        """Test validate_connection_settings returns False when KEY is missing."""
        mock_settings.SUPABASE_URL = "https://test.supabase.co"
        mock_settings.SUPABASE_KEY = None

        # Need to patch the class attributes directly since they're class variables
        with patch.object(SupabaseConfig, "URL", "https://test.supabase.co"):
            with patch.object(SupabaseConfig, "KEY", None):
                result = SupabaseConfig.validate_connection_settings()
                assert result is False

    @patch("app.services.supabase.supabase_config.settings")
    def test_validate_connection_settings_both_missing(self, mock_settings):
        """Test validate_connection_settings returns False when both URL and KEY are missing."""
        mock_settings.SUPABASE_URL = None
        mock_settings.SUPABASE_KEY = None

        # Need to patch the class attributes directly since they're class variables
        with patch.object(SupabaseConfig, "URL", None):
            with patch.object(SupabaseConfig, "KEY", None):
                result = SupabaseConfig.validate_connection_settings()
                assert result is False

    def test_get_cache_ttl_weather(self):
        """Test get_cache_ttl method returns correct TTL for weather cache."""
        # This tests the missing line 126 in coverage
        ttl = SupabaseConfig.get_cache_ttl("weather")
        assert ttl == SupabaseConfig.WEATHER_CACHE_TTL

    def test_get_cache_ttl_cultural(self):
        """Test get_cache_ttl method returns correct TTL for cultural cache."""
        ttl = SupabaseConfig.get_cache_ttl("cultural")
        assert ttl == SupabaseConfig.CULTURAL_CACHE_TTL

    def test_get_cache_ttl_currency(self):
        """Test get_cache_ttl method returns correct TTL for currency cache."""
        ttl = SupabaseConfig.get_cache_ttl("currency")
        assert ttl == SupabaseConfig.CURRENCY_CACHE_TTL

    def test_get_cache_ttl_unknown_type(self):
        """Test get_cache_ttl method returns default TTL for unknown cache type."""
        ttl = SupabaseConfig.get_cache_ttl("unknown_cache_type")
        assert ttl == SupabaseConfig.DEFAULT_CACHE_TTL

    def test_get_rate_limit_cache(self):
        """Test get_rate_limit method returns correct rate limit for cache operations."""
        # This tests the missing line 131 in coverage
        rate_limit = SupabaseConfig.get_rate_limit("cache")
        assert rate_limit == SupabaseConfig.CACHE_RATE_LIMIT

    def test_get_rate_limit_database(self):
        """Test get_rate_limit method returns correct rate limit for database operations."""
        rate_limit = SupabaseConfig.get_rate_limit("database")
        assert rate_limit == SupabaseConfig.DB_RATE_LIMIT

    def test_get_rate_limit_unknown_type(self):
        """Test get_rate_limit method returns default rate limit for unknown operation type."""
        rate_limit = SupabaseConfig.get_rate_limit("unknown_operation")
        assert rate_limit == SupabaseConfig.DB_RATE_LIMIT


class TestSupabaseConfigExport:
    """Test the exported supabase_config instance."""

    def test_supabase_config_export(self):
        """Test that supabase_config is properly exported and instantiated."""
        # This tests the missing lines 136-140 in coverage
        assert supabase_config is not None
        assert isinstance(supabase_config, SupabaseConfig)

        # Test that it has the expected attributes
        assert hasattr(supabase_config, "URL")
        assert hasattr(supabase_config, "KEY")
        assert hasattr(supabase_config, "TABLES")
        assert hasattr(supabase_config, "ERROR_MESSAGES")
        assert hasattr(supabase_config, "get_table_config")
        assert hasattr(supabase_config, "validate_connection_settings")
        assert hasattr(supabase_config, "get_cache_ttl")
        assert hasattr(supabase_config, "get_rate_limit")
