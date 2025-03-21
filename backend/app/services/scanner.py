from datetime import datetime
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException, status
import asyncio
import json
import random

from app.models.base import PyObjectId
from app.models.scan import (
    ScanCreate,
    ScanInDB,
    VulnerabilityCreate,
    VulnerabilityInDB,
    ScanStatus,
    VulnerabilitySeverity
)
from app.core.config import settings

class Scanner:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.active_scans: Dict[str, asyncio.Task] = {}

    async def create_scan(self, user_id: str, scan_create: ScanCreate) -> ScanInDB:
        """Create a new scan."""
        # Check concurrent scans limit
        active_count = await self.db["scans"].count_documents({
            "user_id": ObjectId(user_id),
            "status": ScanStatus.IN_PROGRESS
        })
        if active_count >= settings.MAX_CONCURRENT_SCANS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum concurrent scans limit reached"
            )

        # Create scan document
        scan_dict = scan_create.model_dump()
        scan_dict["user_id"] = ObjectId(user_id)
        scan_dict["status"] = ScanStatus.PENDING
        scan_dict["created_at"] = datetime.utcnow()
        scan_dict["updated_at"] = datetime.utcnow()

        # Insert into database
        result = await self.db["scans"].insert_one(scan_dict)
        scan_dict["_id"] = result.inserted_id

        # Create scan object
        scan = ScanInDB(**scan_dict)

        # Start scan in background
        self.active_scans[str(scan.id)] = asyncio.create_task(
            self._run_scan(str(scan.id))
        )

        return scan

    async def _run_scan(self, scan_id: str) -> None:
        """Execute the scan."""
        try:
            # Get scan from database
            scan_dict = await self.db["scans"].find_one({"_id": ObjectId(scan_id)})
            if not scan_dict:
                return

            # Update status to in progress
            await self.db["scans"].update_one(
                {"_id": ObjectId(scan_id)},
                {
                    "$set": {
                        "status": ScanStatus.IN_PROGRESS,
                        "start_time": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            # Simulate scanning by waiting a few seconds
            await asyncio.sleep(5)
            
            # Create some sample vulnerability findings
            scan = ScanInDB(**scan_dict)
            
            # Mock vulnerabilities based on scan type
            if scan.scan_type == "network":
                await self._create_mock_network_vulnerabilities(scan.id)
            elif scan.scan_type == "web":
                await self._create_mock_web_vulnerabilities(scan.id)
            elif scan.scan_type == "api":
                await self._create_mock_api_vulnerabilities(scan.id)
            else:
                await self._create_mock_generic_vulnerabilities(scan.id)

            # Update status to completed
            await self.db["scans"].update_one(
                {"_id": ObjectId(scan_id)},
                {
                    "$set": {
                        "status": ScanStatus.COMPLETED,
                        "end_time": datetime.utcnow(),
                        "progress": 100.0,
                        "updated_at": datetime.utcnow(),
                        "results": {
                            "summary": "Scan completed successfully",
                            "total_hosts": 1,
                            "open_ports": random.randint(3, 10)
                        }
                    }
                }
            )

        except Exception as e:
            # Update status to failed
            await self.db["scans"].update_one(
                {"_id": ObjectId(scan_id)},
                {
                    "$set": {
                        "status": ScanStatus.FAILED,
                        "end_time": datetime.utcnow(),
                        "error_message": str(e),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        finally:
            # Remove from active scans
            self.active_scans.pop(scan_id, None)
            
    async def _create_mock_network_vulnerabilities(self, scan_id: PyObjectId) -> None:
        """Create mock network vulnerabilities."""
        await self._create_vulnerability(
            scan_id,
            name="Open SSH Port",
            description="SSH port 22 is open and accessible.",
            severity=VulnerabilitySeverity.MEDIUM,
            affected_components=["22/tcp"],
            cvss_score=5.5,
            remediation="Restrict SSH access to specific IP addresses."
        )
        
        await self._create_vulnerability(
            scan_id,
            name="Outdated SSL/TLS Version",
            description="Server supports outdated TLS 1.0 protocol.",
            severity=VulnerabilitySeverity.HIGH,
            affected_components=["443/tcp"],
            cvss_score=7.5,
            remediation="Disable TLS 1.0 and 1.1, enable only TLS 1.2 and above."
        )
        
    async def _create_mock_web_vulnerabilities(self, scan_id: PyObjectId) -> None:
        """Create mock web vulnerabilities."""
        await self._create_vulnerability(
            scan_id,
            name="Cross-Site Scripting (XSS)",
            description="Reflected XSS vulnerability in search parameter.",
            severity=VulnerabilitySeverity.HIGH,
            affected_components=["/search"],
            cvss_score=6.5,
            remediation="Implement input validation and output encoding."
        )
        
        await self._create_vulnerability(
            scan_id,
            name="SQL Injection",
            description="SQL injection vulnerability in login form.",
            severity=VulnerabilitySeverity.CRITICAL,
            affected_components=["/login"],
            cvss_score=9.0,
            remediation="Use parameterized queries and input validation."
        )
        
    async def _create_mock_api_vulnerabilities(self, scan_id: PyObjectId) -> None:
        """Create mock API vulnerabilities."""
        await self._create_vulnerability(
            scan_id,
            name="Missing Rate Limiting",
            description="API lacks rate limiting controls.",
            severity=VulnerabilitySeverity.MEDIUM,
            affected_components=["/api/v1/users"],
            cvss_score=5.0,
            remediation="Implement rate limiting on all API endpoints."
        )
        
        await self._create_vulnerability(
            scan_id,
            name="Insecure Direct Object Reference",
            description="API allows access to resources by modifying ID parameter.",
            severity=VulnerabilitySeverity.HIGH,
            affected_components=["/api/v1/documents"],
            cvss_score=7.5,
            remediation="Implement proper authorization checks."
        )
        
    async def _create_mock_generic_vulnerabilities(self, scan_id: PyObjectId) -> None:
        """Create mock generic vulnerabilities."""
        severity_list = list(VulnerabilitySeverity)
        
        for i in range(3):
            severity = random.choice(severity_list)
            cvss = random.uniform(1.0, 10.0)
            
            await self._create_vulnerability(
                scan_id,
                name=f"Generic Vulnerability {i+1}",
                description=f"This is a generic vulnerability for testing.",
                severity=severity,
                affected_components=[f"component-{i}"],
                cvss_score=round(cvss, 1),
                remediation="Follow security best practices."
            )

    async def _create_vulnerability(
        self,
        scan_id: PyObjectId,
        name: str,
        description: str,
        severity: VulnerabilitySeverity,
        affected_components: Optional[List[str]] = None,
        cvss_score: Optional[float] = None,
        cve_ids: Optional[List[str]] = None,
        remediation: Optional[str] = None,
        references: Optional[List[str]] = None
    ) -> VulnerabilityInDB:
        """Create a vulnerability finding."""
        vuln_dict = {
            "scan_id": scan_id,
            "name": name,
            "description": description,
            "severity": severity,
            "affected_components": affected_components,
            "cvss_score": cvss_score,
            "cve_ids": cve_ids,
            "remediation": remediation,
            "references": references,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Insert vulnerability
        result = await self.db["vulnerabilities"].insert_one(vuln_dict)
        vuln_dict["_id"] = result.inserted_id

        # Update vulnerability counts
        await self.db["scans"].update_one(
            {"_id": scan_id},
            {
                "$inc": {f"vulnerability_counts.{severity}": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        return VulnerabilityInDB(**vuln_dict)

    async def _update_scan_progress(self, scan_id: PyObjectId, progress: float) -> None:
        """Update scan progress."""
        await self.db["scans"].update_one(
            {"_id": scan_id},
            {
                "$set": {
                    "progress": progress,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    async def get_scan(self, scan_id: str) -> Optional[ScanInDB]:
        """Get scan by ID."""
        if not ObjectId.is_valid(scan_id):
            return None
        scan_dict = await self.db["scans"].find_one({"_id": ObjectId(scan_id)})
        if not scan_dict:
            return None
        return ScanInDB(**scan_dict)

    async def get_scan_vulnerabilities(
        self,
        scan_id: str,
        severity: Optional[VulnerabilitySeverity] = None
    ) -> List[VulnerabilityInDB]:
        """Get vulnerabilities for a scan."""
        if not ObjectId.is_valid(scan_id):
            return []
            
        # Build query
        query = {"scan_id": ObjectId(scan_id)}
        if severity:
            query["severity"] = severity
            
        # Execute query
        cursor = self.db["vulnerabilities"].find(query)
        vulns = await cursor.to_list(length=100)
        
        # Convert to model objects
        return [VulnerabilityInDB(**vuln) for vuln in vulns]
        
    async def cancel_scan(self, scan_id: str) -> bool:
        """Cancel a running scan."""
        if scan_id in self.active_scans:
            self.active_scans[scan_id].cancel()
            self.active_scans.pop(scan_id)
            
            # Update scan status
            await self.db["scans"].update_one(
                {"_id": ObjectId(scan_id)},
                {
                    "$set": {
                        "status": ScanStatus.CANCELLED,
                        "end_time": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return True
        return False

    async def cleanup(self) -> None:
        """Cleanup scanner resources."""
        for task in self.active_scans.values():
            task.cancel()
        await asyncio.gather(*self.active_scans.values(), return_exceptions=True)
        self.active_scans.clear() 