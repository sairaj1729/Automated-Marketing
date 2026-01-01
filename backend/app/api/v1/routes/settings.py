from fastapi import APIRouter, Depends
from app.models.user import User, UserSettings
from app.api.v1.deps import get_current_active_user
from app.config.database import db
from datetime import datetime

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/")
async def get_settings(current_user: User = Depends(get_current_active_user)):
    """
    Get current user settings
    """
    return current_user.settings

@router.put("/")
async def update_settings(settings: UserSettings, current_user: User = Depends(get_current_active_user)):
    """
    Update current user settings
    """
    # Update settings in database
    users_collection = db.get_collection("users")
    await users_collection.update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "settings": settings.dict(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return settings