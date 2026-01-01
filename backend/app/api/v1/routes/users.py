from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateSettings
from app.api.v1.deps import get_current_active_user
from app.config.database import db
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile
    """
    # Convert to response model
    user_response = UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        settings=current_user.settings,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    return user_response

@router.put("/me/settings", response_model=UserResponse)
async def update_user_settings(
    settings_update: UserUpdateSettings,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user settings
    """
    # Update user in database
    users_collection = db.get_collection("users")
    result = await users_collection.update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "settings": settings_update.settings.dict(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user settings"
        )
    
    # Return updated user
    updated_user = await users_collection.find_one({"_id": current_user.id})
    updated_user["id"] = str(updated_user["_id"])
    del updated_user["_id"]
    
    return UserResponse(**updated_user)