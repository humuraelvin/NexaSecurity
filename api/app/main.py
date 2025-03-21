from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routers import auth, scan, network, vulnerabilities, pentests, dashboard, system, reports, settings
from .database.database import create_db_and_tables
from .database.migrate import migrate_users_table
import os
from dotenv import load_dotenv
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="NexaSecurity API",
    description="API for NexaSecurity Cybersecurity Platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ORIGIN", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
    expose_headers=["Content-Type", "Authorization"],
)

# Global exception handler for debugging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = str(exc)
    stack_trace = traceback.format_exc()
    logger.error(f"Global exception handler caught: {error_detail}\n{stack_trace}")
    return JSONResponse(
        status_code=500,
        content={"detail": error_detail, "stack_trace": stack_trace},
    )

# Include routers
app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(network.router)
app.include_router(vulnerabilities.router)
app.include_router(pentests.router)
app.include_router(dashboard.router)
app.include_router(system.router)
app.include_router(reports.router)
app.include_router(settings.router)

@app.on_event("startup")
async def startup():
    try:
        logger.info("Creating database and tables...")
        create_db_and_tables()
        logger.info("Database and tables created successfully")
        
        # Run migration to update existing schema
        logger.info("Running database migrations...")
        migrate_users_table()
        logger.info("Migrations completed")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Continue running, as tables might already exist

@app.get("/")
async def root():
    return {"status": "success", "message": "NexaSecurity API is running"} 