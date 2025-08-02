-- =============================================================================
-- TravelStyle AI - Cache Management Functions
-- =============================================================================
-- This file contains functions for managing cache operations
-- =============================================================================

-- =============================================================================
-- CACHE MANAGEMENT FUNCTIONS
-- =============================================================================

-- Function to clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM weather_cache WHERE expires_at < NOW();
    DELETE FROM currency_rates_cache WHERE expires_at < NOW();
    DELETE FROM cultural_insights_cache WHERE expires_at < NOW();
    DELETE FROM chat_sessions WHERE expires_at < NOW() AND is_active = false;
    DELETE FROM user_auth_tokens WHERE expires_at < NOW() OR is_revoked = true;
END;
$$ LANGUAGE plpgsql;

-- Function to normalize destination names for consistent caching
CREATE OR REPLACE FUNCTION normalize_destination(destination_name VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
    RETURN LOWER(TRIM(REGEXP_REPLACE(destination_name, '[^a-zA-Z0-9\s]', '', 'g')));
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- CACHE UTILITY FUNCTIONS
-- =============================================================================

-- Function to check if cache entry is expired
CREATE OR REPLACE FUNCTION is_cache_expired(expires_at TIMESTAMP WITH TIME ZONE)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to get cache entry age in hours
CREATE OR REPLACE FUNCTION get_cache_age_hours(created_at TIMESTAMP WITH TIME ZONE)
RETURNS NUMERIC AS $$
BEGIN
    RETURN EXTRACT(EPOCH FROM (NOW() - created_at)) / 3600;
END;
$$ LANGUAGE plpgsql;

-- Function to refresh cache entry
CREATE OR REPLACE FUNCTION refresh_cache_entry(
    table_name TEXT,
    entry_id UUID,
    new_expires_at TIMESTAMP WITH TIME ZONE
)
RETURNS BOOLEAN AS $$
BEGIN
    EXECUTE format('UPDATE %I SET expires_at = $1, updated_at = NOW() WHERE id = $2', table_name)
    USING new_expires_at, entry_id;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;
