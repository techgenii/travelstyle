-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.api_request_logs (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid,
  session_id uuid,
  endpoint character varying NOT NULL,
  method character varying NOT NULL,
  request_payload jsonb DEFAULT '{}'::jsonb,
  response_data jsonb DEFAULT '{}'::jsonb,
  response_status integer,
  response_time_ms integer,
  error_message text,
  api_provider character varying,
  cache_hit boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT api_request_logs_pkey PRIMARY KEY (id),
  CONSTRAINT api_request_logs_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id),
  CONSTRAINT api_request_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.api_usage_tracking (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid,
  session_id uuid,
  api_provider character varying NOT NULL,
  endpoint character varying NOT NULL,
  method character varying DEFAULT 'GET'::character varying,
  request_data jsonb DEFAULT '{}'::jsonb,
  response_status integer,
  response_time_ms integer,
  cost_credits numeric,
  cache_hit boolean DEFAULT false,
  error_details text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT api_usage_tracking_pkey PRIMARY KEY (id),
  CONSTRAINT api_usage_tracking_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT api_usage_tracking_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id)
);
CREATE TABLE public.chat_bookmarks (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  conversation_id uuid NOT NULL,
  message_id character varying NOT NULL,
  bookmark_title character varying,
  bookmark_tags jsonb DEFAULT '[]'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT chat_bookmarks_pkey PRIMARY KEY (id),
  CONSTRAINT chat_bookmarks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT chat_bookmarks_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id)
);
CREATE TABLE public.chat_sessions (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  conversation_id uuid NOT NULL,
  session_context jsonb DEFAULT '{}'::jsonb,
  current_step character varying,
  destination character varying,
  trip_context jsonb DEFAULT '{}'::jsonb,
  recommendations_cache jsonb DEFAULT '{}'::jsonb,
  is_active boolean DEFAULT true,
  expires_at timestamp with time zone DEFAULT (now() + '24:00:00'::interval),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT chat_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT chat_sessions_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id),
  CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.conversation_messages (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  conversation_id uuid NOT NULL,
  message_id character varying NOT NULL,
  role character varying NOT NULL CHECK (role::text = ANY (ARRAY['user'::character varying, 'assistant'::character varying, 'system'::character varying]::text[])),
  content text NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  message_type character varying DEFAULT 'text'::character varying,
  api_data jsonb DEFAULT '{}'::jsonb,
  processing_time_ms integer,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT conversation_messages_pkey PRIMARY KEY (id),
  CONSTRAINT conversation_messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id)
);
CREATE TABLE public.conversations (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  type character varying NOT NULL CHECK (type::text = ANY (ARRAY['wardrobe'::character varying, 'style'::character varying, 'currency'::character varying, 'mixed'::character varying]::text[])),
  title character varying,
  messages jsonb DEFAULT '[]'::jsonb,
  ui_interactions jsonb DEFAULT '{}'::jsonb,
  destination character varying,
  trip_context jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  is_archived boolean DEFAULT false,
  CONSTRAINT conversations_pkey PRIMARY KEY (id),
  CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.cultural_insights_cache (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  destination character varying NOT NULL,
  destination_normalized character varying NOT NULL,
  cultural_data jsonb NOT NULL,
  style_data jsonb DEFAULT '{}'::jsonb,
  api_source character varying DEFAULT 'qloo'::character varying,
  expires_at timestamp with time zone NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT cultural_insights_cache_pkey PRIMARY KEY (id)
);
CREATE TABLE public.currency_favorites (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  from_currency character varying NOT NULL,
  to_currency character varying NOT NULL,
  is_primary boolean DEFAULT false,
  usage_count integer DEFAULT 1,
  last_used timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT currency_favorites_pkey PRIMARY KEY (id),
  CONSTRAINT currency_favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.currency_rates_cache (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  base_currency character varying NOT NULL,
  rates_data jsonb NOT NULL,
  api_source character varying DEFAULT 'exchangerate-api'::character varying,
  expires_at timestamp with time zone NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT currency_rates_cache_pkey PRIMARY KEY (id)
);
CREATE TABLE public.packing_templates (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  template_name character varying NOT NULL,
  packing_method character varying NOT NULL,
  template_data jsonb DEFAULT '{}'::jsonb,
  destination_type character varying,
  climate_type character varying,
  trip_duration_days integer,
  is_public boolean DEFAULT false,
  usage_count integer DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT packing_templates_pkey PRIMARY KEY (id),
  CONSTRAINT packing_templates_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.recommendation_history (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  conversation_id uuid NOT NULL,
  recommendation_type character varying NOT NULL CHECK (recommendation_type::text = ANY (ARRAY['cultural'::character varying, 'weather'::character varying, 'currency'::character varying, 'wardrobe'::character varying, 'style'::character varying]::text[])),
  destination character varying,
  request_data jsonb DEFAULT '{}'::jsonb,
  recommendation_data jsonb NOT NULL,
  user_feedback jsonb DEFAULT '{}'::jsonb,
  accuracy_score numeric,
  was_helpful boolean,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT recommendation_history_pkey PRIMARY KEY (id),
  CONSTRAINT recommendation_history_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id),
  CONSTRAINT recommendation_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.response_feedback (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  conversation_id uuid NOT NULL,
  message_id character varying NOT NULL,
  feedback_type character varying NOT NULL CHECK (feedback_type::text = ANY (ARRAY['positive'::character varying, 'negative'::character varying, 'neutral'::character varying]::text[])),
  feedback_text text,
  ai_response_content text,
  context_data jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT response_feedback_pkey PRIMARY KEY (id),
  CONSTRAINT response_feedback_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id),
  CONSTRAINT response_feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.saved_destinations (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  destination_name character varying NOT NULL,
  destination_data jsonb DEFAULT '{}'::jsonb,
  visit_count integer DEFAULT 1,
  last_used timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT saved_destinations_pkey PRIMARY KEY (id),
  CONSTRAINT saved_destinations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.system_settings (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  setting_key character varying NOT NULL UNIQUE,
  setting_value jsonb NOT NULL,
  description text,
  is_public boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT system_settings_pkey PRIMARY KEY (id)
);
CREATE TABLE public.ui_analytics (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid,
  session_id character varying,
  interaction_type character varying NOT NULL CHECK (interaction_type::text = ANY (ARRAY['quick_reply'::character varying, 'suggested_reply'::character varying, 'manual_input'::character varying, 'welcome_message'::character varying, 'chat_export'::character varying, 'conversation_search'::character varying]::text[])),
  interaction_data jsonb DEFAULT '{}'::jsonb,
  conversation_id uuid,
  page_url character varying,
  user_agent text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT ui_analytics_pkey PRIMARY KEY (id),
  CONSTRAINT ui_analytics_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id),
  CONSTRAINT ui_analytics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.user_auth_tokens (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  token_type character varying NOT NULL CHECK (token_type::text = ANY (ARRAY['access'::character varying, 'refresh'::character varying, 'reset'::character varying]::text[])),
  token_hash character varying NOT NULL,
  expires_at timestamp with time zone NOT NULL,
  is_revoked boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now(),
  last_used_at timestamp with time zone,
  CONSTRAINT user_auth_tokens_pkey PRIMARY KEY (id),
  CONSTRAINT user_auth_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.user_preferences (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL UNIQUE,
  style_preferences jsonb DEFAULT '{}'::jsonb,
  size_info jsonb DEFAULT '{}'::jsonb,
  travel_patterns jsonb DEFAULT '{}'::jsonb,
  quick_reply_preferences jsonb DEFAULT '{}'::jsonb,
  packing_methods jsonb DEFAULT '{}'::jsonb,
  currency_preferences jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_preferences_pkey PRIMARY KEY (id),
  CONSTRAINT user_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.users (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  email character varying NOT NULL UNIQUE,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  preferences jsonb DEFAULT '{}'::jsonb,
  ui_preferences jsonb DEFAULT '{}'::jsonb,
  last_login timestamp with time zone,
  profile_completed boolean DEFAULT false,
  first_name character varying,
  last_name character varying,
  CONSTRAINT users_pkey PRIMARY KEY (id)
);
CREATE TABLE public.weather_cache (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  destination character varying NOT NULL,
  destination_normalized character varying NOT NULL,
  weather_data jsonb NOT NULL,
  forecast_data jsonb DEFAULT '{}'::jsonb,
  api_source character varying DEFAULT 'openweathermap'::character varying,
  expires_at timestamp with time zone NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT weather_cache_pkey PRIMARY KEY (id)
);