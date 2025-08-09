-- =============================================================================
-- TravelStyle AI - Subscription-Based Limits
-- =============================================================================
-- This file adds subscription-based limit settings to the system_settings table
-- =============================================================================

-- Add subscription-based limit settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
-- Free tier limits
('max_style_preferences_per_user_free', '10'::jsonb, 'Maximum style preferences for free users', false),
('max_conversations_per_user_free', '20'::jsonb, 'Maximum conversations for free users', false),
('max_bookmarks_per_user_free', '3'::jsonb, 'Maximum bookmarks for free users', false),
('api_rate_limit_per_user_per_hour_free', '5'::jsonb, 'API rate limit per hour for free users', false),

-- Paid tier limits (premium/enterprise)
('max_style_preferences_per_user_paid', '50'::jsonb, 'Maximum style preferences for paid users', false),
('max_conversations_per_user_paid', '100'::jsonb, 'Maximum conversations for paid users', false),
('max_bookmarks_per_user_paid', '50'::jsonb, 'Maximum bookmarks for paid users', false),
('api_rate_limit_per_user_per_hour_paid', '100'::jsonb, 'API rate limit per hour for paid users', false),

-- Enterprise tier limits (3x paid)
('max_style_preferences_per_user_enterprise', '150'::jsonb, 'Maximum style preferences for enterprise users (3x paid)', false),
('max_conversations_per_user_enterprise', '300'::jsonb, 'Maximum conversations for enterprise users (3x paid)', false),
('max_bookmarks_per_user_enterprise', '150'::jsonb, 'Maximum bookmarks for enterprise users (3x paid)', false),
('api_rate_limit_per_user_per_hour_enterprise', '300'::jsonb, 'API rate limit per hour for enterprise users (3x paid)', false)

ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    description = EXCLUDED.description,
    updated_at = NOW();

-- =============================================================================
-- ADD SUBSCRIPTION TIER CONSTANTS
-- =============================================================================

-- Add subscription tier settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('subscription_tiers', '["free", "premium", "enterprise"]'::jsonb, 'Available subscription tiers', true),
('subscription_features', '{
  "free": {
    "style_preferences": true,
    "conversations": true,
    "bookmarks": true,
    "basic_recommendations": true
  },
  "premium": {
    "style_preferences": true,
    "conversations": true,
    "bookmarks": true,
    "advanced_recommendations": true,
    "priority_support": true,
    "export_data": true
  },
  "enterprise": {
    "style_preferences": true,
    "conversations": true,
    "bookmarks": true,
    "advanced_recommendations": true,
    "priority_support": true,
    "export_data": true,
    "api_access": true,
    "custom_integrations": true
  }
}'::jsonb, 'Features available for each subscription tier', true)

ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    description = EXCLUDED.description,
    updated_at = NOW();
