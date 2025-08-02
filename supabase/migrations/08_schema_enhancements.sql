-- =============================================================================
-- TravelStyle AI - Schema Enhancements for Existing Database
-- =============================================================================
-- This file adds missing features to your existing comprehensive schema
-- Run this after your original schema is in place
-- =============================================================================

-- =============================================================================
-- ADD MISSING COLUMNS TO EXISTING TABLES
-- =============================================================================

-- Note: All enhanced user columns (first_name, last_name, profile_picture_url,
-- default_location, max_bookmarks, max_conversations, subscription_tier,
-- subscription_expires_at, is_premium) are already defined in 01_core_tables.sql
-- No duplication needed here.

-- Create the update_updated_at_column function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- ADD MISSING COLUMNS TO EXISTING TABLES
-- =============================================================================

-- Note: All enhanced user columns (first_name, last_name, profile_picture_url,
-- default_location, max_bookmarks, max_conversations, subscription_tier,
-- subscription_expires_at, is_premium) are already defined in 01_core_tables.sql
-- No duplication needed here.

-- First check if saved_destinations table exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'saved_destinations'
    ) THEN
        -- Add missing columns to saved_destinations
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'saved_destinations'
            AND column_name = 'is_favorite'
        ) THEN
            ALTER TABLE saved_destinations ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'saved_destinations'
            AND column_name = 'last_visited'
        ) THEN
            ALTER TABLE saved_destinations ADD COLUMN last_visited TIMESTAMP WITH TIME ZONE;
        END IF;
    ELSE
        RAISE NOTICE 'Table saved_destinations does not exist. Skipping column additions.';
    END IF;
END $$;

-- Add missing columns to chat_sessions
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'chat_sessions'
        AND column_name = 'session_data'
    ) THEN
        ALTER TABLE chat_sessions ADD COLUMN session_data JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;

-- =============================================================================
-- ADD MISSING TABLES (if they don't exist)
-- =============================================================================

-- Create clothing_styles table if it doesn't exist (with your enhanced schema)
CREATE TABLE IF NOT EXISTS clothing_styles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    style_name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL CHECK (category IN (
        'aesthetic',        -- streetwear, boho, minimalist, etc.
        'cultural_etiquette', -- mosque-appropriate, temple-appropriate, etc.
        'functional'        -- rain-ready, airport-friendly, snow gear, etc.
    )),
    description TEXT,
    region_applicability JSONB DEFAULT '[]'::jsonb, -- list of regions or country codes (optional)
    qloo_entity_id VARCHAR(255), -- optional: Qloo-compatible entity ID if available
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_style_preferences table if it doesn't exist (with your enhanced schema)
CREATE TABLE IF NOT EXISTS user_style_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    style_id UUID NOT NULL,
    importance_level INTEGER DEFAULT 3 CHECK (importance_level BETWEEN 1 AND 5), -- optional user weighting
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, style_id),
    CONSTRAINT user_style_preferences_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT user_style_preferences_style_id_fkey FOREIGN KEY (style_id)
        REFERENCES clothing_styles(id) ON DELETE CASCADE
);

-- =============================================================================
-- ADD OPTIMIZED INDEXES FOR CLOTHING STYLES
-- =============================================================================

-- For fast lookups by style name (e.g., autocomplete, search)
CREATE UNIQUE INDEX IF NOT EXISTS idx_clothing_styles_style_name
  ON public.clothing_styles (style_name);

-- For filtering by category (aesthetic, functional, etc.)
CREATE INDEX IF NOT EXISTS idx_clothing_styles_category
  ON public.clothing_styles (category);

-- For region-based style filtering (on JSONB field)
CREATE INDEX IF NOT EXISTS idx_clothing_styles_region_applicability
  ON public.clothing_styles
  USING GIN (region_applicability);

-- For lookups via Qloo entity ID
CREATE INDEX IF NOT EXISTS idx_clothing_styles_qloo_entity_id
  ON public.clothing_styles (qloo_entity_id);

-- Speed up join queries between users and their style prefs
CREATE INDEX IF NOT EXISTS idx_user_style_preferences_user_id
  ON public.user_style_preferences (user_id);

CREATE INDEX IF NOT EXISTS idx_user_style_preferences_style_id
  ON public.user_style_preferences (style_id);

-- Composite index for user and style (avoid duplicate inserts or for upserts)
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_style_preferences_user_style
  ON public.user_style_preferences (user_id, style_id);

-- =============================================================================
-- ADD MISSING INDEXES FOR EXISTING TABLES
-- =============================================================================

-- Add missing indexes for users table (only new ones not in core indexes)
-- Note: Core user indexes are already defined in indexes/01_core_indexes.sql
-- Only adding indexes for new columns not in core tables

-- Add missing indexes for saved_destinations if the table exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'saved_destinations'
    ) THEN
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE tablename = 'saved_destinations'
            AND indexname = 'idx_saved_destinations_last_visited'
        ) THEN
            CREATE INDEX idx_saved_destinations_last_visited ON saved_destinations(last_visited);
        END IF;
    END IF;
END $$;

-- Add missing indexes for chat_sessions
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'chat_sessions'
        AND indexname = 'idx_chat_sessions_session_data'
    ) THEN
        CREATE INDEX idx_chat_sessions_session_data ON chat_sessions USING GIN (session_data);
    END IF;
END $$;

-- =============================================================================
-- ADD MISSING TRIGGERS
-- =============================================================================

-- Add timestamp triggers for new tables
DROP TRIGGER IF EXISTS update_clothing_styles_updated_at ON clothing_styles;
CREATE TRIGGER update_clothing_styles_updated_at
BEFORE UPDATE ON clothing_styles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- ADD MISSING RLS POLICIES
-- =============================================================================

-- Enable RLS for new tables
ALTER TABLE clothing_styles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_style_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies for clothing_styles (read-only for all users)
DROP POLICY IF EXISTS "Anyone can read clothing styles" ON clothing_styles;
CREATE POLICY "Anyone can read clothing styles" ON clothing_styles FOR SELECT TO anon, authenticated USING (true);

-- RLS Policies for user_style_preferences
DROP POLICY IF EXISTS "Users can view own style preferences" ON user_style_preferences;
DROP POLICY IF EXISTS "Users can insert own style preferences" ON user_style_preferences;
DROP POLICY IF EXISTS "Users can update own style preferences" ON user_style_preferences;
DROP POLICY IF EXISTS "Users can delete own style preferences" ON user_style_preferences;

CREATE POLICY "Users can view own style preferences" ON user_style_preferences
    FOR SELECT USING ((auth.uid() = user_id));

CREATE POLICY "Users can insert own style preferences" ON user_style_preferences
    FOR INSERT WITH CHECK ((auth.uid() = user_id));

CREATE POLICY "Users can update own style preferences" ON user_style_preferences
    FOR UPDATE USING ((auth.uid() = user_id)) WITH CHECK ((auth.uid() = user_id));

CREATE POLICY "Users can delete own style preferences" ON user_style_preferences
    FOR DELETE USING ((auth.uid() = user_id));

-- =============================================================================
-- ADD MISSING SYSTEM SETTINGS
-- =============================================================================

-- Insert additional system settings if they don't exist
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('max_style_preferences_per_user', '50'::jsonb, 'Maximum number of style preferences a user can have', false),
('style_recommendation_enabled', 'true'::jsonb, 'Whether to enable style recommendations', false),
('clothing_categories', '["aesthetic", "cultural_etiquette", "functional"]'::jsonb, 'Available clothing categories', true),
('style_importance_levels', '5'::jsonb, 'Maximum importance level for style preferences', true)
ON CONFLICT (setting_key) DO NOTHING;

-- =============================================================================
-- ADD MISSING COLUMNS TO USERS TABLE
-- =============================================================================

-- Add missing columns to users table if they don't exist
DO $$
BEGIN
    -- Add last_login column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'last_login'
    ) THEN
        ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
    END IF;

    -- Add preferences column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'preferences'
    ) THEN
        ALTER TABLE users ADD COLUMN preferences JSONB DEFAULT '{}'::jsonb;
    END IF;

    -- Add ui_preferences column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'ui_preferences'
    ) THEN
        ALTER TABLE users ADD COLUMN ui_preferences JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;

-- =============================================================================
-- ADD MISSING VIEWS
-- =============================================================================

-- Create enhanced user profile view if it doesn't exist
DROP VIEW IF EXISTS public.user_profile_view;

CREATE VIEW public.user_profile_view WITH (security_invoker=on) AS
SELECT
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.profile_completed,
    u.profile_picture_url,
    p.style_preferences,
    p.size_info,
    p.travel_patterns,
    p.quick_reply_preferences,
    p.packing_methods,
    p.currency_preferences,
    u.created_at,
    u.updated_at,
    u.last_login,

    -- NEW: Aggregate list of selected style names
    ARRAY_REMOVE(ARRAY_AGG(DISTINCT cs.style_name), NULL) AS selected_style_names,

    -- NEW: Additional user fields
    u.preferences,
    u.ui_preferences,
    u.default_location,
    u.max_bookmarks,
    u.max_conversations,
    u.subscription_tier,
    u.subscription_expires_at,
    u.is_premium

FROM
    public.users u
LEFT JOIN
    public.user_preferences p ON u.id = p.user_id
LEFT JOIN
    public.user_style_preferences usp ON u.id = usp.user_id
LEFT JOIN
    public.clothing_styles cs ON usp.style_id = cs.id

GROUP BY
    u.id, u.email, u.first_name, u.last_name, u.profile_completed,
    u.profile_picture_url, p.style_preferences, p.size_info,
    p.travel_patterns, p.quick_reply_preferences, p.packing_methods,
    p.currency_preferences, u.created_at, u.updated_at, u.last_login,
    u.preferences, u.ui_preferences, u.default_location, u.max_bookmarks,
    u.max_conversations, u.subscription_tier, u.subscription_expires_at,
    u.is_premium;

-- Create style preferences summary view
DROP VIEW IF EXISTS public.user_style_preferences_summary;

CREATE VIEW public.user_style_preferences_summary WITH (security_invoker=on) AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(usp.id) as total_style_preferences,
    COUNT(usp.id) FILTER (WHERE usp.importance_level >= 4) as high_priority_styles,
    COUNT(usp.id) FILTER (WHERE usp.importance_level <= 2) as low_priority_styles,
    COUNT(usp.id) FILTER (WHERE cs.category = 'aesthetic') as aesthetic_styles,
    COUNT(usp.id) FILTER (WHERE cs.category = 'cultural_etiquette') as cultural_styles,
    COUNT(usp.id) FILTER (WHERE cs.category = 'functional') as functional_styles,
    MAX(usp.created_at) as last_style_update
FROM users u
LEFT JOIN user_style_preferences usp ON u.id = usp.user_id
LEFT JOIN clothing_styles cs ON usp.style_id = cs.id
GROUP BY u.id, u.email;
