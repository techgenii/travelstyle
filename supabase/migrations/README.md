# TravelStyle AI Database Migrations

This directory contains all database migrations for the TravelStyle AI application. The migrations are organized in a logical order to ensure proper dependencies are met.

## Migration Structure

### Core Tables (Foundation)
- **`01_core_tables.sql`** - Users, user_preferences, and other core entities
- **`02_chat_tables.sql`** - Chat sessions, messages, and conversation data
- **`03_cache_tables.sql`** - Weather, cultural insights, and API response caching
- **`04_style_tables.sql`** - Clothing styles and user style preferences
- **`04_user_data_tables.sql`** - User-specific data like saved destinations and bookmarks

### Analytics and Views
- **`05_analytics_tables.sql`** - Analytics, logging, and performance tracking
- **`06_views.sql`** - Database views for complex queries and data access

### Functions and Triggers
- **`functions/01_timestamp_triggers.sql`** - Automatic timestamp management
- **`functions/02_user_profile_triggers.sql`** - User profile view triggers
- **`functions/03_cache_functions.sql`** - Cache management functions
- **`functions/04_chat_functions.sql`** - Chat-related functions
- **`functions/05_utility_functions.sql`** - General utility functions

### Indexes and Performance
- **`indexes/01_core_indexes.sql`** - Core table indexes
- **`indexes/02_chat_indexes.sql`** - Chat table indexes
- **`indexes/03_cache_indexes.sql`** - Cache table indexes
- **`indexes/04_analytics_indexes.sql`** - Analytics table indexes

### Schema Enhancements and Security
- **`08_schema_enhancements.sql`** - Adds missing columns and features
- **`09_row_level_security.sql`** - Row-level security policies
- **`10_subscription_limits.sql`** - Subscription and rate limiting configuration

## Migration Order

The migrations must be run in the correct order due to dependencies:

1. **Tables First** - Create all table structures
2. **Views Second** - Create views that depend on tables
3. **Functions Third** - Create functions and triggers that depend on views
4. **Indexes Fourth** - Create indexes for performance
5. **Enhancements Last** - Apply any schema enhancements or security policies

## Running Migrations

### Option 1: Run All Migrations
```bash
psql -h your-host -U your-user -d your-database -f run_all_migrations.sql
```

### Option 2: Run Individual Files
```bash
# Run in order
psql -f 01_core_tables.sql
psql -f 02_chat_tables.sql
psql -f 03_cache_tables.sql
psql -f 04_style_tables.sql
psql -f 04_user_data_tables.sql
psql -f 05_analytics_tables.sql
psql -f 06_views.sql
psql -f functions/01_timestamp_triggers.sql
psql -f functions/02_user_profile_triggers.sql
# ... continue with other files
```

## Key Features

### User Profile View
The `user_profile_view` is a comprehensive view that combines user data from multiple tables. It's fully updatable through PostgreSQL `INSTEAD OF` triggers that handle:
- INSERT operations (creates users and user_preferences records)
- UPDATE operations (updates both users and user_preferences tables)
- DELETE operations (removes user data)

### Style Management
The application includes a sophisticated style management system:
- `clothing_styles` table with categories (aesthetic, cultural_etiquette, functional)
- `user_style_preferences` table for user style choices
- Region-specific style applicability
- Integration with Qloo entity IDs

### Caching System
Multiple caching layers for performance:
- Weather data caching
- Cultural insights caching
- API response caching
- Automatic cleanup of duplicate entries

### Security
- Row-level security policies
- Proper permission grants
- Secure view definitions with `security_invoker=on`

## Troubleshooting

### Common Issues

1. **Migration Order Errors**: Ensure tables are created before views, and views before functions
2. **Permission Errors**: Check that the database user has sufficient privileges
3. **Dependency Errors**: Verify that all required extensions (like `uuid-ossp`) are installed

### Reset Database
If you need to start fresh:
```bash
psql -f 00_reset_database.sql
psql -f run_all_migrations.sql
```

## File Naming Convention

- **`XX_description.sql`** - Main migration files (XX = sequential number)
- **`functions/XX_description.sql`** - Function and trigger files
- **`indexes/XX_description.sql`** - Index creation files

## Notes

- All migrations use `IF NOT EXISTS` and `DROP IF EXISTS` for idempotency
- Timestamps are automatically managed through triggers
- Views are created with `security_invoker=on` for proper permission handling
- The `user_profile_view` is the primary interface for user profile operations
