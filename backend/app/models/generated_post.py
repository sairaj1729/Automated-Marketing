from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class GeneratedPost(BaseModel):
    id: Optional[PyObjectId] = None
    user_id: str
    topic: str
    tone: str
    audience: str
    url: Optional[str] = None
    generated_content: str
    created_at: datetime = datetime.now()
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}