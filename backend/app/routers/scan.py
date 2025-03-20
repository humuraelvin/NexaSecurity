from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Any, List, Optional
from app.core.database import get_database
from app.services.auth import get_current_user
from app.services.scanner import Scanner
from app.models.user import UserInDB
from app.models.scan import ScanType, ScanStatus, ScanCreate, ScanResponse, VulnerabilityResponse
from pydantic import BaseModel, validator
import ipaddress
from datetime import datetime
from bson import ObjectId

router = APIRouter()

class ScanCreate(BaseModel):
    target: str
    scan_type: ScanType
    port_range: Optional[str] = None
    intensity: Optional[int] = 3
    custom_scripts: Optional[List[str]] = None

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
    id: int
    target: str
    scan_type: ScanType
    status: ScanStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_hosts: Optional[int]
    open_ports: Optional[int]
    vulnerabilities_found: Optional[int]
    summary: Optional[dict]

class VulnerabilityResponse(BaseModel):
    id: int
    name: str
    description: str
    severity: str
    cve_id: Optional[str]
    cvss_score: Optional[float]
    affected_component: Optional[str]
    affected_port: Optional[int]
    proof_of_concept: Optional[str]
    remediation_steps: Optional[str]
    references: Optional[List[str]]

@router.post("/", response_model=ScanResponse)
async def create_scan(
    *,
    scan_in: ScanCreate,
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
    scan_id = await scanner.create_scan(
        target=scan_in.target,
        scan_type=scan_in.scan_type,
        port_range=scan_in.port_range,
        intensity=scan_in.intensity,
        custom_scripts=scan_in.custom_scripts,
        user_id=current_user.id
    )
    
    # Get the created scan
    scan = await db["scans"].find_one({"_id": scan_id})
    
    return {**scan, "id": str(scan["_id"])}

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    db = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    Get scan by ID.
    """
    scan = await db["scans"].find_one({
        "_id": ObjectId(scan_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if not scan:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )
    
    return {**scan, "id": str(scan["_id"])}

@router.get("/{scan_id}/vulnerabilities", response_model=List[VulnerabilityResponse])
async def get_scan_vulnerabilities(
    scan_id: str,
    severity: Optional[str] = None,
    db = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    Get vulnerabilities found in scan.
    """
    # Check scan exists and belongs to user
    scan = await db["scans"].find_one({
        "_id": ObjectId(scan_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if not scan:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )
    
    # Query vulnerabilities
    query = {"scan_id": ObjectId(scan_id)}
    
    if severity:
        query["severity"] = severity
    
    cursor = db["vulnerabilities"].find(query)
    vulns = await cursor.to_list(length=100)
    
    # Format the response
    return [{**vuln, "id": str(vuln["_id"])} for vuln in vulns]

@router.get("/{scan_id}/status")
async def get_scan_status(
    scan_id: str,
    db = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    Get scan status and progress.
    """
    scan = await db["scans"].find_one({
        "_id": ObjectId(scan_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if not scan:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )
    
    progress = None
    if scan["status"] == ScanStatus.IN_PROGRESS:
        scanner = Scanner(db)
        progress = await scanner.get_scan_progress(scan_id)
    
    return {
        "status": scan["status"],
        "progress": progress
    }

@router.post("/{scan_id}/cancel")
async def cancel_scan(
    scan_id: str,
    db = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    Cancel running scan.
    """
    scan = await db["scans"].find_one({
        "_id": ObjectId(scan_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if not scan:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )
    
    if scan["status"] != ScanStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400,
            detail="Can only cancel scans that are in progress"
        )
    
    # Cancel scan
    scanner = Scanner(db)
    await scanner.cancel_scan(scan_id)
    
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
    
    cursor = db["scans"].find(query).skip(skip).limit(limit).sort("created_at", -1)
    scans = await cursor.to_list(length=limit)
    
    # Format the response
    return [{**scan, "id": str(scan["_id"])} for scan in scans] 