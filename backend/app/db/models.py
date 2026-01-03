"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .base import Base


class Camera(Base):
    """Camera configuration"""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    url = Column(String(255), nullable=False)
    position = Column(String(50))  # entry, middle, exit
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    frames = relationship("ProcessedFrame", back_populates="camera", cascade="all, delete-orphan")


class ProcessedFrame(Base):
    """Processed frame metadata"""
    __tablename__ = "processed_frames"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    
    # Frame info
    frame_timestamp = Column(DateTime(timezone=True), nullable=False)
    frame_path = Column(String(500))
    processed_path = Column(String(500))
    
    # Processing results
    is_blurred = Column(Boolean)
    blur_score = Column(Float)
    was_deblurred = Column(Boolean, default=False)
    was_enhanced = Column(Boolean, default=False)
    
    # Detection results
    num_wagons_detected = Column(Integer, default=0)
    wagon_ids = Column(JSON)  # List of detected wagon IDs
    ocr_results = Column(JSON)  # Full OCR results
    damage_detected = Column(JSON)  # Damage detection results
    
    # Performance metrics
    processing_time = Column(Float)  # seconds
    fps = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    camera = relationship("Camera", back_populates="frames")
    wagon_detections = relationship("WagonDetection", back_populates="frame", cascade="all, delete-orphan")


class WagonDetection(Base):
    """Individual wagon detection"""
    __tablename__ = "wagon_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    frame_id = Column(Integer, ForeignKey("processed_frames.id", ondelete="CASCADE"), nullable=False)
    
    # Wagon info
    track_id = Column(Integer)
    wagon_number = Column(String(50))
    confidence = Column(Float)
    
    # Bounding box
    bbox_x1 = Column(Integer)
    bbox_y1 = Column(Integer)
    bbox_x2 = Column(Integer)
    bbox_y2 = Column(Integer)
    
    # Additional data - RENAMED from 'metadata' to 'extra_data'
    is_new = Column(Boolean, default=False)
    extra_data = Column(JSON)  # FIXED: renamed from 'metadata'
    
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    frame = relationship("ProcessedFrame", back_populates="wagon_detections")


class SystemMetrics(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metrics
    total_frames_processed = Column(Integer, default=0)
    total_wagons_detected = Column(Integer, default=0)
    avg_processing_time = Column(Float)
    avg_fps = Column(Float)
    
    # Quality metrics
    blur_detection_rate = Column(Float)
    ocr_success_rate = Column(Float)
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class Alert(Base):
    """System alerts and notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    alert_type = Column(String(50))  # blur, damage, system_error
    severity = Column(String(20))  # info, warning, error, critical
    message = Column(Text)
    details = Column(JSON)
    
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
