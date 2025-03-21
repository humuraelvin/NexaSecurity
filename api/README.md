# NexaSecurity API

Backend API for the NexaSecurity Cybersecurity Platform. This RESTful API provides endpoints for security scanning, network mapping, vulnerability management, penetration testing, reporting, and more.

## Features

- **Authentication**: JWT-based secure authentication system
- **Scan Management**: Start and monitor security scans
- **Network Discovery**: Map and analyze network topology
- **Vulnerability Management**: Track and manage vulnerabilities
- **Penetration Testing**: Configure and run automated penetration tests
- **Reporting**: Generate detailed security reports
- **Dashboard Metrics**: Real-time security metrics and insights
- **User Settings**: Manage user preferences and configurations

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/): Modern, high-performance web framework
- [SQLAlchemy](https://www.sqlalchemy.org/): SQL toolkit and ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/): Data validation and settings management
- [JSON Web Tokens](https://jwt.io/): For secure authentication
- [Uvicorn](https://www.uvicorn.org/): ASGI server for Python

## Getting Started

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/your-org/nexasecurity.git
   cd nexasecurity/api
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with configuration (example provided in `.env.example`)

### Running the API

Start the server with:

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000 and the interactive documentation at http://localhost:8000/docs.

## API Documentation

### Authentication Endpoints

- `POST /auth/login/json`: Log in with email/password
- `POST /auth/signup`: Create new account
- `POST /auth/logout`: Log out current user

### Scan Management

- `POST /scan/start`: Start a new security scan
- `GET /scan/{scan_id}/status`: Check scan status
- `GET /scan/{scan_id}/results`: Get scan results
- `GET /scans`: List all scans

### Network Management

- `GET /network/discover`: Discover network devices
- `GET /network/devices/{id}`: Get device details
- `GET /network`: Get network topology map

### Vulnerability Management

- `GET /vulnerabilities`: List all vulnerabilities
- `GET /vulnerabilities/{id}`: Get vulnerability details
- `PATCH /vulnerabilities/{id}`: Update vulnerability status
- `POST /vulnerabilities/scan`: Scan for vulnerabilities

### Penetration Testing

- `POST /pentests/start`: Start a penetration test
- `GET /pentests/{id}/status`: Check pentest status
- `GET /pentests/{id}/results`: Get pentest results
- `GET /pentests`: List all pentests

### Dashboard

- `GET /dashboard/system-health`: Get system health metrics
- `GET /dashboard/alerts`: Get security alerts
- `GET /dashboard/overview`: Get dashboard overview statistics
- `GET /dashboard/security-score`: Get security score

### Reports

- `GET /reports`: List all reports
- `POST /reports/generate`: Generate a new report
- `GET /reports/{id}`: Get report details
- `GET /reports/{id}/download`: Download report

### Settings

- `PUT /settings/user`: Update user settings
- `PUT /settings/notifications`: Update notification preferences
- `PUT /settings/security`: Update security settings

## Development

For local development, you can use SQLite. For production, it's recommended to use PostgreSQL.

### Database Models

The system uses the following main models:

- `User`: User accounts and authentication
- `Scan`: Security scan records and results
- `Vulnerability`: Security vulnerabilities
- `Pentest`: Penetration test records
- `Report`: Generated security reports

## License

Copyright (c) 2023 NexaSecurity. All rights reserved.
