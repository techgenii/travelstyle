import React, { useState } from 'react';
import { Plane, Mail, ArrowLeft, Loader2, CheckCircle } from 'lucide-react';

interface ForgotPasswordScreenProps {
  onSendPasswordResetEmail: (email: string) => Promise<void>;
  onBackToLogin: () => void;
  isLoading: boolean;
}

const ForgotPasswordScreen: React.FC<ForgotPasswordScreenProps> = ({ 
  onSendPasswordResetEmail, 
  onBackToLogin, 
  isLoading 
}) => {
  const [email, setEmail] = useState('');
  const [emailSent, setEmailSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    try {
      setError('');
      await onSendPasswordResetEmail(email);
      setEmailSent(true);
    } catch (err) {
      setError('Failed to send reset email. Please try again.');
    }
  };

  if (emailSent) {
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
            
            <h2 className="text-2xl font-bold text-text-primary mb-4">Check Your Email</h2>
            <p className="text-text-secondary mb-6 leading-relaxed">
              We've sent a password reset link to <strong className="text-text-primary">{email}</strong>. 
              Click the link in the email to reset your password.
            </p>
            
            <div className="bg-secondary-light border border-secondary rounded-lg p-4 mb-6">
              <p className="text-sm text-secondary">
                <strong>Didn't receive the email?</strong> Check your spam folder or try again with a different email address.
              </p>
            </div>

            <button
              onClick={onBackToLogin}
              className="w-full bg-gradient-to-r from-primary to-secondary text-background py-3 px-4 rounded-xl font-semibold hover:from-secondary hover:to-primary transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              Back to Sign In
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

        {/* Forgot Password Form */}
        <div className="bg-surface rounded-2xl shadow-xl p-8 border border-border">
          <div className="mb-6">
            <button
              onClick={onBackToLogin}
              className="flex items-center space-x-2 text-text-secondary hover:text-text-primary transition-colors duration-300 mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back to Sign In</span>
            </button>
            
            <h2 className="text-2xl font-bold text-text-primary mb-2">Forgot Password?</h2>
            <p className="text-text-secondary">
              Enter your email address and we'll send you a link to reset your password.
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-error-light border border-error rounded-lg">
              <p className="text-sm text-error">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full pl-10 pr-4 py-3 border border-border bg-background text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 placeholder-text-secondary"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !email.trim()}
              className="w-full bg-gradient-to-r from-primary to-secondary text-background py-3 px-4 rounded-xl font-semibold hover:from-secondary hover:to-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Sending Reset Link...
                </>
              ) : (
                'Send Reset Link'
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

export default ForgotPasswordScreen;