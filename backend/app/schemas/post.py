from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostGenerateRequest(BaseModel):
    topic: str
    tone: str = "professional"
    audience: str
    url: Optional[str] = None

class PostGenerateResponse(BaseModel):
    post: str

class ScheduledPostCreate(BaseModel):
    content: str
    scheduled_datetime: datetime
    timezone: Optional[str] = "Asia/Kolkata"

class ScheduledPostUpdate(BaseModel):
    content: Optional[str] = None
    scheduled_datetime: Optional[datetime] = None
    timezone: Optional[str] = None
    status: Optional[str] = None

class ScheduledPostResponse(BaseModel):
    id: str
    user_id: str
    content: str
    scheduled_datetime: datetime
    timezone: Optional[str] = "Asia/Kolkata"
    status: str
    linkedin_post_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class LinkedInPostRequest(BaseModel):
    access_token: str
    member_urn: str
    content: str
    image_url: Optional[str] = None
