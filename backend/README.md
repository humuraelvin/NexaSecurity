# NexaSecurity Backend

The backend service for the NexaSecurity penetration testing tool.

## Setup

1. Clone the repository
2. Navigate to the backend directory
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

Run the application with:

```
python run.py
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing with Postman

### 1. Start a Penetration Test

**Endpoint**: `POST http://localhost:8000/api/v1/pentests/start`

**Request Body**:
```json
{
  "url": "",  // Leave empty to use local IP
  "type": "quick",  // Options: quick, standard, comprehensive, webapp, network, custom
  "options": {
    "portScan": true,
    "vulnScan": true,
    "bruteForce": false,
    "sqlInjection": false,
    "xss": false,
    "networkMapping": false,
    "osFingerprinting": false,
    "serviceDetection": true
  }
}
```

**Response**:
```json
{
  "scanId": "60f7b0f8e1d8a23d4c9a2c10"  // This is the ID you'll use for other requests
}
```

### 2. Check Penetration Test Status

**Endpoint**: `GET http://localhost:8000/api/v1/pentests/{scanId}/status`

**Response**:
```json
{
  "completed": false,
  "progress": 65.0,
  "status": "in_progress"
}
```

### 3. Get All Penetration Tests

**Endpoint**: `GET http://localhost:8000/api/v1/pentests`

**Response**:
```json
[
  {
    "id": "60f7b0f8e1d8a23d4c9a2c10",
    "target": "192.168.1.10",
    "type": "quick",
    "status": "completed",
    "date": "July 21, 2023",
    "criticalVulnerabilities": 1,
    "mediumVulnerabilities": 2,
    "lowVulnerabilities": 3
  },
  // Additional test results...
]
```

### 4. Get Penetration Test Results

**Endpoint**: `GET http://localhost:8000/api/v1/pentests/{scanId}/results`

**Response**:
```json
{
  "id": "60f7b0f8e1d8a23d4c9a2c10",
  "target": "192.168.1.10",
  "type": "quick",
  "status": "completed",
  "date": "July 21, 2023",
  "criticalVulnerabilities": 1,
  "mediumVulnerabilities": 2,
  "lowVulnerabilities": 3,
  "findings": [
    {
      "id": "60f7b0f8e1d8a23d4c9a2c11",
      "title": "SQL Injection in Login Form",
      "description": "The login form is vulnerable to SQL injection...",
      "severity": "critical",
      "status": "open"
    },
    // Additional findings...
  ]
}
```

### 5. Download Penetration Test Report

**Endpoint**: `GET http://localhost:8000/api/v1/pentests/{scanId}/download`

**Response**:
A JSON object containing the report information. In a real-world scenario, this would typically return a PDF or other document format. 