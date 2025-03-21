import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { getCookie, setCookie, deleteCookie } from 'cookies-next';
import { toast } from 'react-hot-toast';

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://nexasecurity.onrender.com/api/v1';

export const fetchConfig = {
  credentials: 'include' as RequestCredentials,
  mode: 'cors' as RequestMode,
  headers: {
    'Content-Type': 'application/json',
    ...(typeof window !== 'undefined' && localStorage.getItem('token') 
      ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } 
      : {})
  }
};
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, 
});


apiClient.interceptors.request.use(
  (config) => {
    const token = getCookie('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = getCookie('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }
        
        const response = await apiClient.post('/auth/refresh', { refreshToken });
        const { accessToken, refreshToken: newRefreshToken } = response.data;
        setCookie('auth_token', accessToken, { maxAge: 60 * 60 }); 
        setCookie('refresh_token', newRefreshToken, { maxAge: 60 * 60 * 24 * 7 }); // 1 week
        
        // Retry the original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        // If refresh fails, log out the user
        handleLogout();
        return Promise.reject(refreshError);
      }
    }
    
    // Handle other errors
    handleApiError(error);
    return Promise.reject(error);
  }
);

// Error handler
const handleApiError = (error: AxiosError) => {
  const status = error.response?.status;
  const message = 
    (error.response?.data as any)?.message || 
    error.message || 
    'An unexpected error occurred';
  
  // Show error toast
  toast.error(message);
  
  // Log error for debugging
  console.error('API Error:', {
    status,
    message,
    url: error.config?.url,
  });
};

// Logout handler
export const handleLogout = () => {
  deleteCookie('auth_token');
  deleteCookie('refresh_token');
  deleteCookie('user_data');
  
  // Redirect to login page if we're in the browser
  if (typeof window !== 'undefined') {
    window.location.href = '/auth/login';
  }
};

// Session management
export const getSession = () => {
  try {
    const userData = getCookie('user_data');
    if (!userData) return null;
    return JSON.parse(userData as string);
  } catch (error) {
    console.error('Error parsing user data:', error);
    return null;
  }
};

export const setSession = (userData: any) => {
  setCookie('user_data', JSON.stringify(userData), { maxAge: 60 * 60 * 24 * 7 }); // 1 week
};

// API endpoints
export const api = {
  // Auth endpoints
  auth: {
    login: async (email: string, password: string) => {
      const response = await apiClient.post('/auth/login', { email, password });
      const { user, accessToken, refreshToken } = response.data;
      
      // Set tokens and user data in cookies
      setCookie('auth_token', accessToken, { maxAge: 60 * 60 }); // 1 hour
      setCookie('refresh_token', refreshToken, { maxAge: 60 * 60 * 24 * 7 }); // 1 week
      setSession(user);
      
      return user;
    },
    
    signup: async (userData: any) => {
      const response = await apiClient.post('/auth/signup', userData);
      return response.data;
    },
    
    logout: () => {
      apiClient.post('/auth/logout').catch(console.error);
      handleLogout();
    },
    
    verifyEmail: async (token: string) => {
      const response = await apiClient.post('/auth/verify-email', { token });
      return response.data;
    },
    
    forgotPassword: async (email: string) => {
      const response = await apiClient.post('/auth/forgot-password', { email });
      return response.data;
    },
    
    resetPassword: async (token: string, password: string) => {
      const response = await apiClient.post('/auth/reset-password', { token, password });
      return response.data;
    },
  },
  
  // User endpoints
  user: {
    getProfile: async () => {
      const response = await apiClient.get('/user/profile');
      return response.data;
    },
    
    updateProfile: async (userData: any) => {
      const response = await apiClient.put('/user/profile', userData);
      // Update session with new user data
      setSession(response.data);
      return response.data;
    },
    
    changePassword: async (currentPassword: string, newPassword: string) => {
      const response = await apiClient.put('/user/change-password', {
        currentPassword,
        newPassword,
      });
      return response.data;
    },
  },
  
  // Subscription endpoints
  subscriptions: {
    getPlans: async () => {
      const response = await apiClient.get('/subscriptions/plans');
      return response.data;
    },
    
    getCurrentSubscription: async () => {
      const response = await apiClient.get('/subscriptions/current');
      return response.data;
    },
    
    subscribe: async (planId: string, paymentMethod: string) => {
      const response = await apiClient.post('/subscriptions/subscribe', {
        planId,
        paymentMethod,
      });
      return response.data;
    },
    
    cancelSubscription: async () => {
      const response = await apiClient.post('/subscriptions/cancel');
      return response.data;
    },
  },
  
  // Security scan endpoints
  securityScans: {
    startScan: async (target: string, scanType: string) => {
      const response = await apiClient.post('/security/scan', { target, scanType });
      return response.data;
    },
    
    getScanStatus: async (scanId: string) => {
      const response = await apiClient.get(`/security/scan/${scanId}/status`);
      return response.data;
    },
    
    getScanResults: async (scanId: string) => {
      const response = await apiClient.get(`/security/scan/${scanId}/results`);
      return response.data;
    },
    
    getScanHistory: async () => {
      const response = await apiClient.get('/security/scan/history');
      return response.data;
    },
  },
  
  // Security alerts endpoints
  securityAlerts: {
    getAlerts: async (params?: { page?: number; limit?: number; severity?: string }) => {
      const response = await apiClient.get('/security/alerts', { params });
      return response.data;
    },
    
    getAlertById: async (alertId: string) => {
      const response = await apiClient.get(`/security/alerts/${alertId}`);
      return response.data;
    },
    
    markAlertAsRead: async (alertId: string) => {
      const response = await apiClient.put(`/security/alerts/${alertId}/read`);
      return response.data;
    },
  },
  
  // Dashboard data endpoints
  dashboard: {
    getSummary: async () => {
      const response = await apiClient.get('/dashboard/summary');
      return response.data;
    },
    
    getSecurityScore: async () => {
      const response = await apiClient.get('/dashboard/security-score');
      return response.data;
    },
    
    getRecentActivity: async () => {
      const response = await apiClient.get('/dashboard/recent-activity');
      return response.data;
    },
  },
};

export default api; 