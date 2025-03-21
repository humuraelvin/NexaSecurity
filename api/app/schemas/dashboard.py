from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class SystemHealth(BaseModel):
    status: str
    cpu: float
    memory: float
    disk: float
    uptime: int
    lastUpdate: str
    error: Optional[str] = None

class Alert(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    timestamp: str
    is_read: bool

class ThreatDataPoint(BaseModel):
    date: str
    severity: str
    count: int

class DashboardOverview(BaseModel):
    total_scans: int
    total_pentests: int
    active_scans: int
    active_pentests: int
    vulnerability_statistics: Dict[str, int]
    finding_statistics: Dict[str, int]

class TrendsData(BaseModel):
    vulnerability_trends: List[ThreatDataPoint]
    finding_trends: List[ThreatDataPoint]

class RecentActivity(BaseModel):
    recent_scans: List[Dict[str, Any]]
    recent_pentests: List[Dict[str, Any]]
    recent_vulnerabilities: List[Dict[str, Any]]
    recent_findings: List[Dict[str, Any]]

class SecurityScore(BaseModel):
    security_score: int
    risk_level: str
    vulnerability_counts: Dict[str, int]
    finding_counts: Dict[str, int]
    recommendations: List[str] 