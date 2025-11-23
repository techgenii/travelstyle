-- =============================================================================
-- TravelStyle AI - Add Missing last_login Column and Fix View Triggers
-- =============================================================================
-- This migration:
-- 1. Adds the missing last_login column to the profiles table
-- 2. Updates the user_profile_view to include the last_login column
-- 3. Creates proper INSTEAD OF triggers to make the view updatable
-- 4. Fixes the "cannot update view" error that was occurring
-- =============================================================================

-- Add last_login column to profiles table
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS last_login timestamp with time zone;

-- Update the user_profile_view to include the last_login column
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

-- Update the trigger function to handle the last_login column
CREATE OR REPLACE FUNCTION handle_user_profile_view_update()
RETURNS TRIGGER AS $$
DECLARE
    profile_id uuid;
BEGIN
    -- For INSERT operations
    IF TG_OP = 'INSERT' THEN
        -- Insert into profiles table
        INSERT INTO profiles (
            id,
            email,
            first_name,
            last_name,
            profile_completed,
            profile_picture_url,
            default_location,
            max_bookmarks,
            max_conversations,
            subscription_tier,
            subscription_expires_at,
            is_premium,
            last_login
        ) VALUES (
            COALESCE(NEW.id, extensions.uuid_generate_v4()),
            NEW.email,
            NEW.first_name,
            NEW.last_name,
            NEW.profile_completed,
            NEW.profile_picture_url,
            NEW.default_location,
            NEW.max_bookmarks,
            NEW.max_conversations,
            NEW.subscription_tier,
            NEW.subscription_expires_at,
            NEW.is_premium,
            NEW.last_login
        )
        RETURNING id INTO NEW.id;

        -- Insert into user_preferences table
        INSERT INTO user_preferences (
            user_id,
            style_preferences,
            size_info,
            travel_patterns,
            quick_reply_preferences,
            packing_methods,
            currency_preferences
        ) VALUES (
            NEW.id,
            NEW.style_preferences,
            NEW.size_info,
            NEW.travel_patterns,
            NEW.quick_reply_preferences,
            NEW.packing_methods,
            NEW.currency_preferences
        );

        RETURN NEW;

    -- For UPDATE operations
    ELSIF TG_OP = 'UPDATE' THEN
        -- Update profiles table
        UPDATE profiles SET
            email = NEW.email,
            first_name = NEW.first_name,
            last_name = NEW.last_name,
            profile_completed = NEW.profile_completed,
            profile_picture_url = NEW.profile_picture_url,
            default_location = NEW.default_location,
            max_bookmarks = NEW.max_bookmarks,
            max_conversations = NEW.max_conversations,
            subscription_tier = NEW.subscription_tier,
            subscription_expires_at = NEW.subscription_expires_at,
            is_premium = NEW.is_premium,
            last_login = NEW.last_login,
            updated_at = NOW()
        WHERE id = NEW.id;

        -- Check if profiles update was successful
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Failed to update profiles table for user %', NEW.id;
        END IF;

        -- Update user_preferences table if any preferences are provided
        IF NEW.style_preferences IS NOT NULL OR NEW.size_info IS NOT NULL OR
           NEW.travel_patterns IS NOT NULL OR NEW.quick_reply_preferences IS NOT NULL OR
           NEW.packing_methods IS NOT NULL OR NEW.currency_preferences IS NOT NULL THEN

            -- Check if user_preferences record exists
            IF EXISTS (SELECT 1 FROM user_preferences WHERE user_id = NEW.id) THEN
                UPDATE user_preferences SET
                    style_preferences = COALESCE(NEW.style_preferences, style_preferences),
                    size_info = COALESCE(NEW.size_info, size_info),
                    travel_patterns = COALESCE(NEW.travel_patterns, travel_patterns),
                    quick_reply_preferences = COALESCE(NEW.quick_reply_preferences, quick_reply_preferences),
                    packing_methods = COALESCE(NEW.packing_methods, packing_methods),
                    currency_preferences = COALESCE(NEW.currency_preferences, currency_preferences),
                    updated_at = NOW()
                WHERE user_id = NEW.id;
            ELSE
                INSERT INTO user_preferences (
                    user_id,
                    style_preferences,
                    size_info,
                    travel_patterns,
                    quick_reply_preferences,
                    packing_methods,
                    currency_preferences
                ) VALUES (
                    NEW.id,
                    NEW.style_preferences,
                    NEW.size_info,
                    NEW.travel_patterns,
                    NEW.quick_reply_preferences,
                    NEW.packing_methods,
                    NEW.currency_preferences
                );
            END IF;
        END IF;

        RETURN NEW;

    -- For DELETE operations
    ELSIF TG_OP = 'DELETE' THEN
        -- Delete from user_preferences first (due to foreign key constraint)
        DELETE FROM user_preferences WHERE user_id = OLD.id;

        -- Delete from profiles
        DELETE FROM profiles WHERE id = OLD.id;

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for user_profile_view
DROP TRIGGER IF EXISTS user_profile_view_insert_trigger ON user_profile_view;
CREATE TRIGGER user_profile_view_insert_trigger
    INSTEAD OF INSERT ON user_profile_view
    FOR EACH ROW
    EXECUTE FUNCTION handle_user_profile_view_update();

DROP TRIGGER IF EXISTS user_profile_view_update_trigger ON user_profile_view;
CREATE TRIGGER user_profile_view_update_trigger
    INSTEAD OF UPDATE ON user_profile_view
    FOR EACH ROW
    EXECUTE FUNCTION handle_user_profile_view_update();

DROP TRIGGER IF EXISTS user_profile_view_delete_trigger ON user_profile_view;
CREATE TRIGGER user_profile_view_delete_trigger
    INSTEAD OF DELETE ON user_profile_view
    FOR EACH ROW
    EXECUTE FUNCTION handle_user_profile_view_update();

-- Grant permissions for the updated view
GRANT SELECT ON public.user_profile_view TO authenticated;
GRANT SELECT ON public.user_profile_view TO anon;
