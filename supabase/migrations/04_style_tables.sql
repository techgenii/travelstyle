-- =============================================================================
-- TravelStyle AI - Style Tables
-- =============================================================================
-- This file contains tables for clothing styles and user style preferences
-- =============================================================================

-- Create the update_updated_at_column function first
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- CLOTHING STYLES TABLE
-- =============================================================================

-- Create clothing_styles table for managing different clothing styles
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

-- =============================================================================
-- USER STYLE PREFERENCES TABLE
-- =============================================================================

-- Create user_style_preferences table for storing user style choices
CREATE TABLE IF NOT EXISTS user_style_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    style_id UUID NOT NULL REFERENCES clothing_styles(id) ON DELETE CASCADE,
    importance_level INTEGER NOT NULL CHECK (importance_level >= 1 AND importance_level <= 5),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, style_id)
);

-- =============================================================================
-- INDEXES FOR STYLE TABLES
-- =============================================================================

-- Indexes for clothing_styles table
CREATE UNIQUE INDEX IF NOT EXISTS idx_clothing_styles_style_name
    ON clothing_styles(style_name);

CREATE INDEX IF NOT EXISTS idx_clothing_styles_category
    ON clothing_styles(category);

CREATE INDEX IF NOT EXISTS idx_clothing_styles_region_applicability
    ON clothing_styles USING GIN(region_applicability);

CREATE INDEX IF NOT EXISTS idx_clothing_styles_qloo_entity_id
    ON clothing_styles(qloo_entity_id);

-- Indexes for user_style_preferences table
CREATE INDEX IF NOT EXISTS idx_user_style_preferences_user_id
    ON user_style_preferences(user_id);

CREATE INDEX IF NOT EXISTS idx_user_style_preferences_style_id
    ON user_style_preferences(style_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_style_preferences_user_style
    ON user_style_preferences(user_id, style_id);

-- =============================================================================
-- TRIGGERS FOR STYLE TABLES
-- =============================================================================

-- Create trigger for clothing_styles updated_at
CREATE TRIGGER update_clothing_styles_updated_at
    BEFORE UPDATE ON clothing_styles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for user_style_preferences updated_at
CREATE TRIGGER update_user_style_preferences_updated_at
    BEFORE UPDATE ON user_style_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
