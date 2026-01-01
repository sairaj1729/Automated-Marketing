from pydantic import BaseModel, EmailStr, BeforeValidator
from typing import Optional, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId

def validate_object_id(v):
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str) and ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]

class UserSettings(BaseModel):
    notifications: Dict[str, bool] = {
        "postReminders": True,
        "engagementAlerts": True,
        "weeklyReports": True
    }
    linkedin_credentials: Optional[Dict[str, str]] = None
    theme: str = "dark"
    timezone: str = "UTC"

class User(BaseModel):
    id: Optional[PyObjectId] = None
    email: EmailStr
    hashed_password: str
    linkedin_token: Optional[str] = None
    linkedin_refresh_token: Optional[str] = None
    linkedin_profile: Optional[Dict[str, Any]] = None
    settings: UserSettings = UserSettings()
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}