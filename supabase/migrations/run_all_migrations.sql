-- Master Migration Script for TravelStyle AI
-- Run this after a complete database reset
-- This script runs all migrations in the correct order

-- ============================================================================
-- STEP 1: CORE TABLES (Foundation)
-- ============================================================================
\echo 'Creating core tables...'
\i 01_core_tables.sql

-- ============================================================================
-- STEP 2: CHAT TABLES (Depends on profiles)
-- ============================================================================
\echo 'Creating chat tables...'
\i 02_chat_tables.sql

-- ============================================================================
-- STEP 3: CACHE TABLES (Independent)
-- ============================================================================
\echo 'Creating cache tables...'
\i 03_cache_tables.sql

-- ============================================================================
-- STEP 4: STYLE TABLES (Depends on profiles)
-- ============================================================================
\echo 'Creating style tables...'
\i 04_style_tables.sql

-- ============================================================================
-- STEP 5: USER DATA TABLES (Depends on profiles)
-- ============================================================================
\echo 'Creating user data tables...'
\i 04_user_data_tables.sql

-- ============================================================================
-- STEP 6: ANALYTICS TABLES (Depends on profiles and conversations)
-- ============================================================================
\echo 'Creating analytics tables...'
\i 05_analytics_tables.sql

-- ============================================================================
-- STEP 7: VIEWS (Depends on all tables)
-- ============================================================================
\echo 'Creating views...'
\i 06_views.sql

-- ============================================================================
-- STEP 8: FUNCTIONS (Depends on tables and views)
-- ============================================================================
\echo 'Creating functions...'
\i functions/01_timestamp_triggers.sql
\i functions/02_user_profile_triggers.sql
\i functions/03_cache_functions.sql
\i functions/04_chat_functions.sql
\i functions/05_utility_functions.sql

-- ============================================================================
-- STEP 9: INDEXES (Depends on tables)
-- ============================================================================
\echo 'Creating indexes...'
\i indexes/01_core_indexes.sql
\i indexes/02_chat_indexes.sql
\i indexes/03_cache_indexes.sql
\i indexes/04_analytics_indexes.sql

-- ============================================================================
-- STEP 10: SCHEMA ENHANCEMENTS (Adds missing columns)
-- ============================================================================
\echo 'Applying schema enhancements...'
\i 08_schema_enhancements.sql

-- ============================================================================
-- STEP 11: ADD MISSING LAST_LOGIN COLUMN (Fix for user_profile_view)
-- ============================================================================
\echo 'Adding missing last_login column...'
\i 11_add_last_login_column.sql

-- ============================================================================
-- STEP 12: FIX PROFILE CREATION TRIGGER (Ensures profiles are created automatically)
-- ============================================================================
\echo 'Fixing profile creation trigger...'
\i 12_fix_profile_creation_trigger.sql

-- ============================================================================
-- STEP 13: ROW LEVEL SECURITY (Security policies)
-- ============================================================================
\echo 'Setting up Row Level Security...'
\i 09_row_level_security.sql

-- ============================================================================
-- STEP 14: SUBSCRIPTION LIMITS (Final configuration)
-- ============================================================================
\echo 'Setting up subscription limits...'
\i 10_subscription_limits.sql

-- ============================================================================
-- COMPLETION
-- ============================================================================
\echo 'Migration completed successfully!'
\echo 'Your TravelStyle AI database is now ready.'
\echo 'Note: File storage is handled by Cloudinary, not Supabase storage.'
