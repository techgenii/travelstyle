-- =============================================================================
-- TravelStyle AI - User Profile Triggers
-- =============================================================================
-- This file contains triggers for the user_profile_view
-- =============================================================================

-- =============================================================================
-- USER PROFILE VIEW TRIGGER FUNCTION
-- =============================================================================

-- Create or replace the trigger function for user_profile_view
CREATE OR REPLACE FUNCTION handle_user_profile_view_update()
RETURNS TRIGGER AS $$
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

        -- Insert into user_preferences table if style_preferences are provided
        IF NEW.style_preferences IS NOT NULL OR NEW.size_info IS NOT NULL OR
           NEW.travel_patterns IS NOT NULL OR NEW.quick_reply_preferences IS NOT NULL OR
           NEW.packing_methods IS NOT NULL OR NEW.currency_preferences IS NOT NULL THEN

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

        RETURN NEW;

    -- For UPDATE operations
    ELSIF TG_OP = 'UPDATE' THEN
        -- Check if any user table fields have changed
        IF NEW.email IS DISTINCT FROM OLD.email OR
           NEW.first_name IS DISTINCT FROM OLD.first_name OR
           NEW.last_name IS DISTINCT FROM OLD.last_name OR
           NEW.profile_completed IS DISTINCT FROM OLD.profile_completed OR
           NEW.profile_picture_url IS DISTINCT FROM OLD.profile_picture_url OR
           NEW.default_location IS DISTINCT FROM OLD.default_location OR
           NEW.max_bookmarks IS DISTINCT FROM OLD.max_bookmarks OR
           NEW.max_conversations IS DISTINCT FROM OLD.max_conversations OR
           NEW.subscription_tier IS DISTINCT FROM OLD.subscription_tier OR
           NEW.subscription_expires_at IS DISTINCT FROM OLD.subscription_expires_at OR
           NEW.is_premium IS DISTINCT FROM OLD.is_premium OR
           NEW.last_login IS DISTINCT FROM OLD.last_login THEN

            UPDATE profiles SET
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
        END IF;

        -- Check if any user_preferences fields have changed
        IF NEW.style_preferences IS DISTINCT FROM OLD.style_preferences OR
           NEW.size_info IS DISTINCT FROM OLD.size_info OR
           NEW.travel_patterns IS DISTINCT FROM OLD.travel_patterns OR
           NEW.quick_reply_preferences IS DISTINCT FROM OLD.quick_reply_preferences OR
           NEW.packing_methods IS DISTINCT FROM OLD.packing_methods OR
           NEW.currency_preferences IS DISTINCT FROM OLD.currency_preferences THEN

            -- Insert or update user_preferences
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
            )
            ON CONFLICT (user_id) DO UPDATE SET
                style_preferences = EXCLUDED.style_preferences,
                size_info = EXCLUDED.size_info,
                travel_patterns = EXCLUDED.travel_patterns,
                quick_reply_preferences = EXCLUDED.quick_reply_preferences,
                packing_methods = EXCLUDED.packing_methods,
                currency_preferences = EXCLUDED.currency_preferences,
                updated_at = NOW();
        END IF;

        RETURN NEW;

    -- For DELETE operations
    ELSIF TG_OP = 'DELETE' THEN
        -- Delete from user_preferences first (due to foreign key constraint)
        DELETE FROM user_preferences WHERE user_id = OLD.id;

        -- Delete from profiles table
        DELETE FROM profiles WHERE id = OLD.id;

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- USER PROFILE VIEW TRIGGERS
-- =============================================================================

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
