"""
Test script to verify imports without running the full application.
This helps identify import errors and circular dependencies.
"""
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("import_test")

def test_imports():
    """Test importing critical modules one by one to identify issues."""
    modules_to_test = [
        # Configuration
        "app.core.config",
        "app.core.database",
        
        # Base models
        "app.models.base",
        "app.models.user",
        "app.models.scan",
        "app.models.pentest",
        
        # Auth service
        "app.services.auth",
        
        # Main services
        "app.services.scanner",
        "app.services.pentester",
        
        # Routers (these would import other modules)
        "app.routers.auth",
        "app.routers.scan",
        "app.routers.pentest",
        "app.routers.dashboard",
        "app.routers.report",
        "app.routers.vulnerability",
        
        # Main app
        "app.main"
    ]
    
    success_count = 0
    failed_modules = []
    
    for module_name in modules_to_test:
        try:
            logger.info(f"Testing import of {module_name}")
            module = __import__(module_name, fromlist=['*'])
            logger.info(f"✅ Successfully imported {module_name}")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to import {module_name}: {str(e)}")
            failed_modules.append((module_name, str(e)))
    
    # Report results
    logger.info(f"\nImport test results:")
    logger.info(f"Total modules tested: {len(modules_to_test)}")
    logger.info(f"Successful imports: {success_count}")
    logger.info(f"Failed imports: {len(failed_modules)}")
    
    if failed_modules:
        logger.error("\nFailed modules:")
        for module_name, error in failed_modules:
            logger.error(f"  - {module_name}: {error}")
    else:
        logger.info("\n✅ All modules imported successfully!")

if __name__ == "__main__":
    logger.info("Starting import test")
    test_imports() 