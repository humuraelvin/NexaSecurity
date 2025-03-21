from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class Vulnerability(BaseModel):
    id: str
    name: str
    description: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    status: Literal["open", "in_progress", "resolved", "false_positive", "wont_fix"]
    affected: str
    discovered: datetime
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    remediation: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VulnerabilityStatusUpdate(BaseModel):
    status: str

class VulnerabilityScanResponse(BaseModel):
    success: bool
    message: str 