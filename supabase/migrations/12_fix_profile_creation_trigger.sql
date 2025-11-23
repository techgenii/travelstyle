-- Migration to fix profile creation trigger
-- This ensures that when a user is created in auth.users, a corresponding profile is created in profiles table

-- Create a function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert into profiles table
    INSERT INTO public.profiles (
        id,
        email,
        first_name,
        last_name,
        profile_completed,
        created_at,
        updated_at
    ) VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'first_name', NULL),
        COALESCE(NEW.raw_user_meta_data->>'last_name', NULL),
        CASE
            WHEN NEW.raw_user_meta_data->>'first_name' IS NOT NULL
            AND NEW.raw_user_meta_data->>'last_name' IS NOT NULL
            THEN true
            ELSE false
        END,
        NEW.created_at,
        NEW.updated_at
    );

    -- Insert into user_preferences table with default values
    INSERT INTO public.user_preferences (
        user_id,
        style_preferences,
        size_info,
        travel_patterns,
        quick_reply_preferences,
        packing_methods,
        currency_preferences
    ) VALUES (
        NEW.id,
        '{}'::jsonb,
        '{}'::jsonb,
        '{}'::jsonb,
        '{"enabled": true}'::jsonb,
        '{}'::jsonb,
        '{}'::jsonb
    );

    RETURN NEW;
EXCEPTION
    WHEN unique_violation THEN
        -- Profile already exists, this is fine
        RETURN NEW;
    WHEN OTHERS THEN
        -- Log the error but don't fail the user creation
        RAISE WARNING 'Failed to create profile for user %: %', NEW.id, SQLERRM;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create the trigger on auth.users table
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO service_role;
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO postgres;

-- Update existing users who don't have profiles
-- This is a one-time fix for existing users
INSERT INTO public.profiles (
    id,
    email,
    first_name,
    last_name,
    profile_completed,
    created_at,
    updated_at
)
SELECT
    au.id,
    au.email,
    COALESCE(au.raw_user_meta_data->>'first_name', NULL),
    COALESCE(au.raw_user_meta_data->>'last_name', NULL),
    CASE
        WHEN au.raw_user_meta_data->>'first_name' IS NOT NULL
        AND au.raw_user_meta_data->>'last_name' IS NOT NULL
        THEN true
        ELSE false
    END,
    au.created_at,
    au.updated_at
FROM auth.users au
LEFT JOIN public.profiles p ON au.id = p.id
WHERE p.id IS NULL
ON CONFLICT (id) DO NOTHING;

-- Create user preferences for existing users who don't have them
INSERT INTO public.user_preferences (
    user_id,
    style_preferences,
    size_info,
    travel_patterns,
    quick_reply_preferences,
    packing_methods,
    currency_preferences
)
SELECT
    p.id,
    '{}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb,
    '{"enabled": true}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
FROM public.profiles p
LEFT JOIN public.user_preferences up ON p.id = up.user_id
WHERE up.user_id IS NULL
ON CONFLICT (user_id) DO NOTHING;
