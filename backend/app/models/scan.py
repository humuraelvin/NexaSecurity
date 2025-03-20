from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from app.models.base import MongoBaseModel, PyObjectId

class ScanType(str, Enum):
    NETWORK = "network"
    WEB = "web"
    API = "api"
    MOBILE = "mobile"

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

class ScanCreate(BaseModel):
    target: str
    scan_type: ScanType
    port_range: Optional[str] = None
    intensity: Optional[int] = Field(default=3, ge=1, le=5)
    custom_scripts: Optional[List[str]] = None

    @validator('port_range')
    def validate_port_range(cls, v):
        if v:
            parts = v.split('-')
            if len(parts) == 2:
                start, end = parts
                if not (start.isdigit() and end.isdigit()):
                    raise ValueError("Port range must be numeric")
                if not (1 <= int(start) <= 65535 and 1 <= int(end) <= 65535):
                    raise ValueError("Ports must be between 1 and 65535")
                if int(start) > int(end):
                    raise ValueError("Start port must be less than end port")
            elif len(parts) == 1:
                if not v.isdigit() or not (1 <= int(v) <= 65535):
                    raise ValueError("Port must be between 1 and 65535")
            else:
                raise ValueError("Invalid port range format")
        return v

class ScanInDB(MongoBaseModel):
    user_id: PyObjectId
    target: str
    scan_type: ScanType
    status: ScanStatus = ScanStatus.PENDING
    port_range: Optional[str] = None
    intensity: int = 3
    custom_scripts: Optional[List[str]] = None
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    vulnerability_counts: dict = Field(default_factory=lambda: {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0
    })

    class Collection:
        name = "scans"

class VulnerabilityBase(BaseModel):
    name: str
    description: str
    severity: VulnerabilitySeverity
    cvss_score: Optional[float] = None
    cve_ids: Optional[List[str]] = None
    affected_components: Optional[List[str]] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = None

class VulnerabilityCreate(VulnerabilityBase):
    pass

class VulnerabilityInDB(MongoBaseModel, VulnerabilityBase):
    scan_id: PyObjectId
    status: str = "open"  # open, fixed, false_positive, accepted
    verification_steps: Optional[str] = None
    proof_of_concept: Optional[str] = None
    technical_details: Optional[str] = None
    exploit_available: bool = False
    fixed_in_version: Optional[str] = None
    fixed_date: Optional[datetime] = None

    class Collection:
        name = "vulnerabilities"

class ScanResponse(BaseModel):
    id: str
    user_id: str
    target: str
    scan_type: ScanType
    status: ScanStatus
    port_range: Optional[str]
    intensity: int
    custom_scripts: Optional[List[str]]
    progress: float
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error_message: Optional[str]
    vulnerability_counts: dict
    created_at: datetime
    updated_at: datetime

class VulnerabilityResponse(BaseModel):
    id: str
    scan_id: str
    name: str
    description: str
    severity: VulnerabilitySeverity
    status: str
    cvss_score: Optional[float]
    cve_ids: Optional[List[str]]
    affected_components: Optional[List[str]]
    remediation: Optional[str]
    references: Optional[List[str]]
    verification_steps: Optional[str]
    proof_of_concept: Optional[str]
    technical_details: Optional[str]
    exploit_available: bool
    fixed_in_version: Optional[str]
    fixed_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime 