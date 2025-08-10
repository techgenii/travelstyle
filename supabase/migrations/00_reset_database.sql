-- Complete Database Reset Script
-- This script drops all tables, functions, triggers, and indexes
-- Run this to start completely fresh

-- Disable triggers temporarily
SET session_replication_role = replica;

-- Drop all views first (they depend on tables)
DROP VIEW IF EXISTS user_profile_view CASCADE;
DROP VIEW IF EXISTS api_performance_summary CASCADE;

-- Drop all tables (in reverse dependency order)
DROP TABLE IF EXISTS ui_analytics CASCADE;
DROP TABLE IF EXISTS recommendation_history CASCADE;
DROP TABLE IF EXISTS response_feedback CASCADE;
DROP TABLE IF EXISTS api_usage_tracking CASCADE;
DROP TABLE IF EXISTS api_request_logs CASCADE;
DROP TABLE IF EXISTS saved_destinations CASCADE;
DROP TABLE IF EXISTS packing_templates CASCADE;
DROP TABLE IF EXISTS currency_favorites CASCADE;
DROP TABLE IF EXISTS chat_bookmarks CASCADE;
DROP TABLE IF EXISTS conversation_messages CASCADE;
DROP TABLE IF EXISTS chat_sessions CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS weather_cache CASCADE;
DROP TABLE IF EXISTS currency_rates_cache CASCADE;
DROP TABLE IF EXISTS cultural_insights_cache CASCADE;
DROP TABLE IF EXISTS user_auth_tokens CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;

-- Drop all functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS handle_user_profile_view_update() CASCADE;
DROP FUNCTION IF EXISTS cleanup_expired_cache() CASCADE;
DROP FUNCTION IF EXISTS normalize_destination() CASCADE;
DROP FUNCTION IF EXISTS is_cache_expired() CASCADE;
DROP FUNCTION IF EXISTS get_cache_age_hours() CASCADE;
DROP FUNCTION IF EXISTS refresh_cache_entry() CASCADE;
DROP FUNCTION IF EXISTS increment_messages() CASCADE;
DROP FUNCTION IF EXISTS get_or_create_chat_session() CASCADE;
DROP FUNCTION IF EXISTS archive_old_conversations() CASCADE;
DROP FUNCTION IF EXISTS get_conversation_stats() CASCADE;
DROP FUNCTION IF EXISTS cleanup_expired_chat_sessions() CASCADE;
DROP FUNCTION IF EXISTS generate_random_string() CASCADE;
DROP FUNCTION IF EXISTS is_valid_email() CASCADE;
DROP FUNCTION IF EXISTS get_user_activity_summary() CASCADE;
DROP FUNCTION IF EXISTS get_system_health_metrics() CASCADE;
DROP FUNCTION IF EXISTS cleanup_old_data() CASCADE;

-- Re-enable triggers
SET session_replication_role = DEFAULT;

-- Reset sequences if any exist
-- (PostgreSQL will automatically recreate these when tables are recreated)

-- Note: Storage buckets and policies will need to be recreated separately
-- as they are managed through Supabase's storage system
