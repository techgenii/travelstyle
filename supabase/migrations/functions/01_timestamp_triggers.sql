-- =============================================================================
-- TravelStyle AI - Timestamp Update Triggers
-- =============================================================================
-- This file contains triggers for automatically updating updated_at timestamps
-- =============================================================================

-- First, create the missing tables before adding triggers

-- Create packing_templates table
CREATE TABLE IF NOT EXISTS packing_templates (
    id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
    user_id uuid NOT NULL REFERENCES users(id),
    template_name text NOT NULL,
    template_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    is_default boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Create saved_destinations table
CREATE TABLE IF NOT EXISTS saved_destinations (
    id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
    user_id uuid NOT NULL REFERENCES users(id),
    destination_name text NOT NULL,
    destination_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    is_favorite boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Now the triggers will work correctly
CREATE TRIGGER update_packing_templates_updated_at BEFORE UPDATE ON packing_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_saved_destinations_updated_at BEFORE UPDATE ON saved_destinations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update updated_at column automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =============================================================================
-- TIMESTAMP TRIGGERS
-- =============================================================================

-- Core table timestamp triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Chat table timestamp triggers
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Cache table timestamp triggers
CREATE TRIGGER update_weather_cache_updated_at BEFORE UPDATE ON weather_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_currency_rates_cache_updated_at BEFORE UPDATE ON currency_rates_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cultural_insights_cache_updated_at BEFORE UPDATE ON cultural_insights_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- User data table timestamp triggers
CREATE TRIGGER update_packing_templates_updated_at BEFORE UPDATE ON packing_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Analytics table timestamp triggers
CREATE TRIGGER update_api_usage_tracking_updated_at BEFORE UPDATE ON api_usage_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_saved_destinations_updated_at BEFORE UPDATE ON saved_destinations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

