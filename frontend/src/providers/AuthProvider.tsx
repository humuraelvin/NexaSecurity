"use client"
import { createContext, useContext, ReactNode, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter, usePathname } from 'next/navigation';
import CyberLoader from '@/components/ui/CyberLoader';
import { authApi } from '@/services/api';

interface User {
  id?: string;
  email: string;
  full_name?: string;
  company_name?: string;
  subscription_tier?: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  signup: (email: string, password: string, name: string, company?: string, plan?: string | null) => Promise<any>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { 
    user, 
    setUser,
    isAuthenticated, 
    setIsAuthenticated,
    isLoadingUser 
  } = useAuth();
  
  const router = useRouter();
  const pathname = usePathname();
  
  // Protected routes that require authentication
  const protectedRoutes = [
    '/dashboard',
    '/profile',
    '/security',
    '/subscriptions',
    '/settings'
  ];

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      
      if (!token || !storedUser) {
        if (protectedRoutes.some(route => pathname?.startsWith(route))) {
          router.push('/auth/login');
        }
        return;
      }

      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (e) {
        console.error('Error parsing stored user data:', e);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        if (protectedRoutes.some(route => pathname?.startsWith(route))) {
          router.push('/auth/login');
        }
      }
    };

    if (!isLoadingUser) {
      checkAuth();
    }
  }, [isLoadingUser, pathname, router, setUser, setIsAuthenticated]);

  // Simplified login function
  const login = async (credentials: { email: string; password: string }) => {
    try {
      const response = await authApi.login(credentials);
      
      if (response.access_token) {
        localStorage.setItem('token', response.access_token);
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
        }
        
        // Create user data object from response
        const userData: User = {
          email: credentials.email,
          is_active: true,
          // Add any additional user data from the response
          ...(response.user || {})
        };
        
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        setIsAuthenticated(true);
        
        // Use replace instead of push to prevent back navigation to login
        router.replace('/dashboard');
      }
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  };

  // Simplified signup function
  const signup = async (
    email: string, 
    password: string, 
    name: string, 
    company?: string,
    plan?: string | null
  ) => {
    try {
      const signupData = await authApi.signup({
        email,
        password,
        name,
        company,
        plan: plan || "basic"
      });
      
      // After successful signup, log the user in
      await login({ email, password });
      
      return signupData;
    } catch (error) {
      console.error("Signup error:", error);
      throw error;
    }
  };
  
  // Simplified logout function
  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Always clear local state
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      setUser(null);
      setIsAuthenticated(false);
      router.replace('/');
    }
  };
  
  // Show loading state while checking authentication
  if (isLoadingUser) {
    return <CyberLoader text="Initializing secure environment..." />;
  }
  
  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading: isLoadingUser,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
} 