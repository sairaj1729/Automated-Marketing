import { useState, useEffect } from 'react';

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    const token = localStorage.getItem('token');
    return {
      token,
      isAuthenticated: !!token,
    };
  });

  // Listen for storage changes across tabs
  useEffect(() => {
    const handleStorageChange = () => {
      const token = localStorage.getItem('token');
      setAuthState({
        token,
        isAuthenticated: !!token,
      });
    };

    // Listen for storage events to update auth state across tabs
    window.addEventListener('storage', handleStorageChange);
    
    // Also check periodically in case storage changes without event
    const interval = setInterval(() => {
      const currentToken = localStorage.getItem('token');
      if (currentToken !== authState.token) {
        setAuthState({
          token: currentToken,
          isAuthenticated: !!currentToken,
        });
      }
    }, 1000); // Check every second

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [authState.token]);

  const login = (token: string) => {
    localStorage.setItem('token', token);
    setAuthState({
      token,
      isAuthenticated: true,
    });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setAuthState({
      token: null,
      isAuthenticated: false,
    });
  };

  return {
    ...authState,
    login,
    logout,
  };
};