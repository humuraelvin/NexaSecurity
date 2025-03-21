/**
 * API Integration Utilities for NexaSecurity Tools
 *
 * This file contains utilities for managing API interactions across
 * security tools, including API key management, error handling, and
 * response normalization.
 */

// Common function to mask API keys in logs for security
export const maskApiKey = (apiKey: string): string => {
  if (!apiKey || apiKey.length < 4) return "***";
  return `${apiKey.substring(0, 3)}${"*".repeat(apiKey.length - 3)}`;
};

// Generic API error handler with custom error types
export class ApiError extends Error {
  statusCode?: number;
  errorType: string;

  constructor(
    message: string,
    errorType: string = "API_ERROR",
    statusCode?: number
  ) {
    super(message);
    this.name = "ApiError";
    this.errorType = errorType;
    this.statusCode = statusCode;
  }
}

// Error handling for common API issues
export const handleApiError = (error: unknown): never => {
  if (error instanceof ApiError) {
    throw error;
  }

  if (error instanceof Error) {
    throw new ApiError(
      `API request failed: ${error.message}`,
      "UNEXPECTED_ERROR"
    );
  }

  throw new ApiError("Unknown API error occurred", "UNKNOWN_ERROR");
};

// Standardized API request function with error handling
export const makeApiRequest = async <T>(
  url: string,
  options: RequestInit = {},
  errorContext: string = "API"
): Promise<T> => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new ApiError(
        `${errorContext} API error: ${
          errorData?.message || response.statusText
        }`,
        "REQUEST_FAILED",
        response.status
      );
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof Error) {
      throw new ApiError(`${errorContext} request failed: ${error.message}`);
    }
    throw new ApiError(`Unknown error during ${errorContext} request`);
  }
};

// Simulate API responses for development/demo purposes
export const simulateApiResponse = <T>(
  mockData: T,
  options: {
    delay?: number;
    errorRate?: number;
    errorMessage?: string;
  } = {}
): Promise<T> => {
  const {
    delay = 500,
    errorRate = 0,
    errorMessage = "Simulated API error",
  } = options;

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Randomly fail based on errorRate (0-1)
      if (Math.random() < errorRate) {
        reject(new ApiError(errorMessage, "SIMULATED_ERROR"));
        return;
      }
      resolve(mockData);
    }, delay);
  });
};

// Utility to check if we're in development/test mode
export const isDevelopmentMode = (): boolean => {
  return (
    process.env.NODE_ENV === "development" ||
    process.env.NEXT_PUBLIC_API_SIMULATION === "true"
  );
};

// Safely get API keys from environment with fallbacks for development
export const getApiKey = (keyName: string, fallback: string = ""): string => {
  const key = process.env[keyName];
  if (!key && !isDevelopmentMode()) {
    console.warn(`Missing ${keyName} environment variable in production mode`);
  }
  return key || fallback;
};
