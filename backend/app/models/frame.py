from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class ProcessedFrame(Base):
    __tablename__ = "processed_frames"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True)
    frame_timestamp = Column(DateTime)
    frame_path = Column(String, nullable=True)
    processed_path = Column(String, nullable=True)
    
    # Blur detection results
    is_blurred = Column(Boolean, default=False)
    blur_score = Column(Float, default=0.0)
    was_deblurred = Column(Boolean, default=False)
    was_enhanced = Column(Boolean, default=False)
    
    # Wagon detection results
    num_wagons_detected = Column(Integer, default=0)
    wagon_ids = Column(Text, nullable=True)  # JSON string
    ocr_results = Column(Text, nullable=True)  # JSON string
    
    # Damage detection (future feature)
    damage_detected = Column(Boolean, default=False)
    
    # Performance metrics
    processing_time = Column(Float, default=0.0)
    fps = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
