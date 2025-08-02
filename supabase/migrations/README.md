# Database Schema Migrations

This directory contains the database schema migrations for TravelStyle AI, split into logical modules for better organization and maintainability.

## Migration Files

### Core Tables (`01_core_tables.sql`)
- **Purpose**: Core user and system tables
- **Tables**: `users`, `user_preferences`, `user_auth_tokens`, `system_settings`
- **Dependencies**: None (base tables)

### Chat & Conversations (`02_chat_tables.sql`)
- **Purpose**: Chat functionality and conversation management
- **Tables**: `conversations`, `conversation_messages`, `chat_sessions`, `chat_bookmarks`
- **Dependencies**: Requires `01_core_tables.sql` (references `users`)

### Cache Tables (`03_cache_tables.sql`)
- **Purpose**: External API data caching
- **Tables**: `cultural_insights_cache`, `currency_rates_cache`, `weather_cache`
- **Dependencies**: None (standalone cache tables)

### User Data & Preferences (`04_user_data_tables.sql`)
- **Purpose**: User-specific data and preferences
- **Tables**: `currency_favorites`, `packing_templates`, `saved_destinations`
- **Dependencies**: Requires `01_core_tables.sql` (references `users`)

### Analytics & Tracking (`05_analytics_tables.sql`)
- **Purpose**: Analytics, monitoring, and usage tracking
- **Tables**: `api_request_logs`, `api_usage_tracking`, `recommendation_history`, `response_feedback`, `ui_analytics`
- **Dependencies**: Requires `01_core_tables.sql` and `02_chat_tables.sql`

### Views (`06_views.sql`)
- **Purpose**: Database views for simplified data access
- **Views**: `user_profile_view`, `api_performance_summary`
- **Dependencies**: Requires all table migrations

### One-Time Fixes (`07_one_time_fixes.sql`)
- **Purpose**: Fixes for existing databases
- **Fixes**: Currency cache constraints, conversation messages schema, chat sessions schema
- **Dependencies**: Requires all table migrations
- **Note**: Run this file once after the main schema is applied

### Schema Enhancements (`08_schema_enhancements.sql`)
- **Purpose**: Additional schema improvements and optimizations
- **Enhancements**: Additional constraints, indexes, and schema refinements
- **Dependencies**: Requires all table migrations

### Row Level Security (`09_row_level_security.sql`)
- **Purpose**: Security policies for data access control
- **Policies**: RLS policies for all user-facing tables
- **Dependencies**: Requires all table migrations
- **Note**: Run this after all tables are created to enable security

## Functions

### Timestamp Triggers (`functions/01_timestamp_triggers.sql`)
- **Purpose**: Automatic timestamp updates
- **Functions**: `update_updated_at_column()`
- **Triggers**: All table timestamp triggers
- **Dependencies**: Requires all table migrations

### User Profile Triggers (`functions/02_user_profile_triggers.sql`)
- **Purpose**: User profile view operations
- **Functions**: `handle_user_profile_view_update()`
- **Triggers**: User profile view triggers
- **Dependencies**: Requires `01_core_tables.sql`

### Cache Functions (`functions/03_cache_functions.sql`)
- **Purpose**: Cache management and utilities
- **Functions**: `cleanup_expired_cache()`, `normalize_destination()`, `is_cache_expired()`, `get_cache_age_hours()`, `refresh_cache_entry()`
- **Dependencies**: Requires `03_cache_tables.sql`

### Chat Functions (`functions/04_chat_functions.sql`)
- **Purpose**: Chat and conversation management
- **Functions**: `increment_messages()`, `get_or_create_chat_session()`, `archive_old_conversations()`, `get_conversation_stats()`, `cleanup_expired_chat_sessions()`
- **Dependencies**: Requires `02_chat_tables.sql`

### Utility Functions (`functions/05_utility_functions.sql`)
- **Purpose**: General utility functions
- **Functions**: `generate_random_string()`, `is_valid_email()`, `get_user_activity_summary()`, `get_system_health_metrics()`, `cleanup_old_data()`
- **Dependencies**: Requires all table migrations

## Indexes

### Core Indexes (`indexes/01_core_indexes.sql`)
- **Purpose**: Indexes for core tables
- **Tables**: `users`, `user_preferences`, `user_auth_tokens`, `system_settings`
- **Dependencies**: Requires `01_core_tables.sql`

### Chat Indexes (`indexes/02_chat_indexes.sql`)
- **Purpose**: Indexes for chat tables
- **Tables**: `conversations`, `chat_sessions`, `conversation_messages`, `chat_bookmarks`
- **Dependencies**: Requires `02_chat_tables.sql`

### Cache Indexes (`indexes/03_cache_indexes.sql`)
- **Purpose**: Indexes for cache tables
- **Tables**: `weather_cache`, `currency_rates_cache`, `cultural_insights_cache`
- **Dependencies**: Requires `03_cache_tables.sql`

### Analytics Indexes (`indexes/04_analytics_indexes.sql`)
- **Purpose**: Indexes for analytics tables
- **Tables**: `api_request_logs`, `api_usage_tracking`, `response_feedback`, `ui_analytics`, `recommendation_history`
- **Dependencies**: Requires `05_analytics_tables.sql`

## Storage

**Note**: This project uses Cloudinary for file storage instead of Supabase storage.
Storage buckets and policies are not included in the migration as file uploads
are handled through the Cloudinary service in the backend.

## Migration Order

Run migrations in this order:

```sql
-- 1. Core tables (foundation)
\i 01_core_tables.sql

-- 2. Chat tables (depends on users)
\i 02_chat_tables.sql

-- 3. Cache tables (independent)
\i 03_cache_tables.sql

-- 4. User data tables (depends on users)
\i 04_user_data_tables.sql

-- 5. Analytics tables (depends on users and conversations)
\i 05_analytics_tables.sql

-- 6. Views (depends on all tables)
\i 06_views.sql

-- 7. One-time fixes (for existing databases)
\i 07_one_time_fixes.sql

-- 8. Schema enhancements
\i 08_schema_enhancements.sql

-- 9. Row Level Security policies
\i 09_row_level_security.sql

-- 10. Functions (depends on tables)
\i functions/01_timestamp_triggers.sql
\i functions/02_user_profile_triggers.sql
\i functions/03_cache_functions.sql
\i functions/04_chat_functions.sql
\i functions/05_utility_functions.sql

-- 11. Indexes (depends on tables)
\i indexes/01_core_indexes.sql
\i indexes/02_chat_indexes.sql
\i indexes/03_cache_indexes.sql
\i indexes/04_analytics_indexes.sql
```

## Benefits of Complete Split

1. **Modularity**: Each file focuses on a specific domain
2. **Maintainability**: Easier to find and modify specific components
3. **Dependency Management**: Clear dependencies between modules
4. **Selective Deployment**: Can deploy specific modules independently
5. **Version Control**: Better diff tracking for specific changes
6. **Team Collaboration**: Different team members can work on different modules
7. **Testing**: Can test specific functions or components in isolation
8. **Performance**: Can optimize specific indexes or functions independently
9. **Clean Structure**: No duplicate files, organized by concern

## File Structure

```
supabase/migrations/
├── 01_core_tables.sql
├── 02_chat_tables.sql
├── 03_cache_tables.sql
├── 04_user_data_tables.sql
├── 05_analytics_tables.sql
├── 06_views.sql
├── 07_one_time_fixes.sql
├── 08_schema_enhancements.sql
├── 09_row_level_security.sql
├── README.md
├── functions/
│   ├── 01_timestamp_triggers.sql
│   ├── 02_user_profile_triggers.sql
│   ├── 03_cache_functions.sql
│   ├── 04_chat_functions.sql
│   └── 05_utility_functions.sql
└── indexes/
    ├── 01_core_indexes.sql
    ├── 02_chat_indexes.sql
    ├── 03_cache_indexes.sql
    └── 04_analytics_indexes.sql
```

## Notes

- Each file includes appropriate indexes for the tables it defines
- Foreign key constraints are properly defined
- All tables use UUID primary keys with `uuid_generate_v4()`
- Timestamps use `timestamp with time zone` for consistency
- JSONB columns are used for flexible data storage
- Functions are organized by domain and purpose
- Indexes are optimized for common query patterns
- Storage policies follow security best practices
- No duplicate files - clean, organized structure
