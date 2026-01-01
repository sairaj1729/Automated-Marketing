from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.analytics import HeatmapDataPoint, MetricDataPoint

class AnalyticsResponse(BaseModel):
    metrics: List[MetricDataPoint]
    heatmap_data: List[HeatmapDataPoint]

class MetricData(BaseModel):
    label: str
    value: str
    change: str

class HeatmapData(BaseModel):
    day: str
    hours: List[int]