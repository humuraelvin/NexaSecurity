"use client"
import { useState, useEffect } from "react";
import { toast } from "react-hot-toast";
import FilterTabs from "@/components/dashboard/FilterTabs";
import SearchBar from "@/components/dashboard/SearchBar";
import ActionButtons from "@/components/dashboard/ActionButtons";
import SummaryCards from "@/components/dashboard/SummaryCards";
// import DataFetcher from "@/components/dashboard/DataFetcher";
// import { Network, Shield, AlertTriangle } from "lucide-react";
// import api2 from "@/lib/api";
import { scanService } from "@/services/scanService";
import { networkApi, NetworkMap } from "@/services/networkService";
import NetworkGraph from '@/components/NetworkGraph';
import LoadingSpinner from '@/components/LoadingSpinner';
import * as api from "@/services/api";

interface NetworkDevice {
  id: string;
  name: string;
  ip: string;
  type: string;
  status: string;
  lastSeen: string;
  vulnerabilities: number;
}

interface NetworkScan {
  id: string;
  timestamp: string;
  duration: string;
  devicesScanned: number;
  vulnerabilitiesFound: number;
  status: 'completed' | 'in_progress' | 'failed';
}

export default function NetworkPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [searchQuery, setSearchQuery] = useState("");
  const [devices, setDevices] = useState<NetworkDevice[]>([]);
  const [filteredDevices, setFilteredDevices] = useState<NetworkDevice[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanHistory, setScanHistory] = useState<NetworkScan[]>([]);
  const [networkData, setNetworkData] = useState<NetworkMap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Try to fetch network map
        let networkMap;
        try {
          networkMap = await networkApi.getNetworkMap();
        } catch (err) {
          console.error('Error fetching network map:', err);
          // Provide fallback data
          networkMap = {
            nodes: [
              { id: '1', name: 'Router', type: 'device', status: 'online', ip: '192.168.1.1' },
              { id: '2', name: 'Server', type: 'host', status: 'online', ip: '192.168.1.2' }
            ],
            connections: [{ 
              source: '1', 
              target: '2', 
              type: 'direct' as 'direct' // Force TypeScript to use the literal type
            }]
          };
        }
        
        // Try to fetch scan history
        let scanHistoryData;
        try {
          scanHistoryData = await scanService.getAllScans();
        } catch (err) {
          console.error('Error fetching scan history:', err);
          // Provide fallback data
          scanHistoryData = [];
        }
        
        // Convert NetworkMap nodes to NetworkDevice array
        const deviceList = networkMap.nodes.map(node => ({
          id: node.id,
          name: node.name,
          ip: node.ip || '',
          type: node.type,
          status: node.status,
          lastSeen: new Date().toISOString(),
          vulnerabilities: 0
        }));
        
        setDevices(deviceList);
        setFilteredDevices(deviceList);
        setScanHistory(scanHistoryData);
        setNetworkData(networkMap);
        setError(null);
      } catch (err) {
        setError('Failed to load network data');
        console.error('Error loading network data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  useEffect(() => {
    let filtered = devices;
    
    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(device => 
        device.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        device.ip.includes(searchQuery)
      );
    }
    
    // Apply tab filter
    if (activeTab !== "overview") {
      if (activeTab === "online") {
        filtered = filtered.filter(device => device.status === "online");
      } else if (activeTab === "offline") {
        filtered = filtered.filter(device => device.status === "offline");
      } else if (activeTab === "vulnerable") {
        filtered = filtered.filter(device => device.vulnerabilities > 0);
      }
    }
    
    setFilteredDevices(filtered);
  }, [searchQuery, activeTab, devices]);

  const handleRunScan = async () => {
    try {
      setIsScanning(true);
      toast.loading("Network scan in progress...");
      
      // Start a new scan
      const scan = await scanService.startScan({
        networkTarget: 'all',
        outputDirectory: 'network_scan',
        scanType: 'network',
        useCustomPasswordList: false
      });

      // Poll for scan completion
      const pollInterval = setInterval(async () => {
        const status = await scanService.getScanStatus(scan.scanId);
        if (status.status === 'completed') {
          clearInterval(pollInterval);
          setIsScanning(false);
          toast.dismiss();
          toast.success("Network scan completed");
          
          // Refresh data
          const [newMap, newHistory] = await Promise.all([
            networkApi.getNetworkMap(),
            scanService.getAllScans()
          ]);

          // Convert NetworkMap nodes to NetworkDevice array
          const newDeviceList = newMap.nodes.map(node => ({
            id: node.id,
            name: node.name,
            ip: node.ip || '',
            type: node.type,
            status: node.status,
            lastSeen: new Date().toISOString(),
            vulnerabilities: 0
          }));

          setDevices(newDeviceList);
          setScanHistory(newHistory);
          setNetworkData(newMap);
        }
      }, 2000);

    } catch (error) {
      console.error('Error running network scan:', error);
      setIsScanning(false);
      toast.dismiss();
      toast.error('Failed to run network scan');
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h1 className="text-2xl font-bold mb-2 md:mb-0">Network Security</h1>
        <ActionButtons 
          primaryAction={{
            label: isScanning ? "Scanning..." : "Run Network Scan",
            onClick: handleRunScan
          }}
        />
      </div>

      {/* Network Summary */}
      <div className="mb-6">
        <SummaryCards 
          items={[
            {
              title: "Total Devices",
              count: devices.length,
              description: "Devices on network",
              color: "blue"
            },
            {
              title: "Online Devices",
              count: devices.filter(d => d.status === "online").length,
              description: "Currently active",
              color: "green"
            },
            {
              title: "Vulnerable Devices",
              count: devices.filter(d => d.vulnerabilities > 0).length,
              description: "Require attention",
              color: "red"
            }
          ]}
        />
      </div>

      {/* Tabs and Search */}
      <div className="mb-4">
        <FilterTabs 
          tabs={[
            { id: "overview", label: "Overview" },
            { id: "online", label: "Online" },
            { id: "offline", label: "Offline" },
            { id: "vulnerable", label: "Vulnerable" }
          ]}
          activeTab={activeTab}
          onChange={setActiveTab}
        />
      </div>
      
      <div className="mb-6">
        <SearchBar 
          placeholder="Search devices by name or IP..."
          value={searchQuery}
          onChange={setSearchQuery}
        />
      </div>

      {/* Devices Table */}
      <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800/60 rounded-lg overflow-hidden mb-8">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-800">
            <thead className="bg-gray-800/50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Device
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  IP Address
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Last Seen
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Vulnerabilities
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {filteredDevices.map((device) => (
                <tr key={device.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {device.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                    {device.ip}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                    {device.type.charAt(0).toUpperCase() + device.type.slice(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      device.status === 'online' ? "bg-green-900/30 text-green-400" : 
                      "bg-red-900/30 text-red-400"
                    }`}>
                      {device.status.charAt(0).toUpperCase() + device.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                    {device.lastSeen}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`${
                      device.vulnerabilities > 0 ? "text-red-400" : "text-green-400"
                    }`}>
                      {device.vulnerabilities}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Scan History */}
      <div>
        <h2 className="text-xl font-medium mb-4">Scan History</h2>
        <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800/60 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-800">
              <thead className="bg-gray-800/50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Date & Time
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Duration
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Devices Scanned
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Vulnerabilities
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {scanHistory.map((scan) => (
                  <tr key={scan.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {scan.timestamp}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {scan.duration}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {scan.devicesScanned}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`${
                        scan.vulnerabilitiesFound > 0 ? "text-red-400" : "text-green-400"
                      }`}>
                        {scan.vulnerabilitiesFound}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        scan.status === 'completed' ? "bg-green-900/30 text-green-400" : 
                        scan.status === 'in_progress' ? "bg-blue-900/30 text-blue-400" :
                        "bg-red-900/30 text-red-400"
                      }`}>
                        {scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {networkData && networkData.nodes.length > 0 ? (
        <NetworkGraph data={networkData} />
      ) : (
        <div className="text-center text-gray-500">
          No network data available. Start a scan to map your network.
        </div>
      )}
    </div>
  );
} 