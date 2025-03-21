import { fetchConfig, API_URL } from '@/lib/api';
import { NetworkDevice } from '@/types';
import { api } from './api';

export interface NetworkNode {
  id: string;
  name: string;
  type: string;
  status: string;
  ip?: string;
}

export interface NetworkConnection {
  source: string;
  target: string;
  type: 'direct' | 'indirect';
}

export interface NetworkMap {
  nodes: NetworkNode[];
  connections: NetworkConnection[];
}

export const networkApi = {
  discoverDevices: async () => {
    const response = await fetch(`${API_URL}/network/discover`, {
      ...fetchConfig
    });
    
    if (!response.ok) throw new Error('Failed to discover devices');
    return response.json();
  },

  getDeviceDetails: async (id: string): Promise<NetworkDevice> => {
    const response = await fetch(`${API_URL}/network/devices/${id}`, {
      ...fetchConfig
    });
    
    if (!response.ok) throw new Error('Failed to get device details');
    return response.json();
  },

  getNetworkMap: async (): Promise<NetworkMap> => {
    try {
      // First try to get from cache
      const cachedData = localStorage.getItem('network_map');
      if (cachedData) {
        return JSON.parse(cachedData);
      }

      const response = await api.get('/network/map');
      
      // Cache the successful response
      if (response) {
        localStorage.setItem('network_map', JSON.stringify(response));
      }
      
      return response || { nodes: [], connections: [] };
    } catch (error) {
      console.error('Error fetching network map:', error);
      // Return empty map instead of throwing
      return {
        nodes: [],
        connections: []
      };
    }
  }
}; 