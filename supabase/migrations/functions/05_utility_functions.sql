-- =============================================================================
-- TravelStyle AI - Utility Functions
-- =============================================================================
-- This file contains general utility functions for the application
-- =============================================================================

-- =============================================================================
-- GENERAL UTILITY FUNCTIONS
-- =============================================================================

-- Function to generate a random string
CREATE OR REPLACE FUNCTION generate_random_string(length INTEGER DEFAULT 10)
RETURNS TEXT AS $$
DECLARE
    chars TEXT := 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    result TEXT := '';
    i INTEGER := 0;
BEGIN
    FOR i IN 1..length LOOP
        result := result || substr(chars, floor(random() * length(chars))::integer + 1, 1);
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to validate email format
CREATE OR REPLACE FUNCTION is_valid_email(email TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
END;
$$ LANGUAGE plpgsql;

-- Function to get user activity summary
CREATE OR REPLACE FUNCTION get_user_activity_summary(user_id UUID, days_back INTEGER DEFAULT 30)
RETURNS TABLE(
    total_conversations BIGINT,
    total_messages BIGINT,
    total_api_requests BIGINT,
    last_activity TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT c.id)::BIGINT as total_conversations,
        COALESCE(SUM(c.messages), 0)::BIGINT as total_messages,
        COUNT(arl.id)::BIGINT as total_api_requests,
        GREATEST(
            MAX(c.updated_at),
            MAX(arl.created_at)
        ) as last_activity
    FROM users u
    LEFT JOIN conversations c ON u.id = c.user_id
        AND c.updated_at >= NOW() - INTERVAL '1 day' * days_back
    LEFT JOIN api_request_logs arl ON u.id = arl.user_id
        AND arl.created_at >= NOW() - INTERVAL '1 day' * days_back
    WHERE u.id = get_user_activity_summary.user_id
    GROUP BY u.id;
END;
$$ LANGUAGE plpgsql;

-- Function to get system health metrics
CREATE OR REPLACE FUNCTION get_system_health_metrics()
RETURNS TABLE(
    metric_name TEXT,
    metric_value NUMERIC,
    metric_unit TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        'total_users'::TEXT as metric_name,
        COUNT(*)::NUMERIC as metric_value,
        'users'::TEXT as metric_unit
    FROM users
    UNION ALL
    SELECT
        'active_conversations'::TEXT,
        COUNT(*)::NUMERIC,
        'conversations'::TEXT
    FROM conversations
    WHERE is_archived = false
    UNION ALL
    SELECT
        'total_messages'::TEXT,
        COALESCE(SUM(messages), 0)::NUMERIC,
        'messages'::TEXT
    FROM conversations
    UNION ALL
    SELECT
        'cache_entries'::TEXT,
        (COUNT(*) FILTER (WHERE table_name = 'weather_cache') +
         COUNT(*) FILTER (WHERE table_name = 'currency_rates_cache') +
         COUNT(*) FILTER (WHERE table_name = 'cultural_insights_cache'))::NUMERIC,
        'entries'::TEXT
    FROM (
        SELECT 'weather_cache' as table_name FROM weather_cache
        UNION ALL
        SELECT 'currency_rates_cache' FROM currency_rates_cache
        UNION ALL
        SELECT 'cultural_insights_cache' FROM cultural_insights_cache
    ) cache_tables;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data(
    days_to_keep INTEGER DEFAULT 90,
    max_conversations_per_user INTEGER DEFAULT 100
)
RETURNS TABLE(
    operation TEXT,
    affected_rows INTEGER
) AS $$
DECLARE
    deleted_conversations INTEGER;
    deleted_messages INTEGER;
    deleted_logs INTEGER;
BEGIN
    -- Archive old conversations
    UPDATE conversations
    SET is_archived = true, updated_at = NOW()
    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep
      AND is_archived = false;

    GET DIAGNOSTICS deleted_conversations = ROW_COUNT;

    -- Delete old API request logs
    DELETE FROM api_request_logs
    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;

    GET DIAGNOSTICS deleted_logs = ROW_COUNT;

    -- Delete old UI analytics
    DELETE FROM ui_analytics
    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;

    -- Limit conversations per user (keep most recent)
    WITH user_conversation_counts AS (
        SELECT user_id, COUNT(*) as conv_count
        FROM conversations
        WHERE is_archived = false
        GROUP BY user_id
        HAVING COUNT(*) > max_conversations_per_user
    ),
    conversations_to_archive AS (
        SELECT c.id
        FROM conversations c
        JOIN user_conversation_counts ucc ON c.user_id = ucc.user_id
        WHERE c.is_archived = false
        ORDER BY c.updated_at ASC
        LIMIT (SELECT SUM(conv_count - max_conversations_per_user) FROM user_conversation_counts)
    )
    UPDATE conversations
    SET is_archived = true, updated_at = NOW()
    WHERE id IN (SELECT id FROM conversations_to_archive);

    GET DIAGNOSTICS deleted_messages = ROW_COUNT;

    RETURN QUERY
    SELECT 'archived_conversations'::TEXT, deleted_conversations
    UNION ALL
    SELECT 'deleted_api_logs'::TEXT, deleted_logs
    UNION ALL
    SELECT 'archived_excess_conversations'::TEXT, deleted_messages;
END;
$$ LANGUAGE plpgsql;
