-- =============================================================================
-- TravelStyle AI - Core Tables
-- =============================================================================
-- This file contains the core user and system tables
-- =============================================================================

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- CORE USER AND SYSTEM TABLES
-- =============================================================================

-- Main users table
CREATE TABLE public.users (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  email character varying NOT NULL UNIQUE, -- User's email address
  first_name character varying, -- User's first name
  last_name character varying, -- User's last name
  profile_completed boolean DEFAULT false, -- Whether user has completed profile setup
  profile_picture_url text, -- URL to user's profile picture
  default_location character varying, -- User's default travel location
  max_bookmarks integer DEFAULT 50, -- Maximum number of bookmarks user can have
  max_conversations integer DEFAULT 100, -- Maximum number of conversations user can have
  subscription_tier character varying DEFAULT 'free'::character varying CHECK (subscription_tier::text = ANY (ARRAY['free'::character varying, 'premium'::character varying, 'enterprise'::character varying]::text[])), -- User's subscription tier
  subscription_expires_at timestamp with time zone, -- When subscription expires
  is_premium boolean DEFAULT false, -- Whether user has premium features
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT users_pkey PRIMARY KEY (id)
);

-- User preferences and settings
CREATE TABLE public.user_preferences (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who owns these preferences
  style_preferences jsonb DEFAULT '{}'::jsonb, -- Style and fashion preferences
  size_info jsonb DEFAULT '{}'::jsonb, -- Clothing size information
  travel_patterns jsonb DEFAULT '{}'::jsonb, -- Travel behavior patterns
  quick_reply_preferences jsonb DEFAULT '{"enabled": true}'::jsonb, -- Quick reply settings
  packing_methods jsonb DEFAULT '{}'::jsonb, -- Preferred packing methods
  currency_preferences jsonb DEFAULT '{}'::jsonb, -- Currency conversion preferences
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_preferences_pkey PRIMARY KEY (id),
  CONSTRAINT user_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT user_preferences_user_id_key UNIQUE (user_id)
);

-- User authentication tokens
CREATE TABLE public.user_auth_tokens (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who owns this token
  token_hash character varying NOT NULL, -- Hashed token value
  token_type character varying NOT NULL CHECK (token_type::text = ANY (ARRAY['access'::character varying, 'refresh'::character varying, 'reset'::character varying]::text[])), -- Type of token
  expires_at timestamp with time zone NOT NULL, -- When token expires
  is_revoked boolean DEFAULT false, -- Whether token has been revoked
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_auth_tokens_pkey PRIMARY KEY (id),
  CONSTRAINT user_auth_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- System settings and configuration
CREATE TABLE public.system_settings (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  setting_key character varying NOT NULL UNIQUE, -- Setting identifier
  setting_value jsonb NOT NULL, -- Setting value (JSON for complex settings)
  description text, -- Human-readable description of the setting
  is_public boolean DEFAULT false, -- Whether setting is publicly readable
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT system_settings_pkey PRIMARY KEY (id)
);

-- =============================================================================
-- INDEXES FOR CORE TABLES
-- =============================================================================

-- Note: Core table indexes are defined in indexes/01_core_indexes.sql
-- to maintain separation of concerns and avoid duplication
