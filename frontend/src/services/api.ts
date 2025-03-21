import axios from "axios";
import { fetchConfig, API_URL } from "@/lib/api";
import { secureStorage } from "@/lib/storage";

// Add auth token to request headers
const getAuthHeaders = () => {
  let token = "";
  if (typeof window !== "undefined") {
    token = localStorage.getItem("auth_token") || "";
  }
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  };
};

const fetchOptions = {
  credentials: "include" as RequestCredentials,
  mode: "cors" as RequestMode,
  headers: getAuthHeaders(),
};

// Helper function to handle API errors
const handleApiResponse = async (response: Response) => {
  if (!response.ok) {
    // Try to get error details from response
    let errorMessage = "An error occurred";
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || "Request failed";
    } catch (e) {
      errorMessage = `${response.status}: ${response.statusText}`;
    }
    throw new Error(errorMessage);
  }
  return response.json();
};

// Auth API endpoints
export const authApi = {
  login: async (credentials: { email: string; password: string }) => {
    try {
      console.log("Login attempt with:", credentials.email);
      const response = await fetch(`${API_URL}/auth/login/json`, {
        method: "POST",
        ...fetchOptions,
        body: JSON.stringify(credentials),
      });

      return await handleApiResponse(response);
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  },

  signup: async (userData: {
    email: string;
    password: string;
    name: string;
    company?: string;
    plan?: string;
  }) => {
    try {
      console.log("Signup attempt for:", userData.email);
      const response = await fetch(`${API_URL}/auth/signup`, {
        method: "POST",
        ...fetchOptions,
        body: JSON.stringify(userData),
      });

      return await handleApiResponse(response);
    } catch (error) {
      console.error("Signup error:", error);
      throw error;
    }
  },

  logout: async () => {
    try {
      const response = await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        ...fetchOptions,
      });

      if (!response.ok) {
        console.warn(
          "Logout request failed on server, but will proceed with local logout"
        );
      }

      // Clean up local storage even if server logout fails
      secureStorage.remove("user");
      secureStorage.remove("token");

      return true;
    } catch (error) {
      console.error("Logout error:", error);
      // Clean up local storage even if server logout fails
      secureStorage.remove("user");
      secureStorage.remove("token");
      return true; // Still consider logout successful for the client
    }
  },
};

// Scan API endpoints
export const scanApi = {
  startScan: async (scanConfig: {
    networkTarget: string;
    outputDirectory: string;
    scanType: "basic" | "full";
    customPasswordList?: File;
    useCustomPasswordList: boolean;
  }) => {
    try {
      const formData = new FormData();
      formData.append("networkTarget", scanConfig.networkTarget);
      formData.append("outputDirectory", scanConfig.outputDirectory);
      formData.append("scanType", scanConfig.scanType);
      formData.append(
        "useCustomPasswordList",
        String(scanConfig.useCustomPasswordList)
      );

      if (scanConfig.useCustomPasswordList && scanConfig.customPasswordList) {
        formData.append("customPasswordList", scanConfig.customPasswordList);
      }

      const response = await fetch(`${API_URL}/scan/start`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to start scan");
      }

      return await response.json();
    } catch (error) {
      console.error("Error starting scan:", error);
      throw error;
    }
  },

  getScanStatus: async (scanId: string) => {
    try {
      const response = await fetch(`${API_URL}/scan/${scanId}/status`);

      if (!response.ok) {
        throw new Error("Failed to get scan status");
      }

      return await response.json();
    } catch (error) {
      console.error("Error getting scan status:", error);
      throw error;
    }
  },

  getScanResults: async (scanId: string) => {
    try {
      const response = await fetch(`${API_URL}/scan/${scanId}/results`);

      if (!response.ok) {
        throw new Error("Failed to get scan results");
      }

      return await response.json();
    } catch (error) {
      console.error("Error getting scan results:", error);
      throw error;
    }
  },

  searchScanResults: async (scanId: string, query: string) => {
    try {
      const response = await fetch(
        `${API_URL}/scan/${scanId}/search?q=${encodeURIComponent(query)}`
      );

      if (!response.ok) {
        throw new Error("Failed to search scan results");
      }

      return await response.json();
    } catch (error) {
      console.error("Error searching scan results:", error);
      throw error;
    }
  },

  downloadScanResults: async (scanId: string) => {
    try {
      const response = await fetch(`${API_URL}/scan/${scanId}/download`);

      if (!response.ok) {
        throw new Error("Failed to download scan results");
      }

      return await response.blob();
    } catch (error) {
      console.error("Error downloading scan results:", error);
      throw error;
    }
  },
};

// Dashboard API endpoints
export const dashboardApi = {
  getSystemHealth: async () => {
    try {
      const response = await fetch(`${API_URL}/dashboard/system-health`, {
        ...fetchOptions,
      });

      if (!response.ok) {
        throw new Error("Failed to get system health");
      }

      return await response.json();
    } catch (error) {
      console.error("Error getting system health:", error);
      throw error;
    }
  },

  getAlerts: async (limit?: number) => {
    try {
      const url = limit
        ? `${API_URL}/dashboard/alerts?limit=${limit}`
        : `${API_URL}/dashboard/alerts`;

      const response = await fetch(url, {
        ...fetchOptions,
      });

      if (!response.ok) {
        throw new Error("Failed to get alerts");
      }

      return await response.json();
    } catch (error) {
      console.error("Error getting alerts:", error);
      throw error;
    }
  },

  getThreatData: async () => {
    try {
      const response = await fetch(`${API_URL}/dashboard/threat-data`, {
        ...fetchOptions,
      });

      if (!response.ok) {
        throw new Error("Failed to get threat data");
      }

      return await response.json();
    } catch (error) {
      console.error("Error getting threat data:", error);
      // Return empty array on error to prevent ThreatChart from crashing
      return [];
    }
  },
};

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const api = {
  setToken: (token: string) => {
    secureStorage.set("token", token);
  },

  setUser: (user: any) => {
    secureStorage.set("user", user);
  },

  getToken: () => {
    return secureStorage.get("token");
  },

  getUser: () => {
    return secureStorage.get("user");
  },

  clearAuth: () => {
    secureStorage.remove("token");
    secureStorage.remove("user");
  },

  // Original auth endpoints
  authApi,
  scanApi,
  dashboardApi,

  get: async (endpoint: string) => {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...fetchOptions,
      method: "GET",
    });

    if (!response.ok) {
      throw new Error("API request failed");
    }

    return response.json();
  },

  post: async (endpoint: string, data: any) => {
    const options = {
      ...fetchOptions,
      method: "POST",
      body: data instanceof FormData ? data : JSON.stringify(data),
    };

    if (!(data instanceof FormData)) {
      options.headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${API_URL}${endpoint}`, options);

    if (!response.ok) {
      throw new Error("API request failed");
    }

    return response.json();
  },
};
