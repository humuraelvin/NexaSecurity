from fastapi import APIRouter, Depends
from ..core.security import get_current_user
from ..schemas.auth import User
from ..schemas.dashboard import SystemHealth
import psutil
import time
from datetime import datetime

router = APIRouter(
    prefix="/system",
    tags=["System"],
)

@router.get("/health", response_model=SystemHealth)
async def get_system_health(current_user: User = Depends(get_current_user)):
    """Get system health information"""
    try:
        # Get CPU, memory, and disk usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        # Get system uptime
        uptime = int(time.time() - psutil.boot_time())
        
        return SystemHealth(
            status="healthy" if all([cpu_percent < 80, memory_percent < 80, disk_percent < 80]) else "warning",
            cpu=round(cpu_percent, 1),
            memory=round(memory_percent, 1),
            disk=round(disk_percent, 1),
            uptime=uptime,
            lastUpdate=datetime.now().isoformat(),
            error=None
        )
    except Exception as e:
        return SystemHealth(
            status="error",
            cpu=0.0,
            memory=0.0,
            disk=0.0,
            uptime=0,
            lastUpdate=datetime.now().isoformat(),
            error=str(e)
        ) 