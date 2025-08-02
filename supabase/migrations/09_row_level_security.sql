-- Row Level Security (RLS) Policies
-- This file contains all RLS policies for the TravelStyle AI application
-- Run this after all tables have been created

-- Enable RLS on all tables that need it
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE response_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE ui_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_bookmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_auth_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE weather_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE currency_rates_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE cultural_insights_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_request_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_style_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE clothing_styles ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- USER DATA POLICIES
-- ============================================================================

-- Users table policies
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING ((auth.uid()) = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING ((auth.uid()) = id);

-- User preferences policies
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING ((auth.uid()) = user_id);

CREATE POLICY "Users can insert own preferences" ON user_preferences
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR UPDATE USING ((auth.uid()) = user_id);

-- User auth tokens policies
CREATE POLICY "Users can view own tokens" ON user_auth_tokens
    FOR SELECT USING ((auth.uid()) = user_id);

CREATE POLICY "Users can insert own tokens" ON user_auth_tokens
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

CREATE POLICY "Users can update own tokens" ON user_auth_tokens
    FOR UPDATE USING ((auth.uid()) = user_id);

CREATE POLICY "Users can delete own tokens" ON user_auth_tokens
    FOR DELETE USING ((auth.uid()) = user_id);

-- User style preferences policies
CREATE POLICY "Users can view own style preferences" ON user_style_preferences
    FOR SELECT USING ((auth.uid()) = user_id);

CREATE POLICY "Users can insert own style preferences" ON user_style_preferences
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

CREATE POLICY "Users can update own style preferences" ON user_style_preferences
    FOR UPDATE USING ((auth.uid()) = user_id);

CREATE POLICY "Users can delete own style preferences" ON user_style_preferences
    FOR DELETE USING ((auth.uid()) = user_id);

-- ============================================================================
-- CHAT & CONVERSATION POLICIES
-- ============================================================================

-- Conversations table policies
CREATE POLICY "Users can view own conversations" ON conversations
    FOR SELECT USING ((auth.uid()) = user_id);

CREATE POLICY "Users can insert own conversations" ON conversations
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

CREATE POLICY "Users can update own conversations" ON conversations
    FOR UPDATE USING ((auth.uid()) = user_id);

CREATE POLICY "Users can delete own conversations" ON conversations
    FOR DELETE USING ((auth.uid()) = user_id);

-- Conversation messages policies
CREATE POLICY "Users can view own conversation messages" ON conversation_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
            AND c.user_id = (auth.uid())
        )
    );

CREATE POLICY "Users can insert own conversation messages" ON conversation_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
            AND c.user_id = (auth.uid())
        )
    );

CREATE POLICY "Users can update own conversation messages" ON conversation_messages
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
            AND c.user_id = (auth.uid())
        )
    );

CREATE POLICY "Users can delete own conversation messages" ON conversation_messages
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
            AND c.user_id = (auth.uid())
        )
    );

-- Chat sessions policies
CREATE POLICY "Users can view own chat sessions" ON chat_sessions
    FOR SELECT USING ((auth.uid()) = user_id);

CREATE POLICY "Users can insert own chat sessions" ON chat_sessions
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

CREATE POLICY "Users can update own chat sessions" ON chat_sessions
    FOR UPDATE USING ((auth.uid()) = user_id);

CREATE POLICY "Users can delete own chat sessions" ON chat_sessions
    FOR DELETE USING ((auth.uid()) = user_id);

-- Chat bookmarks policies
CREATE POLICY "Users can view own bookmarks" ON chat_bookmarks
    FOR SELECT USING ((auth.uid()) = user_id);

CREATE POLICY "Users can insert own bookmarks" ON chat_bookmarks
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

CREATE POLICY "Users can update own bookmarks" ON chat_bookmarks
    FOR UPDATE USING ((auth.uid()) = user_id);

CREATE POLICY "Users can delete own bookmarks" ON chat_bookmarks
    FOR DELETE USING ((auth.uid()) = user_id);

-- ============================================================================
-- ANALYTICS & FEEDBACK POLICIES
-- ============================================================================

-- Response feedback policies
CREATE POLICY "Users can view own feedback" ON response_feedback
    FOR SELECT USING ((auth.uid()) = user_id);

CREATE POLICY "Users can insert own feedback" ON response_feedback
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

-- UI analytics policies
CREATE POLICY "Users can view own analytics" ON ui_analytics
    FOR SELECT USING ((auth.uid()) = user_id);

CREATE POLICY "Users can insert own analytics" ON ui_analytics
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

-- API request logs policies
CREATE POLICY "Users can view own API logs" ON api_request_logs
    FOR SELECT USING ((auth.uid()) = user_id);

-- Recommendation history policies
CREATE POLICY "Users can view own recommendation history" ON recommendation_history
    FOR SELECT USING ((auth.uid()) = user_id);

CREATE POLICY "Users can insert own recommendation history" ON recommendation_history
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

CREATE POLICY "Users can update own recommendation history" ON recommendation_history
    FOR UPDATE USING ((auth.uid()) = user_id);

CREATE POLICY "Users can delete own recommendation history" ON recommendation_history
    FOR DELETE USING ((auth.uid()) = user_id);

-- ============================================================================
-- CACHE TABLE POLICIES
-- ============================================================================

-- Cache tables are read-only for users, write access for service role
-- These allow public read access but restrict writes to authenticated users only

CREATE POLICY "Anyone can read weather cache" ON weather_cache
    FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "Anyone can read currency cache" ON currency_rates_cache
    FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "Anyone can read cultural cache" ON cultural_insights_cache
    FOR SELECT TO anon, authenticated USING (true);

-- ============================================================================
-- CLOTHING STYLES POLICIES
-- ============================================================================

-- Clothing styles are publicly readable
CREATE POLICY "Anyone can read clothing styles" ON clothing_styles
    FOR SELECT TO anon, authenticated USING (true);

-- ============================================================================
-- NOTES
-- ============================================================================

-- System settings table does not have RLS enabled as it contains global settings
-- that should be accessible to all authenticated users

-- The service role (used by your backend) bypasses RLS by default
-- This allows your backend to perform operations that users cannot do directly

-- All policies use auth.uid() to ensure users can only access their own data
-- except for cache tables which allow public read access for performance
