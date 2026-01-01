import { useState, useEffect } from "react";

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user has a valid token in localStorage
    const token = localStorage.getItem("token");
    
    if (token) {
      // In a real implementation, you would verify the token with your backend
      // For now, we'll just check if it exists
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
    
    setIsLoading(false);
  }, []);

  return { isAuthenticated, isLoading };
};