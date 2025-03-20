import { fetchConfig, API_URL } from '@/lib/api';
import { ScanResult } from '@/types';

export interface ScanConfig {
  networkTarget: string;
  outputDirectory: string;
  scanType: 'basic' | 'full';
  customPasswordList?: File;
  useCustomPasswordList: boolean;
}

export const scanApi = {
  startScan: async (config: any) => {
    const response = await fetch(`${API_URL}/scans/start`, {
      method: 'POST',
      ...fetchConfig,
      body: JSON.stringify(config)
    });
    
    if (!response.ok) throw new Error('Failed to start scan');
    return response.json();
  },

  getScanStatus: async (id: string) => {
    const response = await fetch(`${API_URL}/scans/${id}/status`, {
      ...fetchConfig
    });
    
    if (!response.ok) throw new Error('Failed to get scan status');
    return response.json();
  },

  getScanResults: async (id: string): Promise<ScanResult> => {
    const response = await fetch(`${API_URL}/scans/${id}/results`, {
      ...fetchConfig
    });
    
    if (!response.ok) throw new Error('Failed to get scan results');
    return response.json();
  },

  getAllScans: async (scanId?: string) => {
    const url = scanId ? `${API_URL}/scans/${scanId}` : `${API_URL}/scans`;
    const response = await fetch(url, {
      ...fetchConfig
    });
    
    if (!response.ok) throw new Error('Failed to get scans');
    return response.json();
  },

  downloadResults: async (id: string): Promise<Blob> => {
    const response = await fetch(`${API_URL}/scans/${id}/download`, {
      ...fetchConfig
    });
    
    if (!response.ok) throw new Error('Failed to download scan results');
    return response.blob();
  }
};

// Export individual functions for backward compatibility
export const startNetworkScan = scanApi.startScan;
export const getScanStatus = scanApi.getScanStatus;
export const getScanResults = scanApi.getScanResults;
export const searchScanResults = scanApi.getAllScans;
export const downloadScanResults = scanApi.downloadResults;
export type { ScanResult } from '@/types'; 