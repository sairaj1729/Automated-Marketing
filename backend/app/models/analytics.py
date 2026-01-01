from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class AnalyticsData(BaseModel):
    id: Optional[PyObjectId] = None
    user_id: str
    metric_type: str  # views, engagement, followers, etc.
    value: float
    metadata: Optional[Dict[str, Any]] = None
    recorded_at: datetime = datetime.now()
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class HeatmapDataPoint(BaseModel):
    day: str
    hours: List[int]

class MetricDataPoint(BaseModel):
    label: str
    value: str
    change: str