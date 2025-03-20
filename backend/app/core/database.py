from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

class MongoDB:
    client: AsyncIOMotorClient = None
    db: Database = None

db = MongoDB()

async def get_database() -> Database:
    if db.db is None:
        logger.error("Database not initialized. Make sure connect_to_mongo was called.")
    else:
        logger.debug("Database connection accessed")
    return db.db

async def connect_to_mongo():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.db = db.client[settings.MONGODB_DB_NAME]
        
        # Test connection by listing collections
        collections = await db.db.list_collection_names()
        logger.info(f"Successfully connected to MongoDB. Available collections: {collections}")
        
        # Count documents in collections for verification
        for collection_name in COLLECTIONS.values():
            count = await db.db[collection_name].count_documents({})
            logger.info(f"Collection '{collection_name}' has {count} documents")
            
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        return False

async def close_mongo_connection():
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        logger.info("MongoDB connection closed")

# Collection names for easy reference
COLLECTIONS = {
    "users": "users",
    "scans": "scans",
    "vulnerabilities": "vulnerabilities",
    "pentests": "pentests",
    "findings": "findings",
    "reports": "reports",
    "report_templates": "report_templates",
    "api_keys": "api_keys",
    "refresh_tokens": "refresh_tokens"
}

# Indexes to be created on startup
INDEXES = {
    "users": [
        [("email", 1)],  # Unique index on email
        [("username", 1)]  # Unique index on username
    ],
    "scans": [
        [("user_id", 1)],  # Index for user's scans
        [("created_at", -1)]  # Index for sorting by creation date
    ],
    "vulnerabilities": [
        [("scan_id", 1)],  # Index for scan's vulnerabilities
        [("severity", 1)]  # Index for filtering by severity
    ],
    "pentests": [
        [("user_id", 1)],  # Index for user's pentests
        [("created_at", -1)]  # Index for sorting by creation date
    ],
    "findings": [
        [("pentest_id", 1)],  # Index for pentest's findings
        [("severity", 1)]  # Index for filtering by severity
    ],
    "reports": [
        [("user_id", 1)],  # Index for user's reports
        [("created_at", -1)]  # Index for sorting by creation date
    ],
    "api_keys": [
        [("user_id", 1)],  # Index for user's API keys
        [("key", 1)]  # Unique index on API key
    ],
    "refresh_tokens": [
        [("user_id", 1)],  # Index for user's refresh tokens
        [("expires_at", 1)]  # Index for token expiration
    ]
}

async def create_indexes():
    """Create all required indexes on startup"""
    logger.info("Creating MongoDB indexes...")
    try:
        for collection_name, indexes in INDEXES.items():
            collection = db.db[collection_name]
            for index in indexes:
                index_name = await collection.create_index(index)
                logger.info(f"Created index '{index_name}' on collection '{collection_name}'")
        logger.info("All indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}") 