-- =============================================================================
-- TravelStyle AI - Analytics and Tracking Tables
-- =============================================================================
-- This file contains tables for analytics, tracking, and monitoring
-- =============================================================================

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

-- Track recommendation quality and usage
CREATE TABLE public.recommendation_history (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who received the recommendation
  conversation_id uuid NOT NULL, -- Conversation where recommendation was made
  message_id character varying NOT NULL, -- Message ID of the recommendation
  recommendation_type character varying NOT NULL, -- Type of recommendation (style, packing, etc.)
  recommendation_data jsonb NOT NULL, -- The actual recommendation data
  user_feedback integer, -- User rating (1-5) if provided
  was_used boolean DEFAULT false, -- Whether user acted on the recommendation
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT recommendation_history_pkey PRIMARY KEY (id),
  CONSTRAINT recommendation_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT recommendation_history_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id)
);

-- Track user feedback on AI responses
CREATE TABLE public.response_feedback (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User who provided feedback
  conversation_id uuid NOT NULL, -- Conversation containing the response
  message_id character varying NOT NULL, -- Message ID of the AI response
  feedback_type character varying NOT NULL CHECK (feedback_type::text = ANY (ARRAY['helpful'::character varying, 'not_helpful'::character varying, 'inaccurate'::character varying, 'offensive'::character varying]::text[])), -- Type of feedback
  feedback_text text, -- Additional feedback text
  ai_response_content text, -- Content of the AI response for context
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT response_feedback_pkey PRIMARY KEY (id),
  CONSTRAINT response_feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT response_feedback_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id)
);

-- Track UI interactions and user behavior
CREATE TABLE public.ui_analytics (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid, -- User performing the action (nullable for anonymous)
  session_id uuid, -- Session identifier
  event_type character varying NOT NULL, -- Type of UI event
  event_data jsonb DEFAULT '{}'::jsonb, -- Event-specific data
  page_url character varying, -- Page where event occurred
  user_agent text, -- Client user agent
  ip_address character varying, -- Client IP address
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT ui_analytics_pkey PRIMARY KEY (id)
);

-- =============================================================================
-- INDEXES FOR ANALYTICS TABLES
-- =============================================================================

-- Indexes for api_request_logs table
CREATE INDEX idx_api_request_logs_user_id ON public.api_request_logs(user_id);
CREATE INDEX idx_api_request_logs_session_id ON public.api_request_logs(session_id);
CREATE INDEX idx_api_request_logs_endpoint ON public.api_request_logs(endpoint);
CREATE INDEX idx_api_request_logs_created_at ON public.api_request_logs(created_at);
CREATE INDEX idx_api_request_logs_response_status ON public.api_request_logs(response_status);

-- Indexes for api_usage_tracking table
CREATE INDEX idx_api_usage_tracking_user_id ON public.api_usage_tracking(user_id);
CREATE INDEX idx_api_usage_tracking_api_name ON public.api_usage_tracking(api_name);
CREATE INDEX idx_api_usage_tracking_date ON public.api_usage_tracking(date);
CREATE INDEX idx_api_usage_tracking_endpoint ON public.api_usage_tracking(endpoint);

-- Indexes for recommendation_history table
CREATE INDEX idx_recommendation_history_user_id ON public.recommendation_history(user_id);
CREATE INDEX idx_recommendation_history_conversation_id ON public.recommendation_history(conversation_id);
CREATE INDEX idx_recommendation_history_recommendation_type ON public.recommendation_history(recommendation_type);
CREATE INDEX idx_recommendation_history_was_used ON public.recommendation_history(was_used);
CREATE INDEX idx_recommendation_history_created_at ON public.recommendation_history(created_at);

-- Indexes for response_feedback table
CREATE INDEX idx_response_feedback_user_id ON public.response_feedback(user_id);
CREATE INDEX idx_response_feedback_conversation_id ON public.response_feedback(conversation_id);
CREATE INDEX idx_response_feedback_feedback_type ON public.response_feedback(feedback_type);
CREATE INDEX idx_response_feedback_created_at ON public.response_feedback(created_at);

-- Indexes for ui_analytics table
CREATE INDEX idx_ui_analytics_user_id ON public.ui_analytics(user_id);
CREATE INDEX idx_ui_analytics_session_id ON public.ui_analytics(session_id);
CREATE INDEX idx_ui_analytics_event_type ON public.ui_analytics(event_type);
CREATE INDEX idx_ui_analytics_created_at ON public.ui_analytics(created_at);
