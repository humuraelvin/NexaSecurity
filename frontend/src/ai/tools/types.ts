import { z } from "zod";

// Common interfaces for tool definitions
export interface AiTool<TParams, TResult> {
  description: string;
  parameters: z.ZodType<TParams>;
  execute: (params: TParams) => Promise<TResult>;
}

// Weather Tool Types
export interface WeatherParams {
  latitude: number;
  longitude: number;
}

export interface WeatherResult {
  [key: string]: any; // Weather API response varies
}

// Network Scan Types
export interface NetworkScanParams {
  target: string;
  ports?: string;
  scanType?: "quick" | "standard" | "deep";
}

export interface NetworkScanResult {
  target: string;
  scanStarted: boolean;
  scanId: string;
  estimatedTime: string;
  message: string;
}

// Vulnerability Scan Types
export interface VulnerabilityScanParams {
  target: string;
  scanType: "cve" | "misconfig" | "full";
}

export interface VulnerabilityScanResult {
  scanStarted: boolean;
  scanId: string;
  target: string;
  scanType: string;
  message: string;
}

// Traffic Analysis Types
export interface TrafficAnalysisParams {
  pcapFile?: string;
  interface?: string;
  duration?: number;
  filter?: string;
  analysisType:
    | "security"
    | "performance"
    | "protocol"
    | "forensics"
    | "behavioral"
    | "full";
}

export interface TrafficAnalysisResult {
  analysisId: string;
  source: string;
  analysisType: string;
  startTime: string;
  estimatedDuration: string;
  status: "running" | "complete" | "failed";
  detailsMessage: string;
  message: string;
  note?: string;
  zeekScripts?: string[];
}

// Password Check Types
export interface PasswordCheckParams {
  password: string;
  checkType: "strength" | "common" | "breach";
}

export interface PasswordStrengthResult {
  checkType: string;
  password: string;
  strength: "weak" | "medium" | "strong";
  hasSpecial: boolean;
  hasNumbers: boolean;
  hasUppercase: boolean;
  recommendations: string[];
  message: string;
}

export interface PasswordBreachResult {
  checkType: string;
  password: string;
  foundInBreaches: boolean;
  lastChecked: string;
  message: string;
}

export type PasswordCheckResult = PasswordStrengthResult | PasswordBreachResult;

// Pentest Types
export type PentestType =
  | "recon"
  | "webScan"
  | "networkScan"
  | "vulnScan"
  | "bruteForce"
  | "sqlInjection"
  | "xss"
  | "fullTest";
export type PentestDepth = "light" | "medium" | "aggressive";

export interface PentestOptions {
  depth?: PentestDepth;
  timeout?: number;
  params?: Record<string, string>;
}

export interface PentestParams {
  target: string;
  testType: PentestType;
  options?: PentestOptions;
}

export interface PentestResult {
  testId: string;
  target: string;
  testType: PentestType;
  depth: PentestDepth;
  startTime: string;
  estimatedDuration: string;
  status: "running" | "complete" | "failed";
  detailsMessage: string;
  message: string;
  note?: string;
}
