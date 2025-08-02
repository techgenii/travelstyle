-- =============================================================================
-- TravelStyle AI - Cache Tables
-- =============================================================================
-- This file contains tables for caching external API data
-- =============================================================================

-- =============================================================================
-- CACHING TABLES
-- =============================================================================

-- Cache cultural insights and style data from external APIs
CREATE TABLE public.cultural_insights_cache (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  destination character varying NOT NULL, -- Travel destination
  destination_normalized character varying NOT NULL, -- Normalized destination name for matching
  cultural_data jsonb NOT NULL, -- Cultural insights data
  style_data jsonb DEFAULT '{}'::jsonb, -- Style recommendations data
  api_source character varying DEFAULT 'qloo'::character varying, -- Source API for the data
  expires_at timestamp with time zone NOT NULL, -- When the cache entry expires
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT cultural_insights_cache_pkey PRIMARY KEY (id)
);

-- Cache currency exchange rates
CREATE TABLE public.currency_rates_cache (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  base_currency character varying NOT NULL, -- Base currency for exchange rates
  rates_data jsonb NOT NULL, -- Exchange rates data
  api_source character varying DEFAULT 'exchangerate-api'::character varying, -- Source API for rates
  expires_at timestamp with time zone NOT NULL, -- When the cache entry expires
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT currency_rates_cache_pkey PRIMARY KEY (id),
  CONSTRAINT currency_rates_cache_base_currency_api_source_key UNIQUE (base_currency, api_source)
);

-- Cache weather data for destinations
CREATE TABLE public.weather_cache (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  destination character varying NOT NULL, -- Travel destination
  destination_normalized character varying NOT NULL, -- Normalized destination name for matching
  weather_data jsonb NOT NULL, -- Weather data from external API
  api_source character varying DEFAULT 'openweathermap'::character varying, -- Source API for weather data
  expires_at timestamp with time zone NOT NULL, -- When the cache entry expires
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT weather_cache_pkey PRIMARY KEY (id)
);

-- =============================================================================
-- INDEXES FOR CACHE TABLES
-- =============================================================================

-- Note: Cache table indexes are defined in indexes/03_cache_indexes.sql
-- to maintain separation of concerns and avoid duplication
