-- =============================================================================
-- TravelStyle AI - Database Views
-- =============================================================================
-- This file contains database views for simplified data access
-- =============================================================================

-- =============================================================================
-- DATABASE VIEWS
-- =============================================================================

-- Enhanced user profile view that combines users, user_preferences, and style preferences
-- Note: This view is defined in 08_schema_enhancements.sql with full style integration
-- This placeholder ensures the view exists for the modular structure

-- API performance summary view
CREATE OR REPLACE VIEW api_performance_summary AS
SELECT
    api_name,
    endpoint,
    COUNT(*) as total_requests,
    AVG(response_time_ms) as avg_response_time,
    MAX(response_time_ms) as max_response_time,
    MIN(response_time_ms) as min_response_time,
    COUNT(CASE WHEN response_status >= 400 THEN 1 END) as error_count,
    ROUND(
        (COUNT(CASE WHEN response_status >= 400 THEN 1 END)::numeric / COUNT(*)::numeric) * 100, 2
    ) as error_rate_percent
FROM api_request_logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY api_name, endpoint
ORDER BY total_requests DESC;

-- =============================================================================
-- VIEW PERMISSIONS
-- =============================================================================

-- Grant permissions for user_profile_view
GRANT SELECT ON public.user_profile_view TO authenticated;
GRANT SELECT ON public.user_profile_view TO anon;

-- Grant permissions for api_performance_summary
GRANT SELECT ON api_performance_summary TO authenticated;
