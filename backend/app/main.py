from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.routers import auth, scan, pentest  # Temporarily remove report, dashboard, and vulnerability
from app.core.database import connect_to_mongo, close_mongo_connection, create_indexes
import logging
import time
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE_PATH)
    ]
)
logger = logging.getLogger("app")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Request ID middleware
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Add request_id to request state
    request.state.request_id = request_id
    
    # Log request details
    logger.info(f"Request started: id={request_id} method={request.method} path={request.url.path} client={request.client.host if request.client else 'unknown'}")
    
    try:
        response = await call_next(request)
        
        # Log response details
        process_time = time.time() - start_time
        logger.info(f"Request completed: id={request_id} status_code={response.status_code} process_time={process_time:.4f}s")
        
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.error(f"Request failed: id={request_id} error={str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now to ensure it works
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "X-Request-ID", "Authorization"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Database connection events
@app.on_event("startup")
async def startup_db_client():
    logger.info("Application starting up...")
    success = await connect_to_mongo()
    if success:
        await create_indexes()
        logger.info("Application startup completed successfully")
    else:
        logger.error("Application startup failed due to database connection issues")

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Application shutting down...")
    await close_mongo_connection()
    logger.info("Application shutdown completed")

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(scan.router, prefix=f"{settings.API_V1_STR}/scans", tags=["Scans"])
app.include_router(pentest.router, prefix=f"{settings.API_V1_STR}/pentests", tags=["Penetration Tests"])
# Temporarily disabled
# app.include_router(vulnerability.router, prefix=f"{settings.API_V1_STR}/vulnerabilities", tags=["Vulnerabilities"])
# app.include_router(report.router, prefix=f"{settings.API_V1_STR}/reports", tags=["Reports"])
# app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to NexaSec API", "status": "connected"}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API and database connection."""
    logger.info("Health check endpoint accessed")
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "database_connected": True,
        "environment": "development" if "localhost" in settings.MONGODB_URL else "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
