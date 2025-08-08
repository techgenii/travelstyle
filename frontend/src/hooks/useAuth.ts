import { useState, useCallback } from 'react';
import { User, AuthState } from '../types';

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    isLoading: false
  });

  const login = useCallback(async (email: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock user data - in a real app, this would come from your auth service
      const user: User = {
        id: '1',
        name: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1),
        firstName: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1),
        lastName: 'Doe',
        email: email,
        avatar: undefined,
        defaultWeatherLocation: 'Los Angeles, CA',
        styles: ['Business Casual', 'Casual', 'Minimalist'],
        travelPatterns: ['Business', 'Leisure', 'Solo'],
        packingMethods: ['5-4-3-2-1 Method'],
        currencies: ['USD', 'EUR', 'GBP'],
        shirtSize: 'XL',
        pantSize: '16, XL',
        shoeSize: '10.0',
        dressSize: '16',
        skirtSize: '16',
        bathingSuitSize: 'XL'
      };

      setAuthState({
        isAuthenticated: true,
        user,
        isLoading: false
      });
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, []);

  const sendPasswordResetEmail = useCallback(async (email: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    
    try {
      // Simulate API call to Supabase
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In a real app, this would call:
      // await supabase.auth.resetPasswordForEmail(email, {
      //   redirectTo: `${window.location.origin}/reset-password`,
      // });
      
      setAuthState(prev => ({ ...prev, isLoading: false }));
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, []);

  const resetPassword = useCallback(async (accessToken: string, newPassword: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    
    try {
      // Simulate API call to Supabase
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // In a real app, this would call:
      // await supabase.auth.updateUser({
      //   password: newPassword
      // });
      
      setAuthState(prev => ({ ...prev, isLoading: false }));
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, []);
  const logout = useCallback(() => {
    setAuthState({
      isAuthenticated: false,
      user: null,
      isLoading: false
    });
  }, []);

  return {
    ...authState,
    login,
    sendPasswordResetEmail,
    resetPassword,
    logout
  };
};