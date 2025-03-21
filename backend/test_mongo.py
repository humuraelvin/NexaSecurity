import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mongo_test")

async def test_mongo_connection():
    """Test MongoDB connection."""
    logger.info(f"Testing MongoDB connection to {settings.MONGODB_URL}")
    
    try:
        # Create client
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_NAME]
        
        # List collections
        collections = await db.list_collection_names()
        logger.info(f"Successfully connected to MongoDB. Collections: {collections}")
        
        # Test basic operations
        collection = db["test_collection"]
        
        # Insert a document
        result = await collection.insert_one({"test": "data", "status": "ok"})
        logger.info(f"Inserted document with ID: {result.inserted_id}")
        
        # Find the document
        doc = await collection.find_one({"_id": result.inserted_id})
        logger.info(f"Found document: {doc}")
        
        # Delete the document
        await collection.delete_one({"_id": result.inserted_id})
        logger.info("Deleted test document")
        
        # Close connection
        client.close()
        logger.info("MongoDB connection test completed successfully")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting MongoDB connection test")
    result = asyncio.run(test_mongo_connection())
    if result:
        logger.info("✅ MongoDB connection test passed")
    else:
        logger.error("❌ MongoDB connection test failed") 