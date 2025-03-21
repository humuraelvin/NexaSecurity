from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database.database import get_db
from ..schemas.scan import ScanConfigRequest, ScanStartResponse, ScanStatusResponse, ScanResult
from ..services import scan_service
from ..core.security import get_current_user
from ..schemas.auth import User
import os
from fastapi.responses import FileResponse

router = APIRouter(tags=["Scan Management"])

@router.post("/scan/start", response_model=ScanStartResponse)
async def start_scan(
    config: ScanConfigRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scan = scan_service.start_scan(db, current_user.id, config, background_tasks)
    return ScanStartResponse(scanId=scan.id, message="Scan started successfully")

@router.post("/scans/start", response_model=ScanStartResponse)
async def start_scan_alt(
    config: ScanConfigRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # This is an alternative endpoint that does the same thing as /scan/start
    return await start_scan(config, background_tasks, current_user, db)

@router.get("/scan/{scan_id}/status", response_model=ScanStatusResponse)
async def get_scan_status(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scan = scan_service.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Check that the scan belongs to the user
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this scan")
    
    return ScanStatusResponse(
        status=scan.status,
        progress=scan.progress,
        currentTask=scan.current_task,
        startTime=scan.start_time,
        estimatedTimeRemaining=scan.estimated_time_remaining
    )

@router.get("/scan/{scan_id}/results", response_model=ScanResult)
async def get_scan_results(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scan = scan_service.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Check that the scan belongs to the user
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this scan")
    
    # Check if scan is completed
    if scan.status != "completed":
        raise HTTPException(status_code=400, detail="Scan is not completed yet")
    
    return ScanResult(
        id=scan.id,
        target=scan.target,
        scanType=scan.scan_type,
        startTime=scan.start_time,
        endTime=scan.end_time,
        status=scan.status,
        findings=scan.findings,
        summary=scan.summary
    )

@router.get("/scan/{scan_id}/search")
async def search_scan_findings(
    scan_id: str,
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scan = scan_service.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Check that the scan belongs to the user
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this scan")
    
    # Check if scan is completed
    if scan.status != "completed":
        raise HTTPException(status_code=400, detail="Scan is not completed yet")
    
    # Simple search implementation
    search_results = []
    for finding in scan.findings:
        if query.lower() in finding["title"].lower() or query.lower() in finding["description"].lower():
            search_results.append(finding)
    
    return {"status": "success", "results": search_results, "count": len(search_results)}

@router.get("/scan/{scan_id}/download")
async def download_scan_report(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scan = scan_service.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Check that the scan belongs to the user
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this scan")
    
    # Check if scan is completed
    if scan.status != "completed":
        raise HTTPException(status_code=400, detail="Scan is not completed yet")
    
    # Mock file download - in a real application, generate and return the actual report
    # For now, return a successful response
    return {"status": "success", "message": "Report download link generated", "link": f"/api/reports/{scan_id}.pdf"}

@router.get("/scans", response_model=List[ScanResult])
async def get_all_scans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scans = scan_service.get_user_scans(db, current_user.id)
    return [
        ScanResult(
            id=scan.id,
            target=scan.target,
            scanType=scan.scan_type,
            startTime=scan.start_time,
            endTime=scan.end_time,
            status=scan.status,
            findings=scan.findings if scan.findings else [],
            summary=scan.summary if scan.summary else {}
        ) 
        for scan in scans
    ]

@router.get("/scans/{scan_id}", response_model=ScanResult)
async def get_scan_by_id(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # This endpoint is an alternative to /scan/{scan_id}/results
    return await get_scan_results(scan_id, current_user, db)

@router.get("/scans/{scan_id}/results", response_model=ScanResult)
async def get_scan_results_alt(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # This endpoint is an alternative to /scan/{scan_id}/results
    return await get_scan_results(scan_id, current_user, db)

@router.get("/scans/{scan_id}/download")
async def download_scan_report_alt(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # This endpoint is an alternative to /scan/{scan_id}/download
    return await download_scan_report(scan_id, current_user, db) 