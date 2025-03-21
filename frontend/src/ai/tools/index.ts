// Import AI tools
import { weatherTool } from "./weatherTool";
import { networkScanTool } from "./networkScanTool";
import { vulnerabilityScanTool } from "./vulnerabilityScanTool";
import { trafficAnalysisTool } from "./trafficAnalysisTool";
import { passwordCheckTool } from "./passwordCheckTool";
import { pentestTool } from "./pentestTool";

// Import types
import type {
  AiTool,
  WeatherParams,
  WeatherResult,
  NetworkScanParams,
  NetworkScanResult,
  VulnerabilityScanParams,
  VulnerabilityScanResult,
  TrafficAnalysisParams,
  TrafficAnalysisResult,
  PasswordCheckParams,
  PasswordCheckResult,
  PasswordStrengthResult,
  PasswordBreachResult,
  PentestParams,
  PentestResult,
  PentestType,
  PentestDepth,
  PentestOptions,
} from "./types";

// Export all AI tools
export const aiTools = {
  weatherTool,
  networkScanTool,
  vulnerabilityScanTool,
  trafficAnalysisTool,
  passwordCheckTool,
  pentestTool,
};

// Export all tool types
export type {
  AiTool,
  WeatherParams,
  WeatherResult,
  NetworkScanParams,
  NetworkScanResult,
  VulnerabilityScanParams,
  VulnerabilityScanResult,
  TrafficAnalysisParams,
  TrafficAnalysisResult,
  PasswordCheckParams,
  PasswordCheckResult,
  PasswordStrengthResult,
  PasswordBreachResult,
  PentestParams,
  PentestResult,
  PentestType,
  PentestDepth,
  PentestOptions,
};
