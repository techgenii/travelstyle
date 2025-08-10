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
CREATE INDEX IF NOT EXISTS idx_api_request_logs_created_at ON api_request_logs(created_at DESC);

-- API usage tracking indexes
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_api_name ON api_usage_tracking(api_name);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage_tracking(created_at DESC);

-- Response feedback indexes
CREATE INDEX IF NOT EXISTS idx_response_feedback_user_id ON response_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_response_feedback_conversation_id ON response_feedback(conversation_id);
CREATE INDEX IF NOT EXISTS idx_response_feedback_type ON response_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_response_feedback_created_at ON response_feedback(created_at DESC);

-- UI analytics indexes
CREATE INDEX IF NOT EXISTS idx_ui_analytics_user_id ON ui_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_ui_analytics_session_id ON ui_analytics(session_id);
CREATE INDEX IF NOT EXISTS idx_ui_analytics_event_type ON ui_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_ui_analytics_created_at ON ui_analytics(created_at DESC);

-- Recommendation history indexes
CREATE INDEX IF NOT EXISTS idx_recommendation_history_user_id ON recommendation_history(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_history_type ON recommendation_history(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_recommendation_history_created_at ON recommendation_history(created_at DESC);

ALTER TABLE public.ui_analytics
ADD CONSTRAINT ui_analytics_user_id_fkey
FOREIGN KEY (user_id) REFERENCES public.profiles(id);

DO $$
BEGIN
    -- Check if the foreign key constraint already exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'ui_analytics_user_id_fkey'
        AND table_name = 'ui_analytics'
        AND constraint_type = 'FOREIGN KEY'
    ) THEN
        -- Create the foreign key if it doesn't exist
        ALTER TABLE public.ui_analytics
        ADD CONSTRAINT ui_analytics_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES public.profiles(id);

        RAISE NOTICE 'Foreign key constraint created successfully.';
    ELSE
        RAISE NOTICE 'Foreign key constraint already exists.';
    END IF;
END;
$$;
