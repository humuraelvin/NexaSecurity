from fastapi import FastAPI, Depends
import uvicorn
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

app = FastAPI(title="Simple NexaSec API")

# Simple enum for demo
class ScanType(str, Enum):
    NETWORK = "network"
    WEB = "web"
    API = "api"

# Simple model for demo
class ScanCreate(BaseModel):
    name: str
    target: str
    scan_type: ScanType
    description: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Simple app is running"}

@app.post("/scans/")
async def create_scan(scan: ScanCreate):
    return {
        "id": "123",
        "name": scan.name,
        "target": scan.target,
        "scan_type": scan.scan_type,
        "message": "Scan created successfully"
    }

@app.get("/scans/")
async def list_scans():
    return [
        {
            "id": "123",
            "name": "Test Scan",
            "target": "example.com",
            "scan_type": "network",
            "status": "completed"
        }
    ]

if __name__ == "__main__":
    uvicorn.run("simple_app:app", host="0.0.0.0", port=8002) 