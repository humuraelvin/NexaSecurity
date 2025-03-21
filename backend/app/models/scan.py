from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.base import PyObjectId, MongoBaseModel
from bson import ObjectId

class ScanStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VulnerabilitySeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

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

class ScanUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[ScanStatus] = None
    end_time: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None

class Scan(MongoBaseModel):
    user_id: Optional[PyObjectId] = None
    name: str
    target: str
    scan_type: ScanType
    status: ScanStatus = ScanStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    options: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    port_range: Optional[str] = None
    intensity: Optional[int] = None
    custom_scripts: Optional[List[str]] = None
    progress: float = 0.0
    vulnerability_counts: Dict[str, int] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ScanInDB(Scan):
    pass

class VulnerabilityBase(BaseModel):
    name: str
    description: str
    severity: VulnerabilitySeverity
    affected_components: Optional[List[str]] = None
    cvss_score: Optional[float] = None
    cve_ids: Optional[List[str]] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = None

class VulnerabilityCreate(VulnerabilityBase):
    scan_id: PyObjectId

class VulnerabilityInDB(MongoBaseModel, VulnerabilityBase):
    scan_id: PyObjectId
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class VulnerabilityResponse(VulnerabilityBase):
    id: str
    scan_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None 