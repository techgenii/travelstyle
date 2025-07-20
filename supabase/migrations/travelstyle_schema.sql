-- =============================================================================
-- TravelStyle AI Database Schema
-- =============================================================================
-- This file contains the complete database schema for the TravelStyle AI application.
-- It includes tables for user management, chat functionality, caching, and analytics.
-- =============================================================================

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- API AND USAGE TRACKING TABLES
-- =============================================================================

-- Track API requests for monitoring and rate limiting
CREATE TABLE public.api_request_logs (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid, -- User making the request (nullable for anonymous requests)
  session_id uuid, -- Chat session associated with the request
  endpoint character varying NOT NULL, -- API endpoint being called
  method character varying NOT NULL, -- HTTP method (GET, POST, etc.)
  request_data jsonb DEFAULT '{}'::jsonb, -- Request payload
  response_status integer, -- HTTP response status code
  response_time_ms integer, -- Request processing time in milliseconds
  error_message text, -- Error details if request failed
  ip_address character varying, -- Client IP address
  user_agent text, -- Client user agent string
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT api_request_logs_pkey PRIMARY KEY (id),
  CONSTRAINT api_request_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT api_request_logs_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id)
);

-- Track API usage for billing and analytics
CREATE TABLE public.api_usage_tracking (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User consuming the API
  api_name character varying NOT NULL, -- Name of the external API (e.g., 'openai', 'qloo')
  endpoint character varying NOT NULL, -- Specific endpoint being called
  request_count integer DEFAULT 1, -- Number of requests made
  tokens_used integer DEFAULT 0, -- Token usage for AI APIs
  cost_usd numeric(10,4) DEFAULT 0, -- Cost in USD
  date date NOT NULL, -- Date of usage for aggregation
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT api_usage_tracking_pkey PRIMARY KEY (id),
  CONSTRAINT api_usage_tracking_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- =============================================================================
-- CHAT AND CONVERSATION TABLES
-- =============================================================================

-- Store bookmarks for important chat messages
CREATE TABLE public.chat_bookmarks (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who created the bookmark
  conversation_id uuid NOT NULL, -- Conversation containing the message
  message_id character varying NOT NULL, -- ID of the bookmarked message
  title character varying, -- User-defined title for the bookmark
  notes text, -- User notes about the bookmark
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT chat_bookmarks_pkey PRIMARY KEY (id),
  CONSTRAINT chat_bookmarks_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id),
  CONSTRAINT chat_bookmarks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- Track individual chat sessions within conversations
CREATE TABLE public.chat_sessions (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User participating in the session
  conversation_id uuid NOT NULL, -- Parent conversation
  destination character varying, -- Travel destination for this session
  session_data jsonb DEFAULT '{}'::jsonb, -- Session-specific metadata
  is_active boolean DEFAULT true, -- Whether session is currently active
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT chat_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT chat_sessions_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id),
  CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- Store individual messages within conversations
CREATE TABLE public.conversation_messages (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  conversation_id uuid NOT NULL, -- Parent conversation
  message_id character varying NOT NULL, -- Unique message identifier
  role character varying NOT NULL CHECK (role::text = ANY (ARRAY['user'::character varying, 'assistant'::character varying, 'system'::character varying]::text[])), -- Message sender role
  content text NOT NULL, -- Message content
  metadata jsonb DEFAULT '{}'::jsonb, -- Additional message metadata
  message_type character varying DEFAULT 'text'::character varying, -- Type of message (text, image, etc.)
  api_data jsonb DEFAULT '{}'::jsonb, -- Data from external APIs used in response
  processing_time_ms integer, -- Time taken to process the message
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT conversation_messages_pkey PRIMARY KEY (id),
  CONSTRAINT conversation_messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id)
);

-- Main conversations table
CREATE TABLE public.conversations (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who owns the conversation
  type character varying NOT NULL CHECK (type::text = ANY (ARRAY['wardrobe'::character varying, 'style'::character varying, 'currency'::character varying, 'mixed'::character varying]::text[])), -- Conversation type
  title character varying, -- User-defined or auto-generated title
  messages jsonb DEFAULT '[]'::jsonb, -- JSON array of message summaries
  ui_interactions jsonb DEFAULT '{}'::jsonb, -- UI interaction tracking data
  destination character varying, -- Primary travel destination
  trip_context jsonb DEFAULT '{}'::jsonb, -- Trip-specific context (dates, purpose, etc.)
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  is_archived boolean DEFAULT false, -- Whether conversation is archived
  CONSTRAINT conversations_pkey PRIMARY KEY (id),
  CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

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
  CONSTRAINT currency_rates_cache_pkey PRIMARY KEY (id)
);

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

-- =============================================================================
-- RECOMMENDATION AND FEEDBACK TABLES
-- =============================================================================

-- Track recommendation history for analytics and improvement
CREATE TABLE public.recommendation_history (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who received the recommendation
  conversation_id uuid NOT NULL, -- Conversation where recommendation was made
  recommendation_type character varying NOT NULL CHECK (recommendation_type::text = ANY (ARRAY['cultural'::character varying, 'weather'::character varying, 'currency'::character varying, 'wardrobe'::character varying, 'style'::character varying]::text[])), -- Type of recommendation
  destination character varying, -- Travel destination for the recommendation
  request_data jsonb DEFAULT '{}'::jsonb, -- Original request data
  recommendation_data jsonb NOT NULL, -- The actual recommendation data
  user_feedback jsonb DEFAULT '{}'::jsonb, -- User feedback on the recommendation
  accuracy_score numeric, -- AI-generated accuracy score
  was_helpful boolean, -- Whether user found the recommendation helpful
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT recommendation_history_pkey PRIMARY KEY (id),
  CONSTRAINT recommendation_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT recommendation_history_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id)
);

-- Store user feedback on AI responses
CREATE TABLE public.response_feedback (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User providing feedback
  conversation_id uuid NOT NULL, -- Conversation containing the response
  message_id character varying NOT NULL, -- ID of the AI response message
  feedback_type character varying NOT NULL CHECK (feedback_type::text = ANY (ARRAY['positive'::character varying, 'negative'::character varying, 'neutral'::character varying]::text[])), -- Type of feedback
  feedback_text text, -- Detailed feedback text
  ai_response_content text, -- Content of the AI response being rated
  context_data jsonb DEFAULT '{}'::jsonb, -- Context when feedback was given
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT response_feedback_pkey PRIMARY KEY (id),
  CONSTRAINT response_feedback_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id),
  CONSTRAINT response_feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- =============================================================================
-- USER DATA TABLES
-- =============================================================================

-- Store user's saved destinations
CREATE TABLE public.saved_destinations (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who saved the destination
  destination_name character varying NOT NULL, -- Name of the destination
  destination_data jsonb DEFAULT '{}'::jsonb, -- Additional destination data
  visit_count integer DEFAULT 1, -- Number of times user has referenced this destination
  last_used timestamp with time zone DEFAULT now(), -- Last time destination was used
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT saved_destinations_pkey PRIMARY KEY (id),
  CONSTRAINT saved_destinations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- System-wide settings and configuration
CREATE TABLE public.system_settings (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  setting_key character varying NOT NULL UNIQUE, -- Setting identifier
  setting_value jsonb NOT NULL, -- Setting value (JSON for flexibility)
  description text, -- Human-readable description of the setting
  is_public boolean DEFAULT false, -- Whether setting is publicly accessible
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT system_settings_pkey PRIMARY KEY (id)
);

-- =============================================================================
-- ANALYTICS TABLES
-- =============================================================================

-- Track UI interactions for user experience analytics
CREATE TABLE public.ui_analytics (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid, -- User performing the interaction (nullable for anonymous)
  session_id character varying, -- Session identifier
  interaction_type character varying NOT NULL CHECK (interaction_type::text = ANY (ARRAY['quick_reply'::character varying, 'suggested_reply'::character varying, 'manual_input'::character varying, 'welcome_message'::character varying, 'chat_export'::character varying, 'conversation_search'::character varying]::text[])), -- Type of UI interaction
  interaction_data jsonb DEFAULT '{}'::jsonb, -- Interaction-specific data
  conversation_id uuid, -- Associated conversation
  page_url character varying, -- Page where interaction occurred
  user_agent text, -- Client user agent
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT ui_analytics_pkey PRIMARY KEY (id),
  CONSTRAINT ui_analytics_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id),
  CONSTRAINT ui_analytics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- =============================================================================
-- AUTHENTICATION AND SECURITY TABLES
-- =============================================================================

-- Store authentication tokens for session management
CREATE TABLE public.user_auth_tokens (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who owns the token
  token_type character varying NOT NULL CHECK (token_type::text = ANY (ARRAY['access'::character varying, 'refresh'::character varying, 'reset'::character varying]::text[])), -- Type of token
  token_hash character varying NOT NULL, -- Hashed token value
  expires_at timestamp with time zone NOT NULL, -- Token expiration time
  is_revoked boolean DEFAULT false, -- Whether token has been revoked
  created_at timestamp with time zone DEFAULT now(),
  last_used_at timestamp with time zone, -- Last time token was used
  CONSTRAINT user_auth_tokens_pkey PRIMARY KEY (id),
  CONSTRAINT user_auth_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- =============================================================================
-- CORE USER TABLES
-- =============================================================================

-- Store user preferences for travel and style
CREATE TABLE public.user_preferences (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL UNIQUE, -- One-to-one relationship with users
  style_preferences jsonb DEFAULT '{}'::jsonb, -- User's style preferences
  size_info jsonb DEFAULT '{}'::jsonb, -- User's size information
  travel_patterns jsonb DEFAULT '{}'::jsonb, -- User's travel patterns and habits
  quick_reply_preferences jsonb DEFAULT '{}'::jsonb, -- User's quick reply preferences
  packing_methods jsonb DEFAULT '{}'::jsonb, -- User's preferred packing methods
  currency_preferences jsonb DEFAULT '{}'::jsonb, -- User's currency preferences
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_preferences_pkey PRIMARY KEY (id),
  CONSTRAINT user_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- Main users table
CREATE TABLE public.users (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  email character varying NOT NULL UNIQUE, -- User's email address (unique)
  created_at timestamp with time zone DEFAULT now(), -- Account creation time
  updated_at timestamp with time zone DEFAULT now(), -- Last update time
  preferences jsonb DEFAULT '{}'::jsonb, -- General user preferences
  ui_preferences jsonb DEFAULT '{}'::jsonb, -- UI-specific preferences
  last_login timestamp with time zone, -- Last login time
  profile_completed boolean DEFAULT false, -- Whether user has completed their profile
  first_name character varying, -- User's first name
  last_name character varying, -- User's last name
  CONSTRAINT users_pkey PRIMARY KEY (id)
);

-- =============================================================================
-- WEATHER CACHING
-- =============================================================================

-- Cache weather data from external APIs
CREATE TABLE public.weather_cache (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  destination character varying NOT NULL, -- Travel destination
  destination_normalized character varying NOT NULL, -- Normalized destination name for matching
  weather_data jsonb NOT NULL, -- Current weather data
  forecast_data jsonb DEFAULT '{}'::jsonb, -- Weather forecast data
  api_source character varying DEFAULT 'openweathermap'::character varying, -- Source API for weather data
  expires_at timestamp with time zone NOT NULL, -- When the cache entry expires
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT weather_cache_pkey PRIMARY KEY (id)
);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Create a view that joins users and user_preferences tables
-- This view provides a unified interface for accessing user profile data
-- and respects Row Level Security (RLS) policies
--
-- Purpose: This view consolidates user profile information from multiple tables
-- into a single, easy-to-query interface for the application's user profile endpoints.
-- It combines basic user information with detailed preferences for travel and style.
CREATE VIEW public.user_profile_view WITH (security_invoker=on) AS
SELECT
    -- Basic user identification and authentication
    u.id,                    -- Unique user identifier (UUID)
    u.email,                 -- User's email address (unique, used for login)

    -- Personal information
    u.first_name,            -- User's first name (optional, for personalization)
    u.last_name,             -- User's last name (optional, for personalization)
    u.profile_completed,     -- Boolean flag indicating if user has completed their profile setup
    u.profile_picture_url,   -- URL to user's profile picture/avatar (optional)

    -- Style and fashion preferences (from user_preferences table)
    p.style_preferences,     -- JSON object containing user's style preferences (colors, patterns, brands, etc.)
    p.size_info,             -- JSON object with user's clothing sizes and measurements

    -- Travel behavior and preferences
    p.travel_patterns,       -- JSON object describing user's travel habits (frequency, destinations, trip types)
    p.quick_reply_preferences, -- JSON object with user's preferred quick reply settings for chat

    -- Packing and organization preferences
    p.packing_methods,       -- JSON object with user's preferred packing techniques and organization methods
    p.currency_preferences,  -- JSON object containing user's currency preferences (base currency, conversion settings)

    -- Timestamps and activity tracking
    u.created_at,            -- When the user account was created
    u.updated_at,            -- When the user profile was last modified
    u.last_login             -- When the user last logged into the application
FROM
    public.users u
LEFT JOIN
    public.user_preferences p ON u.id = p.user_id;

-- Enhanced user activity view with API usage
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT
    u.id,
    u.email,
    u.created_at as user_created_at,
    u.last_login,
    u.profile_completed,
    COUNT(DISTINCT c.id) as total_conversations,
    COUNT(DISTINCT rf.id) as total_feedback_given,
    COUNT(DISTINCT cb.id) as total_bookmarks,
    COUNT(DISTINCT sd.id) as total_saved_destinations,
    COUNT(DISTINCT cf.id) as total_currency_favorites,
    COUNT(DISTINCT pt.id) as total_packing_templates,
    COUNT(DISTINCT cs.id) as total_active_sessions,
    COUNT(DISTINCT arl.id) as total_api_requests,
    COUNT(DISTINCT rh.id) as total_recommendations,
    MAX(c.created_at) as last_conversation_date,
    MAX(arl.created_at) as last_api_request_date
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN response_feedback rf ON u.id = rf.user_id
LEFT JOIN chat_bookmarks cb ON u.id = cb.user_id
LEFT JOIN saved_destinations sd ON u.id = sd.user_id
LEFT JOIN currency_favorites cf ON u.id = cf.user_id
LEFT JOIN packing_templates pt ON u.id = pt.user_id
LEFT JOIN chat_sessions cs ON u.id = cs.user_id AND cs.is_active = true
LEFT JOIN api_request_logs arl ON u.id = arl.user_id
LEFT JOIN recommendation_history rh ON u.id = rh.user_id
GROUP BY u.id, u.email, u.created_at, u.last_login, u.profile_completed;

-- API performance view
CREATE VIEW api_performance_summary AS
SELECT
    api_provider,
    endpoint,
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE cache_hit = true) as cache_hits,
    COUNT(*) FILTER (WHERE response_status >= 200 AND response_status < 300) as successful_requests,
    COUNT(*) FILTER (WHERE response_status >= 400) as failed_requests,
    AVG(response_time_ms) as avg_response_time_ms,
    MAX(response_time_ms) as max_response_time_ms,
    SUM(cost_credits) as total_cost_credits
FROM api_request_logs
GROUP BY api_provider, endpoint, DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;
