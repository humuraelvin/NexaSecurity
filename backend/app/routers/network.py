from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.schemas import NetworkMap, UserInDB
from backend.services import NetworkService
from backend.utils import get_current_user, get_database
from backend.utils import logger

router = APIRouter()

@router.get("/map", response_model=NetworkMap)
async def get_network_map(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """Get network map data."""
    try:
        network_data = await NetworkService.get_network_map(db, str(current_user.id))
        return network_data
    except Exception as e:
        logger.error(f"Error getting network map: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get network map"
        ) 