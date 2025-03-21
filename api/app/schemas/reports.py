from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportGenerationRequest(BaseModel):
    type: str
    target: Optional[str] = None
    includeRemediation: Optional[bool] = None

class Report(BaseModel):
    id: str
    title: str
    created_at: datetime
    type: str
    status: str
    target: Optional[str] = None
    findings_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int 