-- =============================================================================
-- TravelStyle AI - Chat Table Indexes
-- =============================================================================
-- This file contains indexes for chat and conversation tables
-- =============================================================================

-- =============================================================================
-- CHAT TABLE INDEXES
-- =============================================================================

-- Conversation table indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_type ON conversations(type);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_conversations_destination ON conversations(destination);

-- Chat sessions indexes
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_conversation_id ON chat_sessions(conversation_id);
CREATE INDEX idx_chat_sessions_active ON chat_sessions(is_active) WHERE is_active = true;
CREATE INDEX idx_chat_sessions_expires_at ON chat_sessions(expires_at);

-- Conversation messages indexes
CREATE INDEX idx_conversation_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX idx_conversation_messages_role ON conversation_messages(role);
CREATE INDEX idx_conversation_messages_type ON conversation_messages(message_type);
CREATE INDEX idx_conversation_messages_created_at ON conversation_messages(created_at DESC);

-- Chat bookmarks indexes
CREATE INDEX idx_chat_bookmarks_user_id ON chat_bookmarks(user_id);
CREATE INDEX idx_chat_bookmarks_conversation_id ON chat_bookmarks(conversation_id);
