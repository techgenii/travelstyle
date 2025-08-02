-- =============================================================================
-- TravelStyle AI - User Data and Preference Tables
-- =============================================================================
-- This file contains tables for user-specific data and preferences
-- =============================================================================

-- =============================================================================
-- USER PREFERENCE AND FAVORITE TABLES
-- =============================================================================

-- Store user's favorite currency pairs
CREATE TABLE public.currency_favorites (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who favorited the currency pair
  from_currency character varying NOT NULL, -- Source currency
  to_currency character varying NOT NULL, -- Target currency
  is_primary boolean DEFAULT false, -- Whether this is the user's primary currency pair
  usage_count integer DEFAULT 1, -- Number of times this pair has been used
  last_used timestamp with time zone DEFAULT now(), -- Last time this pair was used
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT currency_favorites_pkey PRIMARY KEY (id),
  CONSTRAINT currency_favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- Store user's packing templates
CREATE TABLE public.packing_templates (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who created the template
  template_name character varying NOT NULL, -- Name of the packing template
  packing_method character varying NOT NULL, -- Packing method (e.g., 'rolling', 'folding')
  template_data jsonb DEFAULT '{}'::jsonb, -- Template-specific packing data
  destination_type character varying, -- Type of destination (beach, city, etc.)
  climate_type character varying, -- Climate type (tropical, cold, etc.)
  trip_duration_days integer, -- Duration the template is designed for
  is_public boolean DEFAULT false, -- Whether template is publicly shareable
  usage_count integer DEFAULT 0, -- Number of times template has been used
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT packing_templates_pkey PRIMARY KEY (id),
  CONSTRAINT packing_templates_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- Store user's saved destinations
CREATE TABLE public.saved_destinations (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who saved the destination
  destination_name character varying NOT NULL, -- Name of the destination
  destination_data jsonb DEFAULT '{}'::jsonb, -- Additional destination data
  is_favorite boolean DEFAULT false, -- Whether this is a favorite destination
  visit_count integer DEFAULT 0, -- Number of times user has visited
  last_visited timestamp with time zone, -- Last time user visited
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT saved_destinations_pkey PRIMARY KEY (id),
  CONSTRAINT saved_destinations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- =============================================================================
-- INDEXES FOR USER DATA TABLES
-- =============================================================================

-- Indexes for currency_favorites table
CREATE INDEX idx_currency_favorites_user_id ON public.currency_favorites(user_id);
CREATE INDEX idx_currency_favorites_from_currency ON public.currency_favorites(from_currency);
CREATE INDEX idx_currency_favorites_to_currency ON public.currency_favorites(to_currency);
CREATE INDEX idx_currency_favorites_is_primary ON public.currency_favorites(is_primary);

-- Indexes for packing_templates table
CREATE INDEX idx_packing_templates_user_id ON public.packing_templates(user_id);
CREATE INDEX idx_packing_templates_packing_method ON public.packing_templates(packing_method);
CREATE INDEX idx_packing_templates_destination_type ON public.packing_templates(destination_type);
CREATE INDEX idx_packing_templates_climate_type ON public.packing_templates(climate_type);
CREATE INDEX idx_packing_templates_is_public ON public.packing_templates(is_public);

-- Indexes for saved_destinations table
CREATE INDEX idx_saved_destinations_user_id ON public.saved_destinations(user_id);
CREATE INDEX idx_saved_destinations_destination_name ON public.saved_destinations(destination_name);
-- Note: idx_saved_destinations_is_favorite is also defined in 08_schema_enhancements.sql
-- but with additional columns, so keeping both for now
