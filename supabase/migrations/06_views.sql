-- =============================================================================
-- TravelStyle AI - Views
-- =============================================================================
-- This file contains database views for complex queries
-- =============================================================================

-- =============================================================================
-- USER PROFILE VIEW
-- =============================================================================

-- Create enhanced user profile view
DROP VIEW IF EXISTS public.user_profile_view;

CREATE OR REPLACE VIEW public.user_profile_view WITH (security_invoker=on) AS
SELECT
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.profile_completed,
    u.profile_picture_url,
    p.style_preferences,
    p.size_info,
    p.travel_patterns,
    p.quick_reply_preferences,
    p.packing_methods,
    p.currency_preferences,
    u.created_at,
    u.updated_at,
    u.last_login,
    CASE
        WHEN p.style_preferences IS NULL THEN '{}'::text[]
        WHEN p.style_preferences->>'selected_styles' IS NULL THEN '{}'::text[]
        ELSE (p.style_preferences->>'selected_styles')::text[]
    END AS selected_style_names,
    u.default_location,
    u.max_bookmarks,
    u.max_conversations,
    u.subscription_tier,
    u.subscription_expires_at,
    u.is_premium
FROM
            public.profiles u
LEFT JOIN
    public.user_preferences p ON u.id = p.user_id;

-- =============================================================================
-- USER STYLE PREFERENCES SUMMARY VIEW
-- =============================================================================

-- Create style preferences summary view
DROP VIEW IF EXISTS public.user_style_preferences_summary;

CREATE VIEW public.user_style_preferences_summary WITH (security_invoker=on) AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(usp.id) as total_style_preferences,
    COUNT(usp.id) FILTER (WHERE usp.importance_level >= 4) as high_priority_styles,
    COUNT(usp.id) FILTER (WHERE usp.importance_level <= 2) as low_priority_styles,
    COUNT(usp.id) FILTER (WHERE cs.category = 'aesthetic') as aesthetic_styles,
    COUNT(usp.id) FILTER (WHERE cs.category = 'cultural_etiquette') as cultural_styles,
    COUNT(usp.id) FILTER (WHERE cs.category = 'functional') as functional_styles,
    MAX(usp.created_at) as last_style_update
FROM profiles u
LEFT JOIN user_style_preferences usp ON u.id = usp.user_id
LEFT JOIN clothing_styles cs ON usp.style_id = cs.id
GROUP BY u.id, u.email;

-- =============================================================================
-- API PERFORMANCE SUMMARY VIEW
-- =============================================================================

-- Create API performance summary view
DROP VIEW IF EXISTS public.api_performance_summary;

CREATE VIEW public.api_performance_summary WITH (security_invoker=on) AS
SELECT
    endpoint,
    method,
    COUNT(*) as total_requests,
    AVG(response_time_ms) as avg_response_time,
    MAX(response_time_ms) as max_response_time,
    MIN(response_time_ms) as min_response_time,
    COUNT(*) FILTER (WHERE response_status >= 200 AND response_status < 300) as successful_requests,
    COUNT(*) FILTER (WHERE response_status >= 400) as error_requests,
    AVG(response_time_ms) FILTER (WHERE response_status >= 200 AND response_status < 300) as avg_success_time
FROM api_request_logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY endpoint, method
ORDER BY total_requests DESC;

-- =============================================================================
-- VIEW PERMISSIONS
-- =============================================================================

-- Grant permissions for user_profile_view
GRANT SELECT ON public.user_profile_view TO authenticated;
GRANT SELECT ON public.user_profile_view TO anon;

-- Grant permissions for user_style_preferences_summary
GRANT SELECT ON public.user_style_preferences_summary TO authenticated;
GRANT SELECT ON public.user_style_preferences_summary TO anon;

-- Grant permissions for api_performance_summary
GRANT SELECT ON public.api_performance_summary TO authenticated;
GRANT SELECT ON public.api_performance_summary TO anon;

