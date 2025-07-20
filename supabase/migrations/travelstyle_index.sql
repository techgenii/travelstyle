-- Indexes for better performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_type ON conversations(type);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_conversations_destination ON conversations(destination);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

CREATE INDEX idx_response_feedback_user_id ON response_feedback(user_id);
CREATE INDEX idx_response_feedback_conversation_id ON response_feedback(conversation_id);
CREATE INDEX idx_response_feedback_type ON response_feedback(feedback_type);
CREATE INDEX idx_response_feedback_created_at ON response_feedback(created_at DESC);

CREATE INDEX idx_ui_analytics_user_id ON ui_analytics(user_id);
CREATE INDEX idx_ui_analytics_session_id ON ui_analytics(session_id);
CREATE INDEX idx_ui_analytics_interaction_type ON ui_analytics(interaction_type);
CREATE INDEX idx_ui_analytics_created_at ON ui_analytics(created_at DESC);

CREATE INDEX idx_chat_bookmarks_user_id ON chat_bookmarks(user_id);
CREATE INDEX idx_chat_bookmarks_conversation_id ON chat_bookmarks(conversation_id);

CREATE INDEX idx_saved_destinations_user_id ON saved_destinations(user_id);
CREATE INDEX idx_saved_destinations_last_used ON saved_destinations(last_used DESC);

CREATE INDEX idx_currency_favorites_user_id ON currency_favorites(user_id);
CREATE INDEX idx_currency_favorites_last_used ON currency_favorites(last_used DESC);

CREATE INDEX idx_packing_templates_user_id ON packing_templates(user_id);
CREATE INDEX idx_packing_templates_public ON packing_templates(is_public) WHERE is_public = true;
CREATE INDEX idx_packing_templates_destination_type ON packing_templates(destination_type);

CREATE INDEX idx_api_usage_user_id ON api_usage_tracking(user_id);
CREATE INDEX idx_api_usage_provider ON api_usage_tracking(api_provider);
CREATE INDEX idx_api_usage_created_at ON api_usage_tracking(created_at DESC);

CREATE INDEX idx_weather_cache_destination ON weather_cache(destination_normalized);
CREATE INDEX idx_weather_cache_expires_at ON weather_cache(expires_at);

CREATE INDEX idx_currency_rates_cache_base ON currency_rates_cache(base_currency);
CREATE INDEX idx_currency_rates_cache_expires_at ON currency_rates_cache(expires_at);

CREATE INDEX idx_cultural_insights_cache_destination ON cultural_insights_cache(destination_normalized);
CREATE INDEX idx_cultural_insights_cache_expires_at ON cultural_insights_cache(expires_at);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_conversation_id ON chat_sessions(conversation_id);
CREATE INDEX idx_chat_sessions_active ON chat_sessions(is_active) WHERE is_active = true;
CREATE INDEX idx_chat_sessions_expires_at ON chat_sessions(expires_at);

CREATE INDEX idx_api_request_logs_user_id ON api_request_logs(user_id);
CREATE INDEX idx_api_request_logs_endpoint ON api_request_logs(endpoint);
CREATE INDEX idx_api_request_logs_provider ON api_request_logs(api_provider);
CREATE INDEX idx_api_request_logs_created_at ON api_request_logs(created_at DESC);
CREATE INDEX idx_api_request_logs_cache_hit ON api_request_logs(cache_hit);

CREATE INDEX idx_conversation_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX idx_conversation_messages_role ON conversation_messages(role);
CREATE INDEX idx_conversation_messages_type ON conversation_messages(message_type);
CREATE INDEX idx_conversation_messages_created_at ON conversation_messages(created_at DESC);

CREATE INDEX idx_user_auth_tokens_user_id ON user_auth_tokens(user_id);
CREATE INDEX idx_user_auth_tokens_type ON user_auth_tokens(token_type);
CREATE INDEX idx_user_auth_tokens_expires_at ON user_auth_tokens(expires_at);
CREATE INDEX idx_user_auth_tokens_revoked ON user_auth_tokens(is_revoked) WHERE is_revoked = false;

CREATE INDEX idx_recommendation_history_user_id ON recommendation_history(user_id);
CREATE INDEX idx_recommendation_history_type ON recommendation_history(recommendation_type);
CREATE INDEX idx_recommendation_history_destination ON recommendation_history(destination);
CREATE INDEX idx_recommendation_history_created_at ON recommendation_history(created_at DESC);
