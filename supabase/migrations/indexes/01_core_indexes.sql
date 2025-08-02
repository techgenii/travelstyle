-- =============================================================================
-- TravelStyle AI - Core Table Indexes
-- =============================================================================
-- This file contains indexes for core user and system tables
-- =============================================================================

-- =============================================================================
-- CORE TABLE INDEXES
-- =============================================================================

-- User table indexes
CREATE INDEX idx_users_subscription_tier ON public.users(subscription_tier);
CREATE INDEX idx_users_subscription_expires ON public.users(subscription_expires_at);
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_profile_completed ON public.users(profile_completed);

-- User preferences indexes
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

-- User auth tokens indexes
CREATE INDEX idx_user_auth_tokens_user_id ON user_auth_tokens(user_id);
CREATE INDEX idx_user_auth_tokens_type ON user_auth_tokens(token_type);
CREATE INDEX idx_user_auth_tokens_expires_at ON user_auth_tokens(expires_at);
CREATE INDEX idx_user_auth_tokens_revoked ON user_auth_tokens(is_revoked) WHERE is_revoked = false;

-- System settings indexes
CREATE INDEX idx_system_settings_key ON public.system_settings(setting_key);
CREATE INDEX idx_system_settings_public ON public.system_settings(is_public);
