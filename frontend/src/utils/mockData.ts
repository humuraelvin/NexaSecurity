import { subDays, format, addMinutes } from 'date-fns';
import { Vulnerability, SystemHealth, Alert, ThreatData } from "@/types";

// Generate random number between min and max
const random = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1) + min);

// Generate random IP address
const generateIP = () => {
  return `${random(1, 255)}.${random(1, 255)}.${random(1, 255)}.${random(1, 255)}`;
};

// Generate threat data for the line chart
export const generateThreatData = (days: number = 7) => {
  const data = [];
  const now = new Date();
  
  for (let i = days - 1; i >= 0; i--) {
    const date = subDays(now, i);
    for (let hour = 0; hour < 24; hour++) {
      data.push({
        timestamp: addMinutes(date, hour * 60),
        threats: random(50, 500)
      });
    }
  }
  
  return data;
};

// Generate alerts data
export const generateAlerts = (count: number = 10) => {
  const types = ['Unauthorized access attempt', 'Malware detected', 'Suspicious activity', 'Port scan detected', 'DDoS attempt'];
  const statuses = ['low', 'moderate', 'high'];
  const amounts = ['High level system scanning', 'Data exfiltration attempt', 'Brute force attack', 'SQL injection attempt'];
  
  return Array.from({ length: count }, () => ({
    id: Math.random().toString(36).substr(2, 9),
    type: types[random(0, types.length - 1)],
    date: format(subDays(new Date(), random(0, 30)), 'MMM dd, yyyy'),
    ip: generateIP(),
    status: statuses[random(0, statuses.length - 1)],
    amount: amounts[random(0, amounts.length - 1)]
  }));
};

// Generate network devices data
export const generateNetworkDevices = (count: number = 5) => {
  const deviceTypes = ['Workstation', 'Server', 'Router', 'Mobile Device', 'IoT Device'];
  const activities = ['File transfer', 'Authentication', 'Port scan', 'DNS lookup', 'API access'];
  const statuses = ['active', 'warning', 'blocked'];
  
  return Array.from({ length: count }, (_, index) => ({
    id: Math.random().toString(36).substr(2, 9),
    type: deviceTypes[index % deviceTypes.length],
    ip: generateIP(),
    activity: activities[random(0, activities.length - 1)],
    lastSeen: new Date(Date.now() - random(0, 60) * 60000).toISOString(),
    status: statuses[random(0, statuses.length - 1)]
  }));
};

// Generate system health metrics
export const generateSystemHealth = () => {
  return {
    totalThreats: {
      percentage: random(70, 90),
      count: random(100, 150)
    },
    defeatedThreats: {
      percentage: random(60, 80),
      count: random(80, 120)
    },
    systemHealth: {
      percentage: random(75, 95),
      status: 'Good health!'
    }
  };
};

// Generate vulnerability data
export const generateVulnerabilities = (count: number = 5) => {
  const severities = ['critical', 'high', 'medium', 'low'];
  const statuses = ['open', 'in_progress', 'resolved'];
  const components = ['Web Server', 'Database', 'Authentication Service', 'API Gateway', 'Admin Dashboard'];
  
  return Array.from({ length: count }, () => ({
    id: `CVE-${new Date().getFullYear()}-${random(1000, 9999)}`,
    name: `Vulnerability ${random(1000, 9999)}`,
    description: `Security vulnerability in ${components[random(0, components.length - 1)]}`,
    severity: severities[random(0, severities.length - 1)],
    status: statuses[random(0, statuses.length - 1)],
    affected: components[random(0, components.length - 1)],
    discovered: format(subDays(new Date(), random(0, 60)), 'yyyy-MM-dd')
  }));
};

// Generate network traffic data
export const generateNetworkTraffic = (hours: number = 24) => {
  return Array.from({ length: hours }, (_, index) => ({
    timestamp: subDays(new Date(), index),
    inbound: random(100, 1000),
    outbound: random(100, 1000),
    blocked: random(10, 100)
  }));
};

// New mock data for vulnerabilities
export const mockVulnerabilities: Vulnerability[] = [
  {
    id: "VUL-2023-001",
    name: "SQL Injection Vulnerability",
    severity: "high",
    status: "open",
    affected: "Web Application Server",
    discovered: "2023-11-15",
    description: "SQL injection vulnerability in login form allows unauthorized database access."
  },
  {
    id: "VUL-2023-002",
    name: "Outdated SSL Certificate",
    severity: "medium",
    status: "in_progress",
    affected: "API Gateway",
    discovered: "2023-11-18",
    description: "SSL certificate is using outdated encryption standards."
  },
  {
    id: "VUL-2023-003",
    name: "Weak Password Policy",
    severity: "medium",
    status: "open",
    affected: "User Authentication System",
    discovered: "2023-11-20",
    description: "Password policy does not enforce sufficient complexity requirements."
  },
  {
    id: "VUL-2023-004",
    name: "Unpatched Operating System",
    severity: "high",
    status: "open",
    affected: "Database Server",
    discovered: "2023-11-22",
    description: "Critical security patches missing from production database server."
  },
  {
    id: "VUL-2023-005",
    name: "Cross-Site Scripting (XSS)",
    severity: "medium",
    status: "in_progress",
    affected: "Customer Portal",
    discovered: "2023-11-25",
    description: "XSS vulnerability in comment section allows injection of malicious scripts."
  },
  {
    id: "VUL-2023-006",
    name: "Insecure File Permissions",
    severity: "low",
    status: "resolved",
    affected: "File Server",
    discovered: "2023-11-10",
    description: "Excessive permissions on configuration files allow unauthorized modifications."
  },
  {
    id: "VUL-2023-007",
    name: "Default Admin Credentials",
    severity: "critical",
    status: "open",
    affected: "Network Router",
    discovered: "2023-11-28",
    description: "Network equipment using default administrator credentials."
  },
  {
    id: "VUL-2023-008",
    name: "Exposed API Keys",
    severity: "high",
    status: "resolved",
    affected: "Mobile Application",
    discovered: "2023-11-05",
    description: "API keys hardcoded in mobile application source code."
  },
  {
    id: "VUL-2023-009",
    name: "Missing Data Encryption",
    severity: "high",
    status: "in_progress",
    affected: "Customer Database",
    discovered: "2023-11-17",
    description: "Sensitive customer data stored without encryption at rest."
  },
  {
    id: "VUL-2023-010",
    name: "Denial of Service Vulnerability",
    severity: "medium",
    status: "open",
    affected: "Load Balancer",
    discovered: "2023-11-26",
    description: "Resource exhaustion vulnerability could allow DoS attacks."
  }
];

// Mock data for network devices
export const mockNetworkDevices = [
  {
    id: "DEV-001",
    name: "Main Router",
    ip: "192.168.1.1",
    type: "Router",
    status: "online",
    lastSeen: new Date().toISOString(),
    vulnerabilities: 2,
    manufacturer: "Cisco"
  },
  {
    id: "DEV-002",
    name: "Web Server",
    ip: "192.168.1.10",
    type: "Server",
    status: "online",
    lastSeen: new Date().toISOString(),
    vulnerabilities: 3,
    manufacturer: "Dell"
  },
  {
    id: "DEV-003",
    name: "Database Server",
    ip: "192.168.1.11",
    type: "Server",
    status: "online",
    lastSeen: new Date().toISOString(),
    vulnerabilities: 1,
    manufacturer: "HP"
  },
  {
    id: "DEV-004",
    name: "CEO Laptop",
    ip: "192.168.1.50",
    type: "Workstation",
    status: "offline",
    lastSeen: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    vulnerabilities: 0,
    manufacturer: "Lenovo"
  },
  {
    id: "DEV-005",
    name: "Office Printer",
    ip: "192.168.1.30",
    type: "IoT",
    status: "online",
    lastSeen: new Date().toISOString(),
    vulnerabilities: 4,
    manufacturer: "HP"
  }
];

// Mock data for reports
export const mockReports = [
  {
    id: "RPT-2023-001",
    title: "Monthly Security Assessment",
    date: "2023-11-01",
    type: "scheduled",
    status: "completed",
    summary: "Overall security posture is good with minor improvements needed.",
    findings: 12,
    criticalFindings: 1
  },
  {
    id: "RPT-2023-002",
    title: "Penetration Test Results",
    date: "2023-11-15",
    type: "manual",
    status: "completed",
    summary: "Several vulnerabilities identified in the web application.",
    findings: 8,
    criticalFindings: 2
  },
  {
    id: "RPT-2023-003",
    title: "Compliance Audit",
    date: "2023-11-20",
    type: "compliance",
    status: "in_progress",
    summary: "Evaluating alignment with ISO 27001 standards.",
    findings: null,
    criticalFindings: null
  }
]; 