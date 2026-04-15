import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import * as APIUtility from '../utils/api';
import * as SecureStore from 'expo-secure-store';

interface User {
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const hydrate = async () => {
    setIsLoading(true);
    try {
      const accessToken = await APIUtility.getAccessToken();
      if (accessToken) {
        const response = await APIUtility.API.getMe();
        if (response.ok) {
          const data = await response.json();
          setUser(data);
        } else {
          await logout();
        }
      }
    } catch (e) {
      console.error('Hydration error:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    hydrate();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await APIUtility.API.login({ email, password });
      if (response.ok) {
        const data: APIUtility.AuthResponse = await response.json();
        await APIUtility.setTokens(data.access_token, data.refresh_token);
        
        // Fetch user info
        const meResponse = await APIUtility.API.getMe();
        if (meResponse.ok) {
          const meData = await meResponse.json();
          setUser(meData);
          return true;
        }
      } else if (response.status === 401) {
        setError('Invalid email or password');
      } else {
        const data = await response.json().catch(() => ({}));
        setError(data.message || 'An error occurred during login');
      }
      return false;
    } catch (e) {
      setError('Network error. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await APIUtility.API.register({ email, password });
      if (response.status === 201) {
        const data: APIUtility.AuthResponse = await response.json();
        await APIUtility.setTokens(data.access_token, data.refresh_token);
        
        // Fetch user info
        const meResponse = await APIUtility.API.getMe();
        if (meResponse.ok) {
          const meData = await meResponse.json();
          setUser(meData);
          return true;
        }
      } else if (response.status === 409) {
        setError('Email already exists');
      } else {
        const data = await response.json().catch(() => ({}));
        setError(data.message || 'An error occurred during registration');
      }
      return false;
    } catch (e) {
      setError('Network error. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    await APIUtility.clearTokens();
    setUser(null);
  };

  const refreshUser = async () => {
    const response = await APIUtility.API.getMe();
    if (response.ok) {
      const data = await response.json();
      setUser(data);
    }
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        register,
        logout,
        refreshUser,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
