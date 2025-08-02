-- =============================================================================
-- TravelStyle AI - Analytics Table Indexes
-- =============================================================================
-- This file contains indexes for analytics and tracking tables
-- =============================================================================

-- =============================================================================
-- ANALYTICS TABLE INDEXES
-- =============================================================================

-- API request logs indexes
CREATE INDEX IF NOT EXISTS idx_api_request_logs_user_id ON api_request_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_api_request_logs_endpoint ON api_request_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_request_logs_provider ON api_request_logs(api_provider);
CREATE INDEX IF NOT EXISTS idx_api_request_logs_created_at ON api_request_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_request_logs_cache_hit ON api_request_logs(cache_hit);

-- API usage tracking indexes
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_provider ON api_usage_tracking(api_provider);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage_tracking(created_at DESC);

-- Response feedback indexes
CREATE INDEX IF NOT EXISTS idx_response_feedback_user_id ON response_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_response_feedback_conversation_id ON response_feedback(conversation_id);
CREATE INDEX IF NOT EXISTS idx_response_feedback_type ON response_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_response_feedback_created_at ON response_feedback(created_at DESC);

-- UI analytics indexes
CREATE INDEX IF NOT EXISTS idx_ui_analytics_user_id ON ui_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_ui_analytics_session_id ON ui_analytics(session_id);
CREATE INDEX IF NOT EXISTS idx_ui_analytics_interaction_type ON ui_analytics(interaction_type);
CREATE INDEX IF NOT EXISTS idx_ui_analytics_created_at ON ui_analytics(created_at DESC);

-- Recommendation history indexes
CREATE INDEX IF NOT EXISTS idx_recommendation_history_user_id ON recommendation_history(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_history_type ON recommendation_history(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_recommendation_history_destination ON recommendation_history(destination);
CREATE INDEX IF NOT EXISTS idx_recommendation_history_created_at ON recommendation_history(created_at DESC);
