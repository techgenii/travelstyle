-- Master Migration Script for TravelStyle AI
-- Run this after a complete database reset
-- This script runs all migrations in the correct order

-- ============================================================================
-- STEP 1: CORE TABLES (Foundation)
-- ============================================================================
\echo 'Creating core tables...'
\i 01_core_tables.sql

-- ============================================================================
-- STEP 2: CHAT TABLES (Depends on users)
-- ============================================================================
\echo 'Creating chat tables...'
\i 02_chat_tables.sql

-- ============================================================================
-- STEP 3: CACHE TABLES (Independent)
-- ============================================================================
\echo 'Creating cache tables...'
\i 03_cache_tables.sql

-- ============================================================================
-- STEP 4: USER DATA TABLES (Depends on users)
-- ============================================================================
\echo 'Creating user data tables...'
\i 04_user_data_tables.sql

-- ============================================================================
-- STEP 5: ANALYTICS TABLES (Depends on users and conversations)
-- ============================================================================
\echo 'Creating analytics tables...'
\i 05_analytics_tables.sql

-- ============================================================================
-- STEP 6: VIEWS (Depends on all tables)
-- ============================================================================
\echo 'Creating views...'
\i 06_views.sql

-- ============================================================================
-- STEP 7: ONE-TIME FIXES (For existing databases - safe to run)
-- ============================================================================
\echo 'Applying one-time fixes...'
\i 07_one_time_fixes.sql

-- ============================================================================
-- STEP 8: SCHEMA ENHANCEMENTS
-- ============================================================================
\echo 'Applying schema enhancements...'
\i 08_schema_enhancements.sql

-- ============================================================================
-- STEP 9: ROW LEVEL SECURITY (Security policies)
-- ============================================================================
\echo 'Setting up Row Level Security...'
\i 09_row_level_security.sql

-- ============================================================================
-- STEP 10: FUNCTIONS (Depends on tables)
-- ============================================================================
\echo 'Creating functions...'
\i functions/01_timestamp_triggers.sql
\i functions/02_user_profile_triggers.sql
\i functions/03_cache_functions.sql
\i functions/04_chat_functions.sql
\i functions/05_utility_functions.sql

-- ============================================================================
-- STEP 11: INDEXES (Depends on tables)
-- ============================================================================
\echo 'Creating indexes...'
\i indexes/01_core_indexes.sql
\i indexes/02_chat_indexes.sql
\i indexes/03_cache_indexes.sql
\i indexes/04_analytics_indexes.sql

-- ============================================================================
-- COMPLETION
-- ============================================================================
\echo 'Migration completed successfully!'
\echo 'Your TravelStyle AI database is now ready.'
\echo 'Note: File storage is handled by Cloudinary, not Supabase storage.'
