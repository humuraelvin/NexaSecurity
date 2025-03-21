# Import routers for easier access
from app.routers.auth import router as auth_router
from app.routers.scan import router as scan_router
from app.routers.vulnerability import router as vulnerability_router
from app.routers.api_key import router as api_key_router

# Temporarily import missing routers as None to prevent errors
from fastapi import APIRouter

# Create placeholder routers for modules not yet implemented
# Use actual APIRouter objects to prevent 'has no attribute router' errors
pentest_router = APIRouter()
report_router = APIRouter()
dashboard_router = APIRouter() 