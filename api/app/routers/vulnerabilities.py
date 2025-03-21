from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..schemas.vulnerabilities import Vulnerability, VulnerabilityStatusUpdate, VulnerabilityScanResponse
from ..core.security import get_current_user
from ..schemas.auth import User
from datetime import datetime
import uuid
from ..models.vulnerability import Vulnerability as VulnerabilityModel

router = APIRouter(
    prefix="/vulnerabilities",
    tags=["Vulnerability Management"],
)

@router.get("", response_model=List[Vulnerability])
async def get_vulnerabilities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all vulnerabilities"""
    vulnerabilities = db.query(VulnerabilityModel).filter(
        VulnerabilityModel.user_id == current_user.id
    ).all()
    
    return [Vulnerability.from_orm(vuln) for vuln in vulnerabilities]

@router.get("/{vulnerability_id}", response_model=Vulnerability)
async def get_vulnerability(
    vulnerability_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific vulnerability"""
    vulnerability = db.query(VulnerabilityModel).filter(
        VulnerabilityModel.id == vulnerability_id,
        VulnerabilityModel.user_id == current_user.id
    ).first()
    
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    return Vulnerability.from_orm(vulnerability)

@router.patch("/{vulnerability_id}")
async def update_vulnerability_status(
    vulnerability_id: str,
    status_update: VulnerabilityStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update vulnerability status"""
    vulnerability = db.query(VulnerabilityModel).filter(
        VulnerabilityModel.id == vulnerability_id,
        VulnerabilityModel.user_id == current_user.id
    ).first()
    
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    vulnerability.status = status_update.status
    vulnerability.updated_at = datetime.now()
    db.commit()
    
    return {"status": "success", "message": "Vulnerability status updated"}

@router.post("/scan", response_model=VulnerabilityScanResponse)
async def scan_for_vulnerabilities(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start vulnerability scan"""
    # Initiate a background task to perform the vulnerability scan
    background_tasks.add_task(
        perform_vulnerability_scan, 
        current_user.id, 
        db
    )
    
    return VulnerabilityScanResponse(
        success=True,
        message="Vulnerability scan started. Results will be available in the vulnerabilities list when complete."
    )

async def perform_vulnerability_scan(user_id: str, db: Session):
    """Background task to perform vulnerability scanning"""
    import asyncio
    import random
    
    # Simulate scan delay
    await asyncio.sleep(2)
    
    # Cleanup any old sample vulnerabilities from previous scans
    db.query(VulnerabilityModel).filter(
        VulnerabilityModel.user_id == user_id,
    ).delete()
    
    # Categories of vulnerabilities to simulate
    vulnerability_types = [
        {
            "category": "Web Application",
            "vulnerabilities": [
                {
                    "name": "SQL Injection",
                    "description": "SQL injection vulnerability in login form allows attackers to bypass authentication and extract sensitive data.",
                    "severity": "critical",
                    "cvss_score": 9.8,
                    "cve_id": "CVE-2023-45678",
                    "remediation": "Use prepared statements, parameterized queries, and implement input validation. Consider using an ORM framework."
                },
                {
                    "name": "Cross-Site Scripting (XSS)",
                    "description": "Reflected XSS vulnerability in search functionality allows attackers to inject malicious scripts.",
                    "severity": "high",
                    "cvss_score": 7.4,
                    "cve_id": None,
                    "remediation": "Implement proper output encoding, use Content-Security-Policy headers, and sanitize user input."
                },
                {
                    "name": "Insecure Direct Object References",
                    "description": "Application exposes a direct reference to internal objects, allowing unauthorized access to data.",
                    "severity": "medium",
                    "cvss_score": 6.5,
                    "cve_id": None,
                    "remediation": "Implement proper access controls and use indirect references with authorization checks."
                },
                {
                    "name": "Cross-Site Request Forgery (CSRF)",
                    "description": "Application lacks CSRF tokens, allowing attackers to perform actions on behalf of authenticated users.",
                    "severity": "medium",
                    "cvss_score": 6.8,
                    "cve_id": None,
                    "remediation": "Implement CSRF tokens for all state-changing operations and validate them server-side."
                }
            ]
        },
        {
            "category": "Network Infrastructure",
            "vulnerabilities": [
                {
                    "name": "Outdated SSL/TLS Configuration",
                    "description": "Server supports outdated TLS 1.0 and SSL 3.0 protocols with known security vulnerabilities.",
                    "severity": "high",
                    "cvss_score": 7.5,
                    "cve_id": "CVE-2015-0204",
                    "remediation": "Disable TLS 1.0 and SSL 3.0 in server configuration. Enable only TLS 1.2+ with secure cipher suites."
                },
                {
                    "name": "Open Ports Exposure",
                    "description": "Unnecessary ports are exposed to the internet, increasing the attack surface.",
                    "severity": "medium",
                    "cvss_score": 5.9,
                    "cve_id": None,
                    "remediation": "Implement proper network segmentation and firewall rules. Only expose necessary services."
                },
                {
                    "name": "Weak SSH Configuration",
                    "description": "SSH server allows weak ciphers and authentication methods.",
                    "severity": "medium",
                    "cvss_score": 6.2,
                    "cve_id": None,
                    "remediation": "Configure SSH to use only strong ciphers, disable password authentication, and implement key-based authentication."
                }
            ]
        },
        {
            "category": "Server Configuration",
            "vulnerabilities": [
                {
                    "name": "Missing Security Headers",
                    "description": "Web server is missing important security headers like X-Content-Type-Options, X-Frame-Options, and Content-Security-Policy.",
                    "severity": "low",
                    "cvss_score": 4.3,
                    "cve_id": None,
                    "remediation": "Configure web server to include all recommended security headers in HTTP responses."
                },
                {
                    "name": "Directory Listing Enabled",
                    "description": "Web server has directory listing enabled, revealing file structure to potential attackers.",
                    "severity": "low",
                    "cvss_score": 3.8,
                    "cve_id": None,
                    "remediation": "Disable directory listing in web server configuration."
                },
                {
                    "name": "Default Credentials",
                    "description": "Application admin interface accessible with default credentials.",
                    "severity": "critical",
                    "cvss_score": 9.1,
                    "cve_id": None,
                    "remediation": "Change all default credentials. Implement a strong password policy and periodic password rotation."
                }
            ]
        },
        {
            "category": "Authentication & Authorization",
            "vulnerabilities": [
                {
                    "name": "Insufficient Password Policy",
                    "description": "Password policy allows weak passwords that are susceptible to brute force attacks.",
                    "severity": "medium",
                    "cvss_score": 5.5,
                    "cve_id": None,
                    "remediation": "Implement a strong password policy requiring minimum length, complexity, and prohibiting common passwords."
                },
                {
                    "name": "Missing Account Lockout",
                    "description": "Application doesn't lock accounts after multiple failed login attempts.",
                    "severity": "medium",
                    "cvss_score": 6.0,
                    "cve_id": None,
                    "remediation": "Implement account lockout after a certain number of failed login attempts."
                },
                {
                    "name": "Missing Multi-Factor Authentication",
                    "description": "Critical functionality lacks multi-factor authentication.",
                    "severity": "high",
                    "cvss_score": 7.2,
                    "cve_id": None,
                    "remediation": "Implement multi-factor authentication for all users, especially for administrative access."
                }
            ]
        }
    ]
    
    # Select random number of vulnerability categories
    selected_categories = random.sample(vulnerability_types, k=random.randint(2, len(vulnerability_types)))
    
    # Create vulnerability objects to add to the database
    vulnerabilities_to_add = []
    
    for category in selected_categories:
        # Select a random number of vulnerabilities from each category
        count = random.randint(1, len(category["vulnerabilities"]))
        selected_vulns = random.sample(category["vulnerabilities"], k=count)
        
        for vuln in selected_vulns:
            status_options = ["open", "in_progress", "resolved", "false_positive"]
            # Bias towards open vulnerabilities
            status_weights = [0.7, 0.2, 0.05, 0.05]
            
            vulnerabilities_to_add.append(
                VulnerabilityModel(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    name=vuln["name"],
                    description=vuln["description"],
                    severity=vuln["severity"],
                    status=random.choices(status_options, weights=status_weights)[0],
                    affected=category["category"],
                    discovered=datetime.now(),
                    cvss_score=vuln["cvss_score"],
                    cve_id=vuln["cve_id"],
                    remediation=vuln["remediation"]
                )
            )
    
    # Add all vulnerabilities to the database
    db.add_all(vulnerabilities_to_add)
    db.commit() 