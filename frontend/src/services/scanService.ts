import { scanApi } from './api';

// Base API URL - would come from environment variables in a real app
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.nexasec.rw';

export interface ScanConfig {
  networkTarget: string;
  outputDirectory: string;
  scanType: 'basic' | 'full';
  customPasswordList?: File;
  useCustomPasswordList: boolean;
}

export interface ScanResult {
  id: string;
  timestamp: string;
  networkTarget: string;
  scanType: 'basic' | 'full';
  status: 'in_progress' | 'completed' | 'failed';
  progress: number;
  services: {
    name: string;
    port: number;
    version: string;
    vulnerabilities?: string[];
  }[];
  weakCredentials?: {
    service: string;
    host: string;
    port: number;
    username: string;
    password: string;
  }[];
  vulnerabilities?: {
    host: string;
    service: string;
    cve?: string;
    description: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    exploitAvailable: boolean;
  }[];
  logs: string[];
}

export const startNetworkScan = scanApi.startScan;
export const getScanStatus = scanApi.getScanStatus;
export const getScanResults = scanApi.getScanResults;
export const searchScanResults = scanApi.searchScanResults;
export const downloadScanResults = scanApi.downloadScanResults; 