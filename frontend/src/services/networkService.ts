import { fetchConfig, API_URL } from '@/lib/api';
import { NetworkDevice } from '@/types';

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

  getNetworkMap: async () => {
    const response = await fetch(`${API_URL}/network/map`, {
      ...fetchConfig
    });
    
    if (!response.ok) throw new Error('Failed to get network map');
    return response.json();
  }
}; 