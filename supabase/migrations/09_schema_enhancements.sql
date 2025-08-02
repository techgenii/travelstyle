-- =============================================================================
-- TravelStyle AI - Schema Enhancements
-- =============================================================================
-- This file contains schema enhancements and fixes
-- =============================================================================

-- =============================================================================
-- WEATHER CACHE ENHANCEMENTS
-- =============================================================================

-- First, clean up duplicate weather cache entries by keeping only the most recent one
-- for each destination and API source combination
DELETE FROM public.weather_cache
WHERE id NOT IN (
    SELECT DISTINCT ON (destination, api_source) id
    FROM public.weather_cache
    ORDER BY destination, api_source, created_at DESC
);

-- Then clean up duplicate cultural insights cache entries
DELETE FROM public.cultural_insights_cache
WHERE id NOT IN (
    SELECT DISTINCT ON (destination, api_source) id
    FROM public.cultural_insights_cache
    ORDER BY destination, api_source, created_at DESC
);

-- After cleaning up duplicates, add the unique constraints
ALTER TABLE public.weather_cache
ADD CONSTRAINT weather_cache_destination_api_source_key
UNIQUE (destination, api_source);

ALTER TABLE public.cultural_insights_cache
ADD CONSTRAINT cultural_insights_cache_destination_api_source_key
UNIQUE (destination, api_source);
