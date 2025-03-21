#!/usr/bin/env python3
"""
Migration script for NexaSecurity API.
Run this script to migrate the database schema.
"""
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database.migrate import migrate_users_table
    
    logger.info("Starting migration...")
    migrate_users_table()
    logger.info("Migration completed successfully.")
except Exception as e:
    logger.error(f"Migration failed: {e}")
    sys.exit(1) 