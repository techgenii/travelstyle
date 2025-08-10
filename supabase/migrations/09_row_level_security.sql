-- Row Level Security (RLS) Policies
-- This file contains all RLS policies for the TravelStyle AI application
-- Run this after all tables have been created

-- Enable RLS on all tables that need it
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
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
ALTER TABLE api_usage_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_style_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE clothing_styles ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_destinations ENABLE ROW LEVEL SECURITY;
ALTER TABLE packing_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE currency_favorites ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- USER DATA POLICIES
-- ============================================================================

-- Profiles table policies
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING ((auth.uid()) = id);

DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING ((auth.uid()) = id);

-- User preferences policies
DROP POLICY IF EXISTS "Users can view own preferences" ON user_preferences;
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own preferences" ON user_preferences;
CREATE POLICY "Users can insert own preferences" ON user_preferences
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own preferences" ON user_preferences;
CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR UPDATE USING ((auth.uid()) = user_id);

-- User auth tokens policies
DROP POLICY IF EXISTS "Users can view own tokens" ON user_auth_tokens;
CREATE POLICY "Users can view own tokens" ON user_auth_tokens
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own tokens" ON user_auth_tokens;
CREATE POLICY "Users can insert own tokens" ON user_auth_tokens
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own tokens" ON user_auth_tokens;
CREATE POLICY "Users can update own tokens" ON user_auth_tokens
    FOR UPDATE USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own tokens" ON user_auth_tokens;
CREATE POLICY "Users can delete own tokens" ON user_auth_tokens
    FOR DELETE USING ((auth.uid()) = user_id);

-- User style preferences policies
DROP POLICY IF EXISTS "Users can view own style preferences" ON user_style_preferences;
CREATE POLICY "Users can view own style preferences" ON user_style_preferences
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own style preferences" ON user_style_preferences;
CREATE POLICY "Users can insert own style preferences" ON user_style_preferences
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own style preferences" ON user_style_preferences;
CREATE POLICY "Users can update own style preferences" ON user_style_preferences
    FOR UPDATE USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own style preferences" ON user_style_preferences;
CREATE POLICY "Users can delete own style preferences" ON user_style_preferences
    FOR DELETE USING ((auth.uid()) = user_id);

-- Saved destinations policies
DROP POLICY IF EXISTS "Users can view own saved destinations" ON saved_destinations;
CREATE POLICY "Users can view own saved destinations" ON saved_destinations
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own saved destinations" ON saved_destinations;
CREATE POLICY "Users can insert own saved destinations" ON saved_destinations
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own saved destinations" ON saved_destinations;
CREATE POLICY "Users can update own saved destinations" ON saved_destinations
    FOR UPDATE USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own saved destinations" ON saved_destinations;
CREATE POLICY "Users can delete own saved destinations" ON saved_destinations
    FOR DELETE USING ((auth.uid()) = user_id);

-- Packing templates policies
DROP POLICY IF EXISTS "Users can view own packing templates" ON packing_templates;
CREATE POLICY "Users can view own packing templates" ON packing_templates
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own packing templates" ON packing_templates;
CREATE POLICY "Users can insert own packing templates" ON packing_templates
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own packing templates" ON packing_templates;
CREATE POLICY "Users can update own packing templates" ON packing_templates
    FOR UPDATE USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own packing templates" ON packing_templates;
CREATE POLICY "Users can delete own packing templates" ON packing_templates
    FOR DELETE USING ((auth.uid()) = user_id);

-- Currency favorites policies
DROP POLICY IF EXISTS "Users can view own currency favorites" ON currency_favorites;
CREATE POLICY "Users can view own currency favorites" ON currency_favorites
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own currency favorites" ON currency_favorites;
CREATE POLICY "Users can insert own currency favorites" ON currency_favorites
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own currency favorites" ON currency_favorites;
CREATE POLICY "Users can update own currency favorites" ON currency_favorites
    FOR UPDATE USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own currency favorites" ON currency_favorites;
CREATE POLICY "Users can delete own currency favorites" ON currency_favorites
    FOR DELETE USING ((auth.uid()) = user_id);

-- ============================================================================
-- CHAT & CONVERSATION POLICIES
-- ============================================================================

-- Conversations table policies
DROP POLICY IF EXISTS "Users can view own conversations" ON conversations;
CREATE POLICY "Users can view own conversations" ON conversations
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own conversations" ON conversations;
CREATE POLICY "Users can insert own conversations" ON conversations
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own conversations" ON conversations;
CREATE POLICY "Users can update own conversations" ON conversations
    FOR UPDATE USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own conversations" ON conversations;
CREATE POLICY "Users can delete own conversations" ON conversations
    FOR DELETE USING ((auth.uid()) = user_id);

-- Conversation messages policies
DROP POLICY IF EXISTS "Users can view own conversation messages" ON conversation_messages;
CREATE POLICY "Users can view own conversation messages" ON conversation_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
            AND c.user_id = (auth.uid())
        )
    );

DROP POLICY IF EXISTS "Users can insert own conversation messages" ON conversation_messages;
CREATE POLICY "Users can insert own conversation messages" ON conversation_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
            AND c.user_id = (auth.uid())
        )
    );

DROP POLICY IF EXISTS "Users can update own conversation messages" ON conversation_messages;
CREATE POLICY "Users can update own conversation messages" ON conversation_messages
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
            AND c.user_id = (auth.uid())
        )
    );

DROP POLICY IF EXISTS "Users can delete own conversation messages" ON conversation_messages;
CREATE POLICY "Users can delete own conversation messages" ON conversation_messages
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
            AND c.user_id = (auth.uid())
        )
    );

-- Chat sessions policies
DROP POLICY IF EXISTS "Users can view own chat sessions" ON chat_sessions;
CREATE POLICY "Users can view own chat sessions" ON chat_sessions
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own chat sessions" ON chat_sessions;
CREATE POLICY "Users can insert own chat sessions" ON chat_sessions
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own chat sessions" ON chat_sessions;
CREATE POLICY "Users can update own chat sessions" ON chat_sessions
    FOR UPDATE USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own chat sessions" ON chat_sessions;
CREATE POLICY "Users can delete own chat sessions" ON chat_sessions
    FOR DELETE USING ((auth.uid()) = user_id);

-- Chat bookmarks policies
DROP POLICY IF EXISTS "Users can view own bookmarks" ON chat_bookmarks;
CREATE POLICY "Users can view own bookmarks" ON chat_bookmarks
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own bookmarks" ON chat_bookmarks;
CREATE POLICY "Users can insert own bookmarks" ON chat_bookmarks
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own bookmarks" ON chat_bookmarks;
CREATE POLICY "Users can update own bookmarks" ON chat_bookmarks
    FOR UPDATE USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own bookmarks" ON chat_bookmarks;
CREATE POLICY "Users can delete own bookmarks" ON chat_bookmarks
    FOR DELETE USING ((auth.uid()) = user_id);

-- ============================================================================
-- ANALYTICS & FEEDBACK POLICIES
-- ============================================================================

-- Response feedback policies
DROP POLICY IF EXISTS "Users can view own feedback" ON response_feedback;
CREATE POLICY "Users can view own feedback" ON response_feedback
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own feedback" ON response_feedback;
CREATE POLICY "Users can insert own feedback" ON response_feedback
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

-- UI analytics policies
DROP POLICY IF EXISTS "Users can view own analytics" ON ui_analytics;
CREATE POLICY "Users can view own analytics" ON ui_analytics
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own analytics" ON ui_analytics;
CREATE POLICY "Users can insert own analytics" ON ui_analytics
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

-- API request logs policies
DROP POLICY IF EXISTS "Users can view own API logs" ON api_request_logs;
CREATE POLICY "Users can view own API logs" ON api_request_logs
    FOR SELECT USING ((auth.uid()) = user_id);

-- API usage tracking policies
DROP POLICY IF EXISTS "Users can view own API usage" ON api_usage_tracking;
CREATE POLICY "Users can view own API usage" ON api_usage_tracking
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own API usage" ON api_usage_tracking;
CREATE POLICY "Users can insert own API usage" ON api_usage_tracking
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own API usage" ON api_usage_tracking;
CREATE POLICY "Users can update own API usage" ON api_usage_tracking
    FOR UPDATE USING ((auth.uid()) = user_id);

-- Recommendation history policies
DROP POLICY IF EXISTS "Users can view own recommendation history" ON recommendation_history;
CREATE POLICY "Users can view own recommendation history" ON recommendation_history
    FOR SELECT USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own recommendation history" ON recommendation_history;
CREATE POLICY "Users can insert own recommendation history" ON recommendation_history
    FOR INSERT WITH CHECK ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own recommendation history" ON recommendation_history;
CREATE POLICY "Users can update own recommendation history" ON recommendation_history
    FOR UPDATE USING ((auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own recommendation history" ON recommendation_history;
CREATE POLICY "Users can delete own recommendation history" ON recommendation_history
    FOR DELETE USING ((auth.uid()) = user_id);

-- ============================================================================
-- CACHE TABLE POLICIES
-- ============================================================================

-- Cache tables are read-only for users, write access for service role
-- These allow public read access but restrict writes to authenticated users only

DROP POLICY IF EXISTS "Anyone can read weather cache" ON weather_cache;
CREATE POLICY "Anyone can read weather cache" ON weather_cache
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "Anyone can read currency cache" ON currency_rates_cache;
CREATE POLICY "Anyone can read currency cache" ON currency_rates_cache
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "Anyone can read cultural cache" ON cultural_insights_cache;
CREATE POLICY "Anyone can read cultural cache" ON cultural_insights_cache
    FOR SELECT TO anon, authenticated USING (true);

-- ============================================================================
-- CLOTHING STYLES POLICIES
-- ============================================================================

-- Clothing styles are publicly readable
DROP POLICY IF EXISTS "Anyone can read clothing styles" ON clothing_styles;
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

-- All policies now use DROP POLICY IF EXISTS for idempotency
-- This allows the migration to be run multiple times without errors
