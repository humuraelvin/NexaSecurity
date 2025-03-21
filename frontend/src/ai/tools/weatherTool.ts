import { z } from "zod";
import { AiTool, WeatherParams, WeatherResult } from "./types";

// In a real application, store API key in environment variables
const OPENWEATHER_API_KEY =
  process.env.OPENWEATHER_API_KEY || "YOUR_OPENWEATHER_API_KEY";

export const weatherTool: AiTool<WeatherParams, WeatherResult> = {
  description: "Get current weather conditions for a specific location",
  parameters: z.object({
    latitude: z.number().describe("Latitude coordinate"),
    longitude: z.number().describe("Longitude coordinate"),
  }),
  execute: async ({ latitude, longitude }) => {
    try {
      console.log(
        `[Weather] Fetching weather for coordinates: ${latitude}, ${longitude}`
      );
      console.log(
        `[Weather] Would use API key: ${OPENWEATHER_API_KEY.substring(
          0,
          3
        )}... (masked for security)`
      );

      // In a real implementation, this would call the OpenWeatherMap API:
      // const url = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${OPENWEATHER_API_KEY}&units=metric`;
      // const response = await fetch(url);
      // const data = await response.json();

      // For demo, return simulated data
      const weatherConditions = [
        "Clear",
        "Partly cloudy",
        "Cloudy",
        "Overcast",
        "Light rain",
        "Rain",
        "Heavy rain",
        "Thunderstorm",
        "Fog",
        "Snow",
        "Light snow",
        "Hail",
      ];

      const condition =
        weatherConditions[Math.floor(Math.random() * weatherConditions.length)];
      const temperature = Math.floor(Math.random() * 35) - 5; // -5 to 30°C
      const humidity = Math.floor(Math.random() * 60) + 40; // 40-100%
      const windSpeed = Math.floor(Math.random() * 30) + 1; // 1-30 km/h
      const pressure = Math.floor(Math.random() * 50) + 975; // 975-1025 hPa

      console.log(
        `[Weather] Simulated condition: ${condition}, Temperature: ${temperature}°C`
      );

      return {
        location: {
          lat: latitude,
          lon: longitude,
          name: "Location lookup would happen in production",
        },
        current: {
          temperature,
          condition,
          humidity,
          windSpeed,
          pressure,
          feelsLike: temperature - 2 + Math.random() * 4, // random feels-like adjustment
          uvIndex: Math.floor(Math.random() * 11),
        },
        source: "OpenWeatherMap API (simulated)",
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      console.error("Error fetching weather data:", error);
      throw new Error(`Failed to get weather data: ${error.message}`);
    }
  },
};
