-- Triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_packing_templates_updated_at BEFORE UPDATE ON packing_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Additional triggers for new tables
CREATE TRIGGER update_weather_cache_updated_at BEFORE UPDATE ON weather_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_currency_rates_cache_updated_at BEFORE UPDATE ON currency_rates_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cultural_insights_cache_updated_at BEFORE UPDATE ON cultural_insights_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_weather_cache_updated_at
    BEFORE UPDATE ON weather_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for user_profile_view inserts
CREATE TRIGGER user_profile_view_insert_trigger
    INSTEAD OF INSERT ON user_profile_view
    FOR EACH ROW
    EXECUTE FUNCTION handle_user_profile_view_update();

-- Create trigger for user_profile_view updates
CREATE TRIGGER user_profile_view_update_trigger
    INSTEAD OF UPDATE ON user_profile_view
    FOR EACH ROW
    EXECUTE FUNCTION handle_user_profile_view_update();


-- Function to clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM weather_cache WHERE expires_at < NOW();
    DELETE FROM currency_rates_cache WHERE expires_at < NOW();
    DELETE FROM cultural_insights_cache WHERE expires_at < NOW();
    DELETE FROM chat_sessions WHERE expires_at < NOW() AND is_active = false;
    DELETE FROM user_auth_tokens WHERE expires_at < NOW() OR is_revoked = true;
END;
$$ LANGUAGE plpgsql;

-- Function to get or create chat session
CREATE OR REPLACE FUNCTION get_or_create_chat_session(
    p_user_id UUID,
    p_conversation_id UUID,
    p_destination VARCHAR DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    session_id UUID;
BEGIN
    -- Try to get existing active session
    SELECT id INTO session_id
    FROM chat_sessions
    WHERE user_id = p_user_id
      AND conversation_id = p_conversation_id
      AND is_active = true
      AND expires_at > NOW();

    -- If no active session found, create new one
    IF session_id IS NULL THEN
        INSERT INTO chat_sessions (user_id, conversation_id, destination)
        VALUES (p_user_id, p_conversation_id, p_destination)
        RETURNING id INTO session_id;
    END IF;

    RETURN session_id;
END;
$$ LANGUAGE plpgsql;

-- Function to handle user_profile_view updates and inserts
CREATE OR REPLACE FUNCTION handle_user_profile_view_update()
RETURNS TRIGGER AS $$
BEGIN
    -- For INSERT operations
    IF TG_OP = 'INSERT' THEN
        -- Insert into users table
        INSERT INTO users (
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
            is_premium
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
            NEW.is_premium
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

    -- For UPDATE operations
    ELSIF TG_OP = 'UPDATE' THEN
        -- Update users table
        IF NEW.first_name IS DISTINCT FROM OLD.first_name OR
           NEW.last_name IS DISTINCT FROM OLD.last_name OR
           NEW.profile_completed IS DISTINCT FROM OLD.profile_completed OR
           NEW.profile_picture_url IS DISTINCT FROM OLD.profile_picture_url OR
           NEW.default_location IS DISTINCT FROM OLD.default_location OR
           NEW.max_bookmarks IS DISTINCT FROM OLD.max_bookmarks OR
           NEW.max_conversations IS DISTINCT FROM OLD.max_conversations OR
           NEW.subscription_tier IS DISTINCT FROM OLD.subscription_tier OR
           NEW.subscription_expires_at IS DISTINCT FROM OLD.subscription_expires_at OR
           NEW.is_premium IS DISTINCT FROM OLD.is_premium THEN

            UPDATE users SET
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
                updated_at = NOW()
            WHERE id = NEW.id;
        END IF;

        -- Update user_preferences table
        IF NEW.style_preferences IS DISTINCT FROM OLD.style_preferences OR
           NEW.size_info IS DISTINCT FROM OLD.size_info OR
           NEW.travel_patterns IS DISTINCT FROM OLD.travel_patterns OR
           NEW.quick_reply_preferences IS DISTINCT FROM OLD.quick_reply_preferences OR
           NEW.packing_methods IS DISTINCT FROM OLD.packing_methods OR
           NEW.currency_preferences IS DISTINCT FROM OLD.currency_preferences THEN

            -- Check if user_preferences record exists
            IF EXISTS (SELECT 1 FROM user_preferences WHERE user_id = NEW.id) THEN
                UPDATE user_preferences SET
                    style_preferences = NEW.style_preferences,
                    size_info = NEW.size_info,
                    travel_patterns = NEW.travel_patterns,
                    quick_reply_preferences = NEW.quick_reply_preferences,
                    packing_methods = NEW.packing_methods,
                    currency_preferences = NEW.currency_preferences,
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
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to normalize destination names for consistent caching
CREATE OR REPLACE FUNCTION normalize_destination(destination_name VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
    RETURN LOWER(TRIM(REGEXP_REPLACE(destination_name, '[^a-zA-Z0-9\s]', '', 'g')));
END;
$$ LANGUAGE plpgsql;
