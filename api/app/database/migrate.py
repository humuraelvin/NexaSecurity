"""
Database migration script to update schema from old structure to new structure.
This script should be run once to update the database schema.
"""
import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nexasecurity.db")

def migrate_users_table():
    """
    Migrate the users table to use the new schema with full_name, company_name, subscription_tier and is_active
    """
    # For SQLite database
    if DATABASE_URL.startswith("sqlite"):
        try:
            # Connect to the SQLite database
            db_path = DATABASE_URL.replace("sqlite:///", "")
            if ":" in db_path:  # Handle absolute paths on Windows
                db_path = db_path.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if the users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                logger.info("Users table doesn't exist yet. No migration needed.")
                conn.close()
                return
            
            # Check if we need to migrate
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Determine if we need to migrate from old schema
            needs_migration = ('name' in columns and 'full_name' not in columns) or \
                              ('company' in columns and 'company_name' not in columns) or \
                              ('plan' in columns and 'subscription_tier' not in columns) or \
                              'is_active' not in columns
            
            if needs_migration:
                logger.info("Migrating users table...")
                
                # Add new columns if they don't exist
                if "full_name" not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
                
                if "company_name" not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN company_name TEXT")
                
                if "subscription_tier" not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN subscription_tier TEXT DEFAULT 'basic'")
                
                if "is_active" not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
                
                # Copy data from old columns to new ones if both exist
                if "name" in columns and "full_name" in columns:
                    cursor.execute("UPDATE users SET full_name = name WHERE full_name IS NULL")
                
                if "company" in columns and "company_name" in columns:
                    cursor.execute("UPDATE users SET company_name = company WHERE company_name IS NULL")
                
                if "plan" in columns and "subscription_tier" in columns:
                    cursor.execute("UPDATE users SET subscription_tier = plan WHERE subscription_tier IS NULL")
                
                # Set is_active for all users if it exists
                if "is_active" in columns:
                    cursor.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")
                
                logger.info("Users table migrated successfully.")
            else:
                logger.info("Users table already has the new schema or is empty. No migration needed.")
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Migration error: {e}")
    
    # For other SQL databases (PostgreSQL, MySQL, etc.)
    else:
        try:
            engine = create_engine(DATABASE_URL)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Check if users table exists
            result = session.execute(text("SELECT to_regclass('public.users')"))
            if result.scalar() is None:
                logger.info("Users table doesn't exist yet. No migration needed.")
                session.close()
                return
            
            # Check table structure
            columns_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND table_schema = 'public'
            """)
            result = session.execute(columns_query)
            columns = [row[0] for row in result]
            
            # Determine if we need to migrate from old schema
            needs_migration = ('name' in columns and 'full_name' not in columns) or \
                              ('company' in columns and 'company_name' not in columns) or \
                              ('plan' in columns and 'subscription_tier' not in columns) or \
                              'is_active' not in columns
            
            if needs_migration:
                logger.info("Migrating users table...")
                
                # Add new columns if they don't exist
                if "full_name" not in columns:
                    session.execute(text("ALTER TABLE users ADD COLUMN full_name TEXT"))
                
                if "company_name" not in columns:
                    session.execute(text("ALTER TABLE users ADD COLUMN company_name TEXT"))
                
                if "subscription_tier" not in columns:
                    session.execute(text("ALTER TABLE users ADD COLUMN subscription_tier TEXT DEFAULT 'basic'"))
                
                if "is_active" not in columns:
                    session.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                
                # Copy data from old columns to new ones if both exist
                if "name" in columns and "full_name" in columns:
                    session.execute(text("UPDATE users SET full_name = name WHERE full_name IS NULL"))
                
                if "company" in columns and "company_name" in columns:
                    session.execute(text("UPDATE users SET company_name = company WHERE company_name IS NULL"))
                
                if "plan" in columns and "subscription_tier" in columns:
                    session.execute(text("UPDATE users SET subscription_tier = plan WHERE subscription_tier IS NULL"))
                
                # Set is_active for all users if it exists
                if "is_active" in columns:
                    session.execute(text("UPDATE users SET is_active = TRUE WHERE is_active IS NULL"))
                
                logger.info("Users table migrated successfully.")
            else:
                logger.info("Users table already has the new schema or is empty. No migration needed.")
            
            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Migration error: {e}")
    
if __name__ == "__main__":
    migrate_users_table() 