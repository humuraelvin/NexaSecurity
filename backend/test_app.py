from fastapi import FastAPI
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_app")

app = FastAPI(title="Test App")

@app.get("/")
async def root():
    return {"message": "Test app running"}

# First test if we can import the models
logger.info("Testing model imports...")
try:
    from app.models.scan import (
        ScanType, ScanStatus, ScanCreate, ScanInDB, 
        VulnerabilityInDB, VulnerabilitySeverity, VulnerabilityResponse
    )
    logger.info("Model imports successful")
except Exception as e:
    logger.error(f"Error importing models: {str(e)}")
    raise

# Try importing the router directly
logger.info("Testing router import...")
try:
    from app.routers.scan import router as scan_router
    app.include_router(scan_router, prefix="/api/v1/scans", tags=["Scans"])
    logger.info("Router import successful")
except Exception as e:
    logger.error(f"Error importing router: {str(e)}")
    raise

# Run the app
if __name__ == "__main__":
    logger.info("Starting test app...")
    uvicorn.run("test_app:app", host="0.0.0.0", port=8001, reload=False) 