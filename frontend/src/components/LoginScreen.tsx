import React, { useState } from 'react';
import { Plane, Mail, Lock, Eye, EyeOff, Loader2, User } from 'lucide-react';

interface LoginScreenProps {
  onLogin: (email: string, password: string) => Promise<void>;
  onForgotPassword: () => void;
  isLoading: boolean;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ onLogin, onForgotPassword, isLoading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (email && password && (!isSignUp || name)) {
      await onLogin(email, password);
    }
  };

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

        {/* Login Form */}
        <div className="bg-surface rounded-2xl shadow-xl p-8 border border-border">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-text-primary mb-2">
              {isSignUp ? 'Create Account' : 'Welcome Back'}
            </h2>
            <p className="text-text-secondary">
              {isSignUp 
                ? 'Start your stylish travel journey' 
                : 'Sign in to continue your travel planning'
              }
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name Field - Only for Sign Up */}
            {isSignUp && (
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-text-primary mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your full name"
                    className="w-full pl-10 pr-4 py-3 border border-border bg-background text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 placeholder-text-secondary"
                    required={isSignUp}
                  />
                </div>
              </div>
            )}

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

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full pl-10 pr-12 py-3 border border-border bg-background text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 placeholder-text-secondary"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors duration-300"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !email || !password || (isSignUp && !name)}
              className="w-full bg-gradient-to-r from-primary to-secondary text-background py-3 px-4 rounded-xl font-semibold hover:from-secondary hover:to-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  {isSignUp ? 'Creating Account...' : 'Signing In...'}
                </>
              ) : (
                isSignUp ? 'Create Account' : 'Sign In'
              )}
            </button>
          </form>

          {/* Toggle Sign Up/Sign In */}
          <div className="mt-6 text-center">
            <p className="text-text-secondary">
              {isSignUp ? 'Already have an account?' : "Don't have an account?"}
              <button
                onClick={() => setIsSignUp(!isSignUp)}
                className="ml-2 text-secondary hover:text-primary font-semibold transition-colors duration-300"
              >
                {isSignUp ? 'Sign In' : 'Sign Up'}
              </button>
            </p>
          </div>

          {/* Demo Account */}
          <div className="mt-4 p-3 bg-secondary-light rounded-lg border border-secondary">
            <p className="text-xs text-secondary text-center">
              <strong>Demo:</strong> Use any email and password to try the app
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p className="text-text-secondary">Secure • Private • Personalized Travel Styling</p>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;