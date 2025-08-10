-- =============================================================================
-- TravelStyle AI - Additional Subscription Settings
-- =============================================================================
-- This file adds any additional subscription-related settings not covered in initial data
-- Note: Core subscription configuration is now in initial-data/system_settings_data.sql
-- =============================================================================

-- =============================================================================
-- ADDITIONAL SUBSCRIPTION SETTINGS (Future Extensions)
-- =============================================================================

-- Add any new subscription features or limits that get added after initial deployment
-- This file can be used for subscription system extensions without modifying initial data

-- Example: Add new subscription tiers or features here
-- Example: Add subscription-specific rate limiting rules
-- Example: Add subscription-based API quotas

-- For now, this file is minimal since all core subscription configuration
-- is consolidated in the initial data file for cleaner deployment

-- =============================================================================
-- SUBSCRIPTION SYSTEM HEALTH CHECKS
-- =============================================================================

-- Add subscription system monitoring settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('subscription_system_health', '{
  "monitor_usage_patterns": true,
  "alert_on_anomalies": true,
  "auto_scale_limits": false,
  "performance_monitoring": true
}'::jsonb, 'Subscription system health monitoring settings', false)

ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    description = EXCLUDED.description,
    updated_at = NOW();

