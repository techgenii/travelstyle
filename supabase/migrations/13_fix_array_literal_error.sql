-- =============================================================================
-- TravelStyle AI - Fix Array Literal Error in Views
-- =============================================================================
-- This migration fixes the "malformed array literal" error in user_profile_view
-- by properly handling NULL values and array casting
-- =============================================================================

-- Drop and recreate the user_profile_view with proper array handling
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

-- Grant permissions for user_profile_view
GRANT SELECT ON public.user_profile_view TO authenticated;
GRANT SELECT ON public.user_profile_view TO anon;
