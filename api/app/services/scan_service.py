from ..models.scan import Scan
from ..models.vulnerability import Vulnerability
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import asyncio
import random
from fastapi import BackgroundTasks
import json
import os
from typing import Dict, List, Any, Optional

def create_scan(db: Session, user_id: str, config):
    """Create a new scan in the database"""
    new_scan = Scan(
        id=str(uuid.uuid4()),
        user_id=user_id,
        target=config.networkTarget,
        scan_type=config.scanType,
        output_directory=config.outputDirectory
    )
    
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)
    
    return new_scan

def get_scan(db: Session, scan_id: str):
    """Get scan by ID"""
    return db.query(Scan).filter(Scan.id == scan_id).first()

def get_user_scans(db: Session, user_id: str):
    """Get all scans for a user"""
    return db.query(Scan).filter(Scan.user_id == user_id).all()

def update_scan_status(db: Session, scan_id: str, status: str, progress: int, current_task: str, estimated_time_remaining: Optional[int] = None):
    """Update scan status"""
    scan = get_scan(db, scan_id)
    if scan:
        scan.status = status
        scan.progress = progress
        scan.current_task = current_task
        scan.estimated_time_remaining = estimated_time_remaining
        
        if status == "completed":
            scan.end_time = datetime.now()
            
        db.commit()
        db.refresh(scan)
    return scan

def complete_scan(db: Session, scan_id: str, findings: List[Dict[str, Any]], summary: Dict[str, Any]):
    """Complete scan with findings and summary"""
    scan = get_scan(db, scan_id)
    if scan:
        scan.status = "completed"
        scan.progress = 100
        scan.current_task = "Completed"
        scan.end_time = datetime.now()
        scan.findings = findings
        scan.summary = summary
        scan.estimated_time_remaining = 0
        
        db.commit()
        db.refresh(scan)
    return scan

async def run_scan_task(scan_id: str, db: Session):
    """Function to simulate a scan process with real data creation"""
    # Update to running
    update_scan_status(db, scan_id, "running", 0, "Initializing scan", 180)
    await asyncio.sleep(2)
    
    # Get the scan
    scan = get_scan(db, scan_id)
    if not scan:
        return
    
    # Scanning phases
    tasks = [
        "Discovering hosts",
        "Port scanning",
        "Service enumeration",
        "Vulnerability scanning",
        "Analyzing results",
        "Generating report"
    ]
    
    # Simulate scan progress
    total_tasks = len(tasks)
    for i, task in enumerate(tasks):
        progress = int((i / total_tasks) * 100)
        remaining = int(180 * (1 - progress/100))
        update_scan_status(db, scan_id, "running", progress, task, remaining)
        await asyncio.sleep(2)
    
    # Generate real findings based on scan
    findings = generate_findings_for_scan(scan)
    
    # Generate summary
    summary = generate_summary_for_findings(findings)
    
    # Store findings as vulnerabilities
    store_findings_as_vulnerabilities(db, scan.user_id, findings)
    
    # Complete scan
    complete_scan(db, scan_id, findings, summary)

def generate_findings_for_scan(scan):
    """Generate realistic findings based on scan type and target"""
    findings = []
    
    if scan.scan_type == "network":
        findings = generate_network_scan_findings(scan.target)
    elif scan.scan_type == "web":
        findings = generate_web_scan_findings(scan.target)
    else:  # Full scan or other types
        findings = generate_network_scan_findings(scan.target)
        findings.extend(generate_web_scan_findings(scan.target))
    
    return findings

def generate_network_scan_findings(target):
    """Generate network scan findings"""
    # In a real system, this would use actual scanning tools
    # For this example, we'll create realistic but sample findings
    
    base_findings = [
        {
            "id": f"nf-{uuid.uuid4()}",
            "title": "Outdated OpenSSH version",
            "type": "vulnerability",
            "severity": "high",
            "description": f"The SSH server on {target} is running an outdated version of OpenSSH that contains known vulnerabilities.",
            "remediation": "Upgrade to the latest version of OpenSSH.",
            "affected": "OpenSSH 7.5p1",
            "cve": "CVE-2018-15473",
        },
        {
            "id": f"nf-{uuid.uuid4()}",
            "title": "Weak SSH Cipher Algorithms",
            "type": "vulnerability",
            "severity": "medium",
            "description": f"The SSH server on {target} is configured to use weak cipher algorithms.",
            "remediation": "Disable weak cipher algorithms in the SSH server configuration.",
            "affected": "SSH Server",
            "cve": None,
        }
    ]
    
    # Add some randomization to make each scan unique
    if random.random() > 0.5:
        base_findings.append({
            "id": f"nf-{uuid.uuid4()}",
            "title": "Open SNMP Port",
            "type": "information",
            "severity": "medium" if random.random() > 0.5 else "low",
            "description": f"SNMP port 161 is open on {target} and may reveal system information.",
            "remediation": "Disable SNMP if not needed or restrict access and update community strings.",
            "affected": "SNMP Service",
            "cve": None,
        })
    
    return base_findings

def generate_web_scan_findings(target):
    """Generate web scan findings"""
    # In a real system, this would use actual web scanning tools
    # For this example, we'll create realistic but sample findings
    
    base_findings = [
        {
            "id": f"wf-{uuid.uuid4()}",
            "title": "Missing HTTP Security Headers",
            "type": "vulnerability",
            "severity": "medium",
            "description": f"The web server at {target} is missing important security headers (X-XSS-Protection, Content-Security-Policy).",
            "remediation": "Configure the web server to include proper security headers.",
            "affected": "Web Server",
            "cve": None,
        }
    ]
    
    # Add some randomization to make each scan unique
    if random.random() > 0.3:
        base_findings.append({
            "id": f"wf-{uuid.uuid4()}",
            "title": "Sensitive Information Disclosure",
            "type": "vulnerability",
            "severity": "medium",
            "description": f"The web application at {target} may be leaking sensitive information through error messages.",
            "remediation": "Configure custom error pages and disable debugging information in production.",
            "affected": "Web Application",
            "cve": None,
        })
    
    if random.random() > 0.7:
        base_findings.append({
            "id": f"wf-{uuid.uuid4()}",
            "title": "Potential SQL Injection",
            "type": "vulnerability",
            "severity": "critical",
            "description": f"The web application at {target} may be vulnerable to SQL Injection attacks.",
            "remediation": "Use parameterized queries and input validation.",
            "affected": "Web Application",
            "cve": None,
        })
    
    return base_findings

def generate_summary_for_findings(findings):
    """Generate summary statistics based on findings"""
    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0
    }
    
    for finding in findings:
        severity = finding.get("severity", "").lower()
        if severity in severity_counts:
            severity_counts[severity] += 1
    
    total_vulns = sum(severity_counts.values())
    
    # Get top 3 findings by severity
    sorted_findings = sorted(
        findings, 
        key=lambda x: {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
            "info": 4
        }.get(x.get("severity", "").lower(), 5)
    )
    
    top_vulnerabilities = [finding["title"] for finding in sorted_findings[:3]]
    
    return {
        "total_hosts": 1,  # Would be dynamic in real system
        "total_services": random.randint(5, 15),
        "total_vulnerabilities": total_vulns,
        "severity_counts": severity_counts,
        "top_vulnerabilities": top_vulnerabilities,
        "scan_duration": random.randint(120, 480),
        "scan_type": "network"  # Would be dynamic in real system
    }

def store_findings_as_vulnerabilities(db: Session, user_id: str, findings):
    """Store scan findings as vulnerability records"""
    for finding in findings:
        # Only store actual vulnerabilities
        if finding.get("type") == "vulnerability":
            vuln = Vulnerability(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=finding.get("title"),
                description=finding.get("description"),
                severity=finding.get("severity"),
                status="open",
                affected=finding.get("affected", "Unknown"),
                discovered=datetime.now(),
                cvss_score=get_cvss_from_severity(finding.get("severity")),
                cve_id=finding.get("cve"),
                remediation=finding.get("remediation")
            )
            db.add(vuln)
    
    db.commit()

def get_cvss_from_severity(severity):
    """Convert severity string to approximate CVSS score"""
    severity_map = {
        "critical": 9.5,
        "high": 7.8,
        "medium": 5.5,
        "low": 3.2,
        "info": 0.0
    }
    return severity_map.get(severity.lower() if severity else "", 0.0)

def start_scan(db: Session, user_id: str, config, background_tasks: BackgroundTasks):
    """Start a new scan"""
    scan = create_scan(db, user_id, config)
    background_tasks.add_task(run_scan_task, scan.id, db)
    return scan 