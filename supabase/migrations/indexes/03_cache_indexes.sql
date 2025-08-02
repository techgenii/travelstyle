-- =============================================================================
-- TravelStyle AI - Cache Table Indexes
-- =============================================================================
-- This file contains indexes for cache tables
-- =============================================================================

-- =============================================================================
-- CACHE TABLE INDEXES
-- =============================================================================

-- Weather cache indexes
CREATE INDEX idx_weather_cache_destination ON weather_cache(destination_normalized);
CREATE INDEX idx_weather_cache_expires_at ON weather_cache(expires_at);

-- Currency rates cache indexes
CREATE INDEX idx_currency_rates_cache_base ON currency_rates_cache(base_currency);
CREATE INDEX idx_currency_rates_cache_expires_at ON currency_rates_cache(expires_at);

-- Cultural insights cache indexes
CREATE INDEX idx_cultural_insights_cache_destination ON cultural_insights_cache(destination_normalized);
CREATE INDEX idx_cultural_insights_cache_expires_at ON cultural_insights_cache(expires_at);
