import { api } from './api';
import type { ScanResult } from '@/types';
import { API_URL, fetchConfig } from '@/lib/api';

export interface ScanConfig {
  networkTarget: string;
  outputDirectory: string;
  scanType: 'network' | 'web' | 'full';
  useCustomPasswordList: boolean;
  customPasswordList?: File;
}

export const scanService = {
  startScan: async (config: ScanConfig): Promise<{ scanId: string }> => {
    try {
      // Create FormData if there's a file
      if (config.customPasswordList) {
        const formData = new FormData();
        formData.append('networkTarget', config.networkTarget);
        formData.append('outputDirectory', config.outputDirectory);
        formData.append('scanType', config.scanType);
        formData.append('useCustomPasswordList', String(config.useCustomPasswordList));
        formData.append('customPasswordList', config.customPasswordList);
        
        const response = await api.post('/scans/start', formData);
        return response;
      }
      
      // Regular JSON request without file
      const response = await api.post('/scans/start', config);
      return response;
    } catch (error) {
      console.error('Error starting scan:', error);
      throw new Error('Failed to start scan. Please try again.');
    }
  },

  getScanStatus: async (scanId: string): Promise<ScanResult> => {
    try {
      const response = await api.get(`/scans/${scanId}`);
      return response;
    } catch (error) {
      console.error('Error getting scan status:', error);
      throw new Error('Failed to get scan status');
    }
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
export const startNetworkScan = scanService.startScan;
export const getScanStatus = scanService.getScanStatus;
export const getScanResults = scanService.getScanResults;
export const searchScanResults = scanService.getAllScans;
export const downloadScanResults = scanService.downloadResults;
export type { ScanResult } from '@/types'; 