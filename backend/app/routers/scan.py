from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Any, List, Optional
from app.core.database import get_database
from app.services.auth import get_current_user
from app.services.scanner import Scanner
from app.services.api_key import ApiKeyService
from app.models.user import UserInDB
from app.models.scan import (
    ScanType, 
    ScanStatus, 
    ScanCreate, 
    ScanInDB,
    VulnerabilityInDB,
    VulnerabilitySeverity,
    VulnerabilityResponse
)
from app.models.api_key import ApiKeyCreate
from pydantic import BaseModel, validator
import ipaddress
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from app.schemas import ScanStatus as ScanStatusSchema, ScanConfig

router = APIRouter()

logger = logging.getLogger(__name__)

class ScanCreateRequest(BaseModel):
    target: str
    scan_type: ScanType
    port_range: Optional[str] = None
    intensity: Optional[int] = 3
    custom_scripts: Optional[List[str]] = None
    name: str = "New Scan"
    description: Optional[str] = None

    @validator("target")
    def validate_target(cls, v):
        """Validate target is a valid IP or domain."""
        try:
            ipaddress.ip_address(v)
        except ValueError:
            # If not IP, check if it's a domain
            if not all(c.isalnum() or c in "-." for c in v):
                raise ValueError("Invalid target. Must be IP address or domain name")
        return v

    @validator("port_range")
    def validate_port_range(cls, v):
        """Validate port range format."""
        if v:
            try:
                for part in v.split(","):
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        if not (1 <= start <= 65535 and 1 <= end <= 65535):
                            raise ValueError()
                    else:
                        port = int(part)
                        if not 1 <= port <= 65535:
                            raise ValueError()
            except (ValueError, TypeError):
                raise ValueError("Invalid port range format")
        return v

    @validator("intensity")
    def validate_intensity(cls, v):
        """Validate scan intensity."""
        if v and not 1 <= v <= 5:
            raise ValueError("Intensity must be between 1 and 5")
        return v

class ScanResponse(BaseModel):
    id: str
    target: str
    scan_type: ScanType
    status: ScanStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_hosts: Optional[int] = None
    open_ports: Optional[int] = None
    vulnerabilities_found: Optional[int] = None
    summary: Optional[dict] = None
    api_key: Optional[dict] = None

class VulnerabilityResponse(BaseModel):
    id: str
    name: str
    description: str
    severity: str
    cve_ids: Optional[List[str]] = None
    cvss_score: Optional[float] = None
    affected_components: Optional[List[str]] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = None

@router.post("/", response_model=ScanResponse)
async def create_scan(
    *,
    scan_in: ScanCreateRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    Create new scan.
    """
    # Check user's scan limit
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_scans_count = await db["scans"].count_documents({
        "user_id": ObjectId(current_user.id),
        "created_at": {"$gte": today_start}
    })
    
    if today_scans_count >= current_user.scan_limit:
        raise HTTPException(
            status_code=429,
            detail="Daily scan limit reached"
        )
    
    # Create scan record
    scanner = Scanner(db)
    scan_create = ScanCreate(
        name=scan_in.name,
        target=scan_in.target,
        scan_type=scan_in.scan_type,
        options={
            "port_range": scan_in.port_range,
            "intensity": scan_in.intensity,
            "custom_scripts": scan_in.custom_scripts
        },
        description=scan_in.description
    )
    
    scan = await scanner.create_scan(str(current_user.id), scan_create)
    
    # Generate API key for this scan
    api_key_service = ApiKeyService(db)
    api_key = await api_key_service.create_api_key(
        str(current_user.id),
        ApiKeyCreate(
            name=f"Scan {scan.name} API Key",
            scopes=["scan:read"],
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
    )
    
    # Convert to response model format
    return {
        "id": str(scan.id),
        "target": scan.target,
        "scan_type": scan.scan_type,
        "status": scan.status,
        "start_time": scan.start_time,
        "end_time": scan.end_time,
        "total_hosts": scan.results.get("total_hosts"),
        "open_ports": scan.results.get("open_ports"),
        "vulnerabilities_found": sum(scan.vulnerability_counts.values()) if scan.vulnerability_counts else 0,
        "summary": scan.results.get("summary"),
        "api_key": {
            "id": api_key.id,
            "key": api_key.key,
            "name": api_key.name,
            "expires_at": api_key.expires_at
        }
    }

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    db = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    Get scan by ID.
    """
    scanner = Scanner(db)
    scan = await scanner.get_scan(scan_id)
    
    if not scan or str(scan.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )
    
    # Check if there's an API key for this scan
    api_key_service = ApiKeyService(db)
    api_keys = await api_key_service.get_api_keys(str(current_user.id))
    # Find API keys that might be related to this scan (by name)
    scan_api_key = next((k for k in api_keys if f"Scan {scan.name}" in k.name), None)
    
    api_key_info = None
    if scan_api_key:
        api_key_info = {
            "id": scan_api_key.id,
            "key": scan_api_key.key,  # This will be masked
            "name": scan_api_key.name,
            "expires_at": scan_api_key.expires_at
        }
    
    # Convert to response model format
    return {
        "id": str(scan.id),
        "target": scan.target,
        "scan_type": scan.scan_type,
        "status": scan.status,
        "start_time": scan.start_time,
        "end_time": scan.end_time,
        "total_hosts": scan.results.get("total_hosts"),
        "open_ports": scan.results.get("open_ports"),
        "vulnerabilities_found": sum(scan.vulnerability_counts.values()) if scan.vulnerability_counts else 0,
        "summary": scan.results.get("summary"),
        "api_key": api_key_info
    }

@router.get("/{scan_id}/vulnerabilities", response_model=List[VulnerabilityResponse])
async def get_scan_vulnerabilities(
    scan_id: str,
    severity: Optional[VulnerabilitySeverity] = None,
    db = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    Get vulnerabilities found in scan.
    """
    scanner = Scanner(db)
    
    # Check scan exists and belongs to user
    scan = await scanner.get_scan(scan_id)
    if not scan or str(scan.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )
    
    # Get vulnerabilities
    vulnerabilities = await scanner.get_scan_vulnerabilities(scan_id, severity)
    
    # Format the response
    return [
        {
            "id": str(vuln.id),
            "name": vuln.name,
            "description": vuln.description,
            "severity": vuln.severity,
            "cve_ids": vuln.cve_ids,
            "cvss_score": vuln.cvss_score,
            "affected_components": vuln.affected_components,
            "remediation": vuln.remediation,
            "references": vuln.references
        }
        for vuln in vulnerabilities
    ]

@router.post("/{scan_id}/cancel")
async def cancel_scan(
    scan_id: str,
    db = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    Cancel running scan.
    """
    scanner = Scanner(db)
    
    # Check scan exists and belongs to user
    scan = await scanner.get_scan(scan_id)
    if not scan or str(scan.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )
    
    if scan.status != ScanStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400,
            detail="Can only cancel scans that are in progress"
        )
    
    # Cancel scan
    success = await scanner.cancel_scan(scan_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel scan"
        )
    
    return {"message": "Scan cancelled successfully"}

@router.get("/", response_model=List[ScanResponse])
async def list_scans(
    skip: int = 0,
    limit: int = 10,
    status: Optional[ScanStatus] = None,
    db = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    List user's scans.
    """
    query = {"user_id": ObjectId(current_user.id)}
    
    if status:
        query["status"] = status
    
    total = await db["scans"].count_documents(query)
    
    cursor = db["scans"].find(query).sort("created_at", -1).skip(skip).limit(limit)
    scans = await cursor.to_list(length=limit)
    
    # Get all API keys for the user
    api_key_service = ApiKeyService(db)
    api_keys = await api_key_service.get_api_keys(str(current_user.id))
    
    result = []
    for scan in scans:
        # Find API key related to this scan
        scan_api_key = next((k for k in api_keys if f"Scan {scan['name']}" in k.name), None)
        
        api_key_info = None
        if scan_api_key:
            api_key_info = {
                "id": scan_api_key.id,
                "key": scan_api_key.key,  # This will be masked
                "name": scan_api_key.name,
                "expires_at": scan_api_key.expires_at
            }
        
        result.append({
            "id": str(scan["_id"]),
            "target": scan["target"],
            "scan_type": scan["scan_type"],
            "status": scan["status"],
            "start_time": scan.get("start_time"),
            "end_time": scan.get("end_time"),
            "total_hosts": scan.get("results", {}).get("total_hosts"),
            "open_ports": scan.get("results", {}).get("open_ports"),
            "vulnerabilities_found": sum(scan.get("vulnerability_counts", {}).values()) if scan.get("vulnerability_counts") else 0,
            "summary": scan.get("results", {}).get("summary"),
            "api_key": api_key_info
        })
    
    return result

@router.post("/start", response_model=ScanResponse)
async def start_scan(
    scan_config: ScanConfig,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """Start a new scan."""
    try:
        scanner = Scanner(db)
        
        # Create the scan
        scan_create = ScanCreate(
            name=scan_config.name,
            target=scan_config.target,
            scan_type=scan_config.scan_type,
            options=scan_config.options,
            description=scan_config.description
        )
        
        scan = await scanner.create_scan(str(current_user.id), scan_create)
        
        # Generate API key for this scan
        api_key_service = ApiKeyService(db)
        api_key = await api_key_service.create_api_key(
            str(current_user.id),
            ApiKeyCreate(
                name=f"Scan {scan.name} API Key",
                scopes=["scan:read"],
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
        )
        
        return {
            "id": str(scan.id),
            "target": scan.target,
            "scan_type": scan.scan_type,
            "status": scan.status,
            "start_time": scan.start_time,
            "end_time": scan.end_time,
            "total_hosts": scan.results.get("total_hosts"),
            "open_ports": scan.results.get("open_ports"),
            "vulnerabilities_found": sum(scan.vulnerability_counts.values()) if scan.vulnerability_counts else 0,
            "summary": scan.results.get("summary"),
            "api_key": {
                "id": api_key.id,
                "key": api_key.key,
                "name": api_key.name,
                "expires_at": api_key.expires_at
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting scan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start scan: {str(e)}"
        )