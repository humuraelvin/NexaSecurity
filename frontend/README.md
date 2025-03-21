# NexaSecurity Frontend

A modern cybersecurity platform frontend with integrated AI tools for security assessment and monitoring.

## Features

- **AI-Powered Security Tools**: Interactive tools for password checking, network scanning, vulnerability scanning, penetration testing, and traffic analysis
- **API Integrations**: Connect with industry-standard security tools like OWASP ZAP, Shodan, VirusTotal, HaveIBeenPwned, and more
- **Secure Architecture**: Best practices for secure frontend development and API communication
- **Modern UI/UX**: Clean, responsive interface built with React, NextJS, and TailwindCSS

## AI Tools Overview

The frontend includes several AI-powered security tools:

1. **Password Check Tool**: Analyzes password strength and checks for breaches using HaveIBeenPwned API with k-anonymity
2. **Network Scan Tool**: Scans network targets for open ports and services using Shodan API
3. **Vulnerability Scan Tool**: Identifies vulnerabilities in systems using VirusTotal API
4. **Penetration Test Tool**: Executes various penetration tests against targets using OWASP ZAP API
5. **Traffic Analysis Tool**: Analyzes network traffic patterns using Zeek (formerly Bro) IDS
6. **Weather Tool**: Provides weather data for operations planning using OpenWeatherMap API

## Architecture

- **TypeScript**: Type-safe codebase with interfaces for all tool parameters and results
- **Zod Validation**: Runtime validation for all API inputs
- **Error Handling**: Comprehensive error handling for all API interactions
- **Modular Design**: Each tool is independently implemented with reusable components

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Add your API keys to the `.env.local` file:
   ```
   SHODAN_API_KEY=your_key_here
   VIRUSTOTAL_API_KEY=your_key_here
   ZAP_API_URL=http://localhost:8080
   ZAP_API_KEY=your_key_here
   OPENWEATHER_API_KEY=your_key_here
   ZEEK_API_ENDPOINT=http://localhost:9200/zeek
   ZEEK_API_KEY=your_key_here
   ```
4. Run the development server:
   ```
   npm run dev
   ```

## Usage

The AI tools can be accessed through a conversational interface or directly through the UI components. Example operations:

- Check password security: "Check if my password is secure"
- Scan a network: "Scan 192.168.1.0/24 for open ports"
- Analyze vulnerabilities: "Check for vulnerabilities on example.com"
- Run a penetration test: "Run an XSS test against test.example.com"
- Analyze traffic: "Analyze network traffic on eth0 for security threats"

## API Integration

The tools support both real API integration and simulation mode for development:

- **Production Mode**: Connects to real security APIs using environment variables
- **Development Mode**: Simulates API responses for testing and development
- **Hybrid Mode**: Can use real APIs for some tools and simulation for others

To enable simulation mode, set the environment variable:

```
NEXT_PUBLIC_API_SIMULATION=true
```

## Security Notes

- API keys are never exposed to the client
- All operations follow ethical security testing principles
- For penetration testing tools, proper authorization is required
- Use in production environments requires additional security measures

## License

This project is licensed under the MIT License - see the LICENSE file for details.
