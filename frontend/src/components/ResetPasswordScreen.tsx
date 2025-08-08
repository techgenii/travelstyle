import React, { useState } from 'react';
import { Plane, Lock, Eye, EyeOff, Loader2, CheckCircle } from 'lucide-react';

interface ResetPasswordScreenProps {
  onResetPassword: (accessToken: string, newPassword: string) => Promise<void>;
  onBackToLogin: () => void;
  accessToken: string;
  isLoading: boolean;
}

const ResetPasswordScreen: React.FC<ResetPasswordScreenProps> = ({ 
  onResetPassword, 
  onBackToLogin, 
  accessToken,
  isLoading 
}) => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordReset, setPasswordReset] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    try {
      setError('');
      await onResetPassword(accessToken, newPassword);
      setPasswordReset(true);
    } catch (err) {
      setError('Failed to reset password. Please try again.');
    }
  };

  if (passwordReset) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-light via-secondary-light to-accent-light flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Logo and Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-2xl mb-4 shadow-lg">
              <Plane className="w-8 h-8 text-background" />
            </div>
            <h1 className="text-3xl font-bold text-text-primary mb-2">TravelStyle AI</h1>
            <p className="text-text-secondary">Your personal travel style assistant</p>
          </div>

          {/* Success Message */}
          <div className="bg-surface rounded-2xl shadow-xl p-8 border border-border text-center">
            <div className="w-16 h-16 bg-success-light rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-8 h-8 text-success" />
            </div>
            
            <h2 className="text-2xl font-bold text-text-primary mb-4">Password Reset Successful</h2>
            <p className="text-text-secondary mb-6 leading-relaxed">
              Your password has been successfully updated. You can now sign in with your new password.
            </p>

            <button
              onClick={onBackToLogin}
              className="w-full bg-gradient-to-r from-primary to-secondary text-background py-3 px-4 rounded-xl font-semibold hover:from-secondary hover:to-primary transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              Continue to Sign In
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-light via-secondary-light to-accent-light flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-2xl mb-4 shadow-lg">
            <Plane className="w-8 h-8 text-background" />
          </div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">TravelStyle AI</h1>
          <p className="text-text-secondary">Your personal travel style assistant</p>
        </div>

        {/* Reset Password Form */}
        <div className="bg-surface rounded-2xl shadow-xl p-8 border border-border">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-text-primary mb-2">Reset Your Password</h2>
            <p className="text-text-secondary">
              Enter your new password below to complete the reset process.
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-error-light border border-error rounded-lg">
              <p className="text-sm text-error">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* New Password Field */}
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-text-primary mb-2">
                New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
                <input
                  id="newPassword"
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter your new password"
                  className="w-full pl-10 pr-12 py-3 border border-border bg-background text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 placeholder-text-secondary"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors duration-300"
                >
                  {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-text-primary mb-2">
                Confirm New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your new password"
                  className="w-full pl-10 pr-12 py-3 border border-border bg-background text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 placeholder-text-secondary"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors duration-300"
                >
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Password Requirements */}
            <div className="bg-accent-light border border-accent rounded-lg p-3">
              <p className="text-xs text-accent">
                <strong>Password Requirements:</strong> At least 6 characters long
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !newPassword || !confirmPassword || newPassword !== confirmPassword}
              className="w-full bg-gradient-to-r from-primary to-secondary text-background py-3 px-4 rounded-xl font-semibold hover:from-secondary hover:to-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Updating Password...
                </>
              ) : (
                'Update Password'
              )}
            </button>
          </form>

          {/* Help Text */}
          <div className="mt-6 text-center">
            <p className="text-sm text-text-secondary">
              Remember your password?
              <button
                onClick={onBackToLogin}
                className="ml-2 text-secondary hover:text-primary font-semibold transition-colors duration-300"
              >
                Sign In
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordScreen;