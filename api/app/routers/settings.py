from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..schemas.settings import UserSettings, NotificationPreferences, SecuritySettings
from ..core.security import get_current_user
from ..schemas.auth import User
from ..models.user import User as UserModel

router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
)

@router.put("/user")
async def update_user_settings(
    settings: UserSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user settings"""
    # Get the user from the database
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user settings
    user.name = settings.name
    user.email = settings.email
    user.company = settings.company
    
    # In a real application, you would update additional fields as well
    # and possibly have a separate user_settings table
    
    db.commit()
    
    return {"status": "success", "message": "User settings updated successfully"}

@router.put("/notifications")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences"""
    # In a real application, you would update these in the database
    # For now, just return success
    
    return {
        "status": "success",
        "message": "Notification preferences updated successfully",
        "preferences": preferences.dict()
    }

@router.put("/security")
async def update_security_settings(
    settings: SecuritySettings,
    current_user: User = Depends(get_current_user)
):
    """Update security settings"""
    # In a real application, you would update these in the database
    # For now, just return success
    
    return {
        "status": "success",
        "message": "Security settings updated successfully",
        "settings": settings.dict()
    } 