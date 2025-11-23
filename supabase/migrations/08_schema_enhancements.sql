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
-- ADD MISSING COLUMNS TO EXISTING TABLES
-- =============================================================================

-- Add missing columns to user_preferences if they don't exist
DO $$
BEGIN
    -- Add style_preferences column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_preferences'
        AND column_name = 'style_preferences'
    ) THEN
        ALTER TABLE user_preferences ADD COLUMN style_preferences JSONB DEFAULT '{}'::jsonb;
    END IF;

    -- Add size_info column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_preferences'
        AND column_name = 'size_info'
    ) THEN
        ALTER TABLE user_preferences ADD COLUMN size_info JSONB DEFAULT '{}'::jsonb;
    END IF;

    -- Add travel_patterns column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_preferences'
        AND column_name = 'travel_patterns'
    ) THEN
        ALTER TABLE user_preferences ADD COLUMN travel_patterns JSONB DEFAULT '{}'::jsonb;
    END IF;

    -- Add quick_reply_preferences column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_preferences'
        AND column_name = 'quick_reply_preferences'
    ) THEN
        ALTER TABLE user_preferences ADD COLUMN quick_reply_preferences JSONB DEFAULT '{"enabled": true}'::jsonb;
    END IF;

    -- Add packing_methods column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_preferences'
        AND column_name = 'packing_methods'
    ) THEN
        ALTER TABLE user_preferences ADD COLUMN packing_methods JSONB DEFAULT '{}'::jsonb;
    END IF;

    -- Add currency_preferences column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_preferences'
        AND column_name = 'currency_preferences'
    ) THEN
        ALTER TABLE user_preferences ADD COLUMN currency_preferences JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;

-- =============================================================================
-- ADD MISSING INDEXES FOR EXISTING TABLES
-- =============================================================================

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
-- ADD MISSING VIEWS
-- =============================================================================

-- Create enhanced user profile view if it doesn't exist
DROP VIEW IF EXISTS public.user_profile_view;

CREATE OR REPLACE VIEW public.user_profile_view WITH (security_invoker=on) AS
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
    CASE
        WHEN p.style_preferences IS NULL THEN '{}'::text[]
        WHEN p.style_preferences->>'selected_styles' IS NULL THEN '{}'::text[]
        ELSE (p.style_preferences->>'selected_styles')::text[]
    END AS selected_style_names,
    u.default_location,
    u.max_bookmarks,
    u.max_conversations,
    u.subscription_tier,
    u.subscription_expires_at,
    u.is_premium
FROM
    public.profiles u
LEFT JOIN
    public.user_preferences p ON u.id = p.user_id;

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
FROM profiles u
LEFT JOIN user_style_preferences usp ON u.id = usp.user_id
LEFT JOIN clothing_styles cs ON usp.style_id = cs.id
GROUP BY u.id, u.email;

-- =============================================================================
-- CREATE TRIGGERS FOR USER PROFILE VIEW
-- =============================================================================

-- Create or replace the trigger function
CREATE OR REPLACE FUNCTION handle_user_profile_view_update()
RETURNS TRIGGER AS $$
BEGIN
    -- For INSERT operations
    IF TG_OP = 'INSERT' THEN
        -- Insert into profiles table
        INSERT INTO profiles (
            id,
            email,
            first_name,
            last_name,
            profile_completed,
            profile_picture_url,
            default_location,
            max_bookmarks,
            max_conversations,
            subscription_tier,
            subscription_expires_at,
            is_premium,
            last_login
        ) VALUES (
            COALESCE(NEW.id, extensions.uuid_generate_v4()),
            NEW.email,
            NEW.first_name,
            NEW.last_name,
            NEW.profile_completed,
            NEW.profile_picture_url,
            NEW.default_location,
            NEW.max_bookmarks,
            NEW.max_conversations,
            NEW.subscription_tier,
            NEW.subscription_expires_at,
            NEW.is_premium,
            NEW.last_login
        )
        RETURNING id INTO NEW.id;

        -- Insert into user_preferences table
        INSERT INTO user_preferences (
            user_id,
            style_preferences,
            size_info,
            travel_patterns,
            quick_reply_preferences,
            packing_methods,
            currency_preferences
        ) VALUES (
            NEW.id,
            NEW.style_preferences,
            NEW.size_info,
            NEW.travel_patterns,
            NEW.quick_reply_preferences,
            NEW.packing_methods,
            NEW.currency_preferences
        );

        RETURN NEW;

    -- For UPDATE operations
    ELSIF TG_OP = 'UPDATE' THEN
        -- Update profiles table
        IF NEW.first_name IS DISTINCT FROM OLD.first_name OR
           NEW.last_name IS DISTINCT FROM OLD.last_name OR
           NEW.profile_completed IS DISTINCT FROM OLD.profile_completed OR
           NEW.profile_picture_url IS DISTINCT FROM OLD.profile_picture_url OR
           NEW.default_location IS DISTINCT FROM OLD.default_location OR
           NEW.max_bookmarks IS DISTINCT FROM OLD.max_bookmarks OR
           NEW.max_conversations IS DISTINCT FROM OLD.max_conversations OR
           NEW.subscription_tier IS DISTINCT FROM OLD.subscription_tier OR
           NEW.subscription_expires_at IS DISTINCT FROM OLD.subscription_expires_at OR
           NEW.is_premium IS DISTINCT FROM OLD.is_premium OR
           NEW.last_login IS DISTINCT FROM OLD.last_login THEN

            UPDATE profiles SET
                first_name = NEW.first_name,
                last_name = NEW.last_name,
                profile_completed = NEW.profile_completed,
                profile_picture_url = NEW.profile_picture_url,
                default_location = NEW.default_location,
                max_bookmarks = NEW.max_bookmarks,
                max_conversations = NEW.max_conversations,
                subscription_tier = NEW.subscription_tier,
                subscription_expires_at = NEW.subscription_expires_at,
                is_premium = NEW.is_premium,
                last_login = NEW.last_login,
                updated_at = NOW()
            WHERE id = NEW.id;
        END IF;

        -- Update user_preferences table
        IF NEW.style_preferences IS DISTINCT FROM OLD.style_preferences OR
           NEW.size_info IS DISTINCT FROM OLD.size_info OR
           NEW.travel_patterns IS DISTINCT FROM OLD.travel_patterns OR
           NEW.quick_reply_preferences IS DISTINCT FROM OLD.quick_reply_preferences OR
           NEW.packing_methods IS DISTINCT FROM OLD.packing_methods OR
           NEW.currency_preferences IS DISTINCT FROM OLD.currency_preferences THEN

            -- Check if user_preferences record exists
            IF EXISTS (SELECT 1 FROM user_preferences WHERE user_id = NEW.id) THEN
                UPDATE user_preferences SET
                    style_preferences = NEW.style_preferences,
                    size_info = NEW.size_info,
                    travel_patterns = NEW.travel_patterns,
                    quick_reply_preferences = NEW.quick_reply_preferences,
                    packing_methods = NEW.packing_methods,
                    currency_preferences = NEW.currency_preferences,
                    updated_at = NOW()
                WHERE user_id = NEW.id;
            ELSE
                INSERT INTO user_preferences (
                    user_id,
                    style_preferences,
                    size_info,
                    travel_patterns,
                    quick_reply_preferences,
                    packing_methods,
                    currency_preferences
                ) VALUES (
                    NEW.id,
                    NEW.style_preferences,
                    NEW.size_info,
                    NEW.travel_patterns,
                    NEW.quick_reply_preferences,
                    NEW.packing_methods,
                    NEW.currency_preferences
                );
            END IF;
        END IF;

    -- For DELETE operations
    ELSIF TG_OP = 'DELETE' THEN
        -- Delete from user_preferences first (due to foreign key constraint)
        DELETE FROM user_preferences WHERE user_id = OLD.id;

        -- Delete from profiles
        DELETE FROM profiles WHERE id = OLD.id;

        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for user_profile_view
DROP TRIGGER IF EXISTS user_profile_view_insert_trigger ON user_profile_view;
CREATE TRIGGER user_profile_view_insert_trigger
    INSTEAD OF INSERT ON user_profile_view
    FOR EACH ROW
    EXECUTE FUNCTION handle_user_profile_view_update();

DROP TRIGGER IF EXISTS user_profile_view_update_trigger ON user_profile_view;
CREATE TRIGGER user_profile_view_update_trigger
    INSTEAD OF UPDATE ON user_profile_view
    FOR EACH ROW
    EXECUTE FUNCTION handle_user_profile_view_update();

DROP TRIGGER IF EXISTS user_profile_view_delete_trigger ON user_profile_view;
CREATE TRIGGER user_profile_view_delete_trigger
    INSTEAD OF DELETE ON user_profile_view
    FOR EACH ROW
    EXECUTE FUNCTION handle_user_profile_view_update();
