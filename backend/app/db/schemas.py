"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Camera Schemas
class CameraBase(BaseModel):
    camera_id: str
    name: str
    url: str
    position: Optional[str] = None


class CameraCreate(CameraBase):
    pass


class CameraResponse(CameraBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Frame Processing Schemas
class FrameProcessRequest(BaseModel):
    camera_id: str
    skip_heavy: bool = False


class WagonDetectionSchema(BaseModel):
    track_id: int
    wagon_number: Optional[str] = None
    confidence: float
    bbox: List[int]


class FrameProcessResponse(BaseModel):
    frame_id: int
    camera_id: str
    is_blurred: bool
    blur_score: float
    was_deblurred: bool
    was_enhanced: bool
    num_wagons: int
    wagon_ids: List[str]
    processing_time: float
    fps: float
    timestamp: datetime


# Analytics Schemas
class AnalyticsResponse(BaseModel):
    total_frames: int
    total_wagons: int
    avg_processing_time: float
    avg_fps: float
    blur_detection_rate: float
    ocr_success_rate: float
    time_period: str


class SystemHealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    ai_pipeline: str
    cameras_active: int
    uptime_seconds: float


# Alert Schemas
class AlertCreate(BaseModel):
    alert_type: str
    severity: str
    message: str
    details: Optional[Dict[str, Any]] = None


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    is_resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
