from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class ScheduledPost(BaseModel):
    id: Optional[PyObjectId] = None
    user_id: str
    content: str
    scheduled_datetime: datetime
    timezone: Optional[str] = "Asia/Kolkata"
    status: str  # pending, published, failed
    linkedin_post_id: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}