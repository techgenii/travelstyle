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

-- Function to normalize destination names for consistent caching
CREATE OR REPLACE FUNCTION normalize_destination(destination_name VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
    RETURN LOWER(TRIM(REGEXP_REPLACE(destination_name, '[^a-zA-Z0-9\s]', '', 'g')));
END;
$$ LANGUAGE plpgsql;
