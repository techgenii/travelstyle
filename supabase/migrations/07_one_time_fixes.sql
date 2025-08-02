-- =============================================================================
-- TravelStyle AI - One-Time Fixes
-- =============================================================================
-- This file contains one-time fixes for existing databases
-- Run this file once after the main schema is applied
-- =============================================================================

-- =============================================================================
-- CURRENCY CACHE UNIQUE CONSTRAINT FIX
-- =============================================================================

-- First, remove any existing duplicate entries
-- Fix for the MIN(uuid) error
DELETE FROM currency_rates_cache
WHERE id NOT IN (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY base_currency, api_source ORDER BY id) as rn
        FROM currency_rates_cache
    ) t
    WHERE t.rn = 1
);

-- Add the unique constraint
ALTER TABLE currency_rates_cache
ADD CONSTRAINT currency_rates_cache_base_currency_api_source_key
UNIQUE (base_currency, api_source);

-- =============================================================================
-- CONVERSATION MESSAGES SCHEMA FIX
-- =============================================================================

-- Add message_id column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'conversation_messages'
        AND column_name = 'message_id'
    ) THEN
        ALTER TABLE conversation_messages ADD COLUMN message_id character varying;
    END IF;
END $$;

-- Add role column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'conversation_messages'
        AND column_name = 'role'
    ) THEN
        ALTER TABLE conversation_messages ADD COLUMN role character varying;
    END IF;
END $$;

-- Add content column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'conversation_messages'
        AND column_name = 'content'
    ) THEN
        ALTER TABLE conversation_messages ADD COLUMN content text;
    END IF;
END $$;

-- Remove old columns if they exist (user_message, ai_response)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'conversation_messages'
        AND column_name = 'user_message'
    ) THEN
        ALTER TABLE conversation_messages DROP COLUMN user_message;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'conversation_messages'
        AND column_name = 'ai_response'
    ) THEN
        ALTER TABLE conversation_messages DROP COLUMN ai_response;
    END IF;
END $$;

-- Add NOT NULL constraints if they don't exist
ALTER TABLE conversation_messages ALTER COLUMN message_id SET NOT NULL;
ALTER TABLE conversation_messages ALTER COLUMN role SET NOT NULL;
ALTER TABLE conversation_messages ALTER COLUMN content SET NOT NULL;

-- Add check constraint for role values
ALTER TABLE conversation_messages DROP CONSTRAINT IF EXISTS conversation_messages_role_check;
ALTER TABLE conversation_messages ADD CONSTRAINT conversation_messages_role_check
    CHECK (role::text = ANY (ARRAY['user'::character varying, 'assistant'::character varying, 'system'::character varying]::text[]));

-- =============================================================================
-- CHAT SESSIONS SCHEMA FIX
-- =============================================================================

-- Add expires_at column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'chat_sessions'
        AND column_name = 'expires_at'
    ) THEN
        ALTER TABLE chat_sessions ADD COLUMN expires_at timestamp with time zone;
    END IF;
END $$;

-- Note: Functions cleanup_expired_cache() and get_or_create_chat_session()
-- are already defined in the modular function files:
-- - functions/03_cache_functions.sql (cleanup_expired_cache)
-- - functions/04_chat_functions.sql (get_or_create_chat_session)
-- No duplication needed here.
