-- =============================================================================
-- TravelStyle AI - Chat Functions
-- =============================================================================
-- This file contains functions for chat and conversation management
-- =============================================================================

-- =============================================================================
-- CHAT MANAGEMENT FUNCTIONS
-- =============================================================================

-- Function to increment message count in conversations
CREATE OR REPLACE FUNCTION increment_messages(conv_id UUID)
RETURNS INTEGER AS $$
DECLARE
    current_count INTEGER;
BEGIN
    -- Get current message count
    SELECT COALESCE(messages, 0) INTO current_count
    FROM conversations
    WHERE id = conv_id;

    -- Return incremented count
    RETURN current_count + 1;
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
      AND (expires_at IS NULL OR expires_at > NOW());

    -- If no active session found, create new one
    IF session_id IS NULL THEN
        INSERT INTO chat_sessions (user_id, conversation_id, destination, expires_at)
        VALUES (p_user_id, p_conversation_id, p_destination, NOW() + INTERVAL '24 hours')
        RETURNING id INTO session_id;
    END IF;

    RETURN session_id;
END;
$$ LANGUAGE plpgsql;

-- Function to archive old conversations
CREATE OR REPLACE FUNCTION archive_old_conversations(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE conversations
    SET is_archived = true, updated_at = NOW()
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old
      AND is_archived = false;

    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get conversation statistics
CREATE OR REPLACE FUNCTION get_conversation_stats(user_id UUID)
RETURNS TABLE(
    total_conversations BIGINT,
    active_conversations BIGINT,
    archived_conversations BIGINT,
    total_messages BIGINT,
    avg_messages_per_conversation NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_conversations,
        COUNT(*) FILTER (WHERE is_archived = false)::BIGINT as active_conversations,
        COUNT(*) FILTER (WHERE is_archived = true)::BIGINT as archived_conversations,
        COALESCE(SUM(messages), 0)::BIGINT as total_messages,
        CASE
            WHEN COUNT(*) > 0 THEN AVG(messages)
            ELSE 0
        END as avg_messages_per_conversation
    FROM conversations
    WHERE conversations.user_id = get_conversation_stats.user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired chat sessions
CREATE OR REPLACE FUNCTION cleanup_expired_chat_sessions()
RETURNS INTEGER AS $$
DECLARE
    cleaned_count INTEGER;
BEGIN
    UPDATE chat_sessions
    SET is_active = false, updated_at = NOW()
    WHERE expires_at < NOW() AND is_active = true;

    GET DIAGNOSTICS cleaned_count = ROW_COUNT;
    RETURN cleaned_count;
END;
$$ LANGUAGE plpgsql;
