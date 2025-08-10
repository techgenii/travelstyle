-- =============================================================================
-- TravelStyle AI - Chat and Conversation Tables
-- =============================================================================
-- This file contains tables for chat functionality and conversations
-- =============================================================================

-- =============================================================================
-- CHAT AND CONVERSATION TABLES
-- =============================================================================

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
  CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
);

-- Track individual chat sessions within conversations
CREATE TABLE public.chat_sessions (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL, -- User participating in the session
  conversation_id uuid NOT NULL, -- Parent conversation
  destination character varying, -- Travel destination for this session
  session_data jsonb DEFAULT '{}'::jsonb, -- Session-specific metadata
  is_active boolean DEFAULT true, -- Whether session is currently active
  expires_at timestamp with time zone, -- When session expires
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT chat_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT chat_sessions_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id),
  CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
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
  CONSTRAINT chat_bookmarks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
);

-- =============================================================================
-- INDEXES FOR CHAT TABLES
-- =============================================================================

-- Note: Chat table indexes are defined in indexes/02_chat_indexes.sql
-- to maintain separation of concerns and avoid duplication
