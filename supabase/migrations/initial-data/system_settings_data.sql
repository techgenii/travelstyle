-- Insert some default system settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('supported_currencies', '["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "BRL", "MXN", "KRW", "SGD", "HKD", "NZD", "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "ILS", "ZAR", "THB", "PHP", "MYR", "IDR", "VND", "TRY", "RUB"]', 'List of supported currencies for conversion', true),
('default_packing_methods', '["5-4-3-2-1 Method", "3x3x3 Capsule", "Rule of 3s", "10×10 Challenge", "12-Piece Travel Capsule", "4x4 Wardrobe Grid", "1-2-3-4-5-6 Formula"]', 'Default packing methods available to users', true),
('feedback_collection_enabled', 'true', 'Whether to collect user feedback on responses', false),
('analytics_collection_enabled', 'true', 'Whether to collect UI analytics', false),
('weather_cache_duration_hours', '6', 'How long to cache weather data in hours', false),
('currency_cache_duration_hours', '1', 'How long to cache currency rates in hours', false),
('cultural_cache_duration_hours', '24', 'How long to cache cultural insights in hours', false),
('chat_session_timeout_hours', '24', 'How long chat sessions remain active', false);

-- =============================================================================
-- COMPLETE SUBSCRIPTION TIER CONFIGURATION
-- =============================================================================

-- Complete subscription tiers with enhanced limits, features, and business intelligence
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('subscription_tiers', '{
  "free": {
    "limits": {
      "style_preferences": 10,
      "conversations": 20,
      "bookmarks": 3,
      "api_rate_limit_per_hour": 5,
      "max_destinations": 5,
      "max_packing_templates": 2,
      "weather_cache_access": false,
      "currency_cache_access": false
    },
    "features": {
      "style_preferences": true,
      "conversations": true,
      "bookmarks": true,
      "basic_recommendations": true,
      "advanced_recommendations": false,
      "priority_support": false,
      "export_data": false,
      "api_access": false,
      "custom_integrations": false,
      "weather_insights": false,
      "cultural_insights": false
    }
  },
  "premium": {
    "limits": {
      "style_preferences": 50,
      "conversations": 100,
      "bookmarks": 50,
      "api_rate_limit_per_hour": 100,
      "max_destinations": 25,
      "max_packing_templates": 10,
      "weather_cache_access": true,
      "currency_cache_access": true
    },
    "features": {
      "style_preferences": true,
      "conversations": true,
      "bookmarks": true,
      "basic_recommendations": true,
      "advanced_recommendations": true,
      "priority_support": true,
      "export_data": true,
      "api_access": false,
      "custom_integrations": false,
      "weather_insights": true,
      "cultural_insights": true
    }
  },
  "enterprise": {
    "limits": {
      "style_preferences": 150,
      "conversations": 300,
      "bookmarks": 150,
      "api_rate_limit_per_hour": 300,
      "max_destinations": 100,
      "max_packing_templates": 50,
      "weather_cache_access": true,
      "currency_cache_access": true
    },
    "features": {
      "style_preferences": true,
      "conversations": true,
      "bookmarks": true,
      "basic_recommendations": true,
      "advanced_recommendations": true,
      "priority_support": true,
      "export_data": true,
      "api_access": true,
      "custom_integrations": true,
      "weather_insights": true,
      "cultural_insights": true
    }
  }
}'::jsonb, 'Complete subscription tier configuration with enhanced limits and features', true),

-- =============================================================================
-- SUBSCRIPTION BUSINESS INTELLIGENCE SETTINGS
-- =============================================================================

-- Subscription upgrade prompts and notifications
('subscription_upgrade_prompts', '{
  "free": {
    "conversation_limit_warning": 15,
    "bookmark_limit_warning": 2,
    "style_preference_warning": 8
  },
  "premium": {
    "conversation_limit_warning": 80,
    "bookmark_limit_warning": 40,
    "style_preference_warning": 40
  }
}'::jsonb, 'Warning thresholds for subscription upgrade prompts', false),

-- Subscription management behavior
('subscription_grace_period_hours', '24', 'Grace period in hours after subscription expires before enforcing limits', false),

('subscription_downgrade_behavior', '{
  "keep_existing_data": true,
  "archive_old_conversations": false,
  "notify_user": true,
  "offer_upgrade": true
}'::jsonb, 'Behavior when user downgrades subscription', false),

-- Subscription analytics and tracking
('subscription_analytics', '{
  "track_upgrade_conversions": true,
  "track_downgrade_reasons": true,
  "track_feature_usage": true,
  "track_limit_hits": true,
  "conversion_funnel_tracking": true
}'::jsonb, 'Settings for subscription analytics and conversion tracking', false),

-- Marketing and promotional settings
('subscription_marketing', '{
  "free_trial_days": 7,
  "upgrade_incentives": true,
  "loyalty_rewards": true,
  "referral_program": true
}'::jsonb, 'Marketing and promotional settings for subscriptions', false)

ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    description = EXCLUDED.description,
    updated_at = NOW();
