import { Report } from "@/types";
import { mockReports } from "@/utils/mockData";

// Base API URL - would come from environment variables in a real app
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.nexasec.rw';

// Fetch all reports
export const fetchReports = async (): Promise<Report[]> => {
  try {
    // In a real app, this would be an API call
    // For now, return mock data
    return [
      {
        id: "1",
        title: "Network Security Assessment",
        date: "2023-12-15",
        type: "security",
        status: "completed",
        summary: "Comprehensive analysis of network vulnerabilities"
      },
      {
        id: "2",
        title: "Web Application Penetration Test",
        date: "2023-11-28",
        type: "pentest",
        status: "completed",
        summary: "Detailed testing of web application security"
      },
      {
        id: "3",
        title: "Monthly Security Scan",
        date: "2024-01-05",
        type: "scan",
        status: "completed",
        summary: "Regular security scan of all systems"
      }
    ];
  } catch (error) {
    console.error("Error fetching reports:", error);
    throw error;
  }
};

// Generate a new report
export const generateReport = async (options: {
  type: string;
  target?: string;
  includeRemediation?: boolean;
}): Promise<Report> => {
  try {
    // In a real app, this would be an API call
    // For now, return a mock response
    return {
      id: Math.random().toString(36).substring(2, 9),
      title: `${options.type.charAt(0).toUpperCase() + options.type.slice(1)} Report`,
      date: new Date().toISOString().split('T')[0],
      type: options.type,
      status: "completed",
      summary: `Generated ${options.type} report${options.target ? ` for ${options.target}` : ''}`
    };
  } catch (error) {
    console.error("Error generating report:", error);
    throw error;
  }
};

export async function getReportDetails(id: string): Promise<Report> {
  try {
    const response = await fetch(`${API_URL}/api/reports/${id}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch report details');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching report details:', error);
    // Return a mock report as fallback
    const report = mockReports.find(r => r.id === id) || mockReports[0];
    return report;
  }
}

export async function downloadReport(id: string): Promise<Blob> {
  try {
    const response = await fetch(`${API_URL}/api/reports/${id}/download`);
    
    if (!response.ok) {
      throw new Error('Failed to download report');
    }
    
    return await response.blob();
  } catch (error) {
    console.error('Error downloading report:', error);
    throw error;
  }
} 