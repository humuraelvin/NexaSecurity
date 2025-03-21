from fastapi import FastAPI, Depends, HTTPException
import uvicorn
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

# Create a simple base PyObjectId class
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Create minimal versions of our models to test
class ScanStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScanType(str, Enum):
    QUICK = "quick"
    FULL = "full"
    NETWORK = "network"
    WEB = "web"
    API = "api"
    CUSTOM = "custom"

class ScanCreate(BaseModel):
    name: str
    target: str
    scan_type: ScanType
    options: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class ScanResponse(BaseModel):
    id: str
    name: str
    target: str
    scan_type: ScanType
    status: ScanStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

# Create the FastAPI app
app = FastAPI(title="Minimal NexaSec API")

@app.get("/")
async def root():
    return {"message": "Minimal app is running"}

@app.post("/scans/", response_model=ScanResponse)
async def create_scan(scan: ScanCreate):
    # Just return a mock response
    return {
        "id": str(ObjectId()),
        "name": scan.name,
        "target": scan.target,
        "scan_type": scan.scan_type,
        "status": ScanStatus.PENDING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@app.get("/scans/", response_model=List[ScanResponse])
async def list_scans():
    # Return mock scans
    return [
        {
            "id": str(ObjectId()),
            "name": "Test Scan 1",
            "target": "example.com",
            "scan_type": ScanType.NETWORK,
            "status": ScanStatus.COMPLETED,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(ObjectId()),
            "name": "Test Scan 2",
            "target": "192.168.1.1",
            "scan_type": ScanType.WEB,
            "status": ScanStatus.IN_PROGRESS,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

if __name__ == "__main__":
    print("Starting minimal app...")
    uvicorn.run("minimal_app:app", host="0.0.0.0", port=8003) 