from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

class ScanConfigRequest(BaseModel):
    networkTarget: str
    outputDirectory: str
    scanType: Literal["network", "web", "full"]
    useCustomPasswordList: bool

class ScanStartResponse(BaseModel):
    scanId: str
    message: str

class ScanStatusResponse(BaseModel):
    status: Literal["running", "completed", "failed"]
    progress: int
    currentTask: str
    startTime: datetime
    estimatedTimeRemaining: Optional[int] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScanResult(BaseModel):
    id: str
    target: str
    scanType: str
    startTime: datetime
    endTime: Optional[datetime] = None
    status: str
    findings: List[Dict[str, Any]]
    summary: Dict[str, Any]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 