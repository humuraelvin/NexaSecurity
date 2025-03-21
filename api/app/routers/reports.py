from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..schemas.reports import ReportGenerationRequest, Report
from ..core.security import get_current_user
from ..schemas.auth import User
from ..models.report import Report as ReportModel
import uuid
from datetime import datetime
import asyncio
import random

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

@router.get("", response_model=List[Report])
async def get_all_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reports for the current user"""
    reports = db.query(ReportModel).filter(ReportModel.user_id == current_user.id).all()
    
    return [
        Report(
            id=report.id,
            title=report.title,
            created_at=report.created_at,
            type=report.type,
            status=report.status,
            target=report.target,
            findings_count=report.findings_count,
            critical_count=report.critical_count,
            high_count=report.high_count,
            medium_count=report.medium_count,
            low_count=report.low_count
        )
        for report in reports
    ]

@router.post("/generate")
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new report"""
    report_id = str(uuid.uuid4())
    
    # Create a title based on type and date
    title = f"{request.type.capitalize()} Security Report - {datetime.now().strftime('%B %d, %Y')}"
    if request.target:
        title = f"{title} for {request.target}"
    
    # Create a new report in the database
    new_report = ReportModel(
        id=report_id,
        user_id=current_user.id,
        title=title,
        type=request.type,
        status="generating",
        target=request.target
    )
    
    db.add(new_report)
    db.commit()
    
    # Start background task to generate the report
    background_tasks.add_task(generate_report_task, report_id, db)
    
    return {
        "status": "success",
        "message": "Report generation started",
        "report_id": report_id
    }

async def generate_report_task(report_id: str, db: Session):
    """Background task to generate a report"""
    # Simulate report generation
    await asyncio.sleep(3)
    
    # Generate random findings counts
    findings_count = random.randint(10, 30)
    critical_count = random.randint(0, 3)
    high_count = random.randint(2, 8)
    medium_count = random.randint(5, 15)
    low_count = findings_count - critical_count - high_count - medium_count
    
    # Update the report with completed status and counts
    report = db.query(ReportModel).filter(ReportModel.id == report_id).first()
    if report:
        report.status = "generated"
        report.findings_count = findings_count
        report.critical_count = critical_count
        report.high_count = high_count
        report.medium_count = medium_count
        report.low_count = low_count
        report.file_path = f"/reports/{report_id}.pdf"
        
        db.commit()

@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific report"""
    report = db.query(ReportModel).filter(ReportModel.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    
    return Report(
        id=report.id,
        title=report.title,
        created_at=report.created_at,
        type=report.type,
        status=report.status,
        target=report.target,
        findings_count=report.findings_count,
        critical_count=report.critical_count,
        high_count=report.high_count,
        medium_count=report.medium_count,
        low_count=report.low_count
    )

@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a report"""
    report = db.query(ReportModel).filter(ReportModel.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    
    if report.status != "generated":
        raise HTTPException(status_code=400, detail="Report generation is not complete")
    
    # In a real application, this would return the actual PDF file
    return {
        "status": "success",
        "message": "Report download link generated",
        "link": f"/api/reports/{report_id}.pdf"
    } 