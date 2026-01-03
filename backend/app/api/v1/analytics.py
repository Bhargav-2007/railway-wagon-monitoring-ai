from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional
import json

from app.database import get_db
from app.models.frame import ProcessedFrame

router = APIRouter()

@router.get("/summary")
async def get_analytics_summary(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get analytics summary for the last N hours"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Total frames
        total_frames = db.query(func.count(ProcessedFrame.id)).filter(
            ProcessedFrame.created_at >= cutoff_time
        ).scalar() or 0
        
        # Total wagons - count frames that have wagon_ids
        frames_with_wagons = db.query(ProcessedFrame).filter(
            and_(
                ProcessedFrame.created_at >= cutoff_time,
                ProcessedFrame.wagon_ids.isnot(None),
                ProcessedFrame.wagon_ids != '[]'
            )
        ).all()
        
        total_wagons = 0
        for frame in frames_with_wagons:
            try:
                wagon_list = json.loads(frame.wagon_ids) if isinstance(frame.wagon_ids, str) else frame.wagon_ids
                if wagon_list:
                    total_wagons += len(wagon_list)
            except:
                pass
        
        # Average processing time and FPS
        avg_stats = db.query(
            func.avg(ProcessedFrame.processing_time).label('avg_time'),
            func.avg(ProcessedFrame.fps).label('avg_fps')
        ).filter(
            ProcessedFrame.created_at >= cutoff_time
        ).first()
        
        avg_processing_time = float(avg_stats.avg_time or 0) if avg_stats else 0
        avg_fps = float(avg_stats.avg_fps or 0) if avg_stats else 0
        
        # Blur detection rate
        blurred_count = db.query(func.count(ProcessedFrame.id)).filter(
            and_(
                ProcessedFrame.created_at >= cutoff_time,
                ProcessedFrame.is_blurred == True
            )
        ).scalar() or 0
        
        blur_detection_rate = (blurred_count / total_frames * 100) if total_frames > 0 else 0
        
        # OCR success rate (frames with non-empty wagon_ids)
        ocr_success_count = len(frames_with_wagons)
        ocr_success_rate = (ocr_success_count / total_frames * 100) if total_frames > 0 else 0
        
        return {
            "total_frames": total_frames,
            "total_wagons": total_wagons,
            "avg_processing_time": round(avg_processing_time, 3),
            "avg_fps": round(avg_fps, 2),
            "blur_detection_rate": round(blur_detection_rate, 2),
            "ocr_success_rate": round(ocr_success_rate, 2),
            "time_period": f"Last {hours} hours"
        }
    
    except Exception as e:
        return {
            "total_frames": 0,
            "total_wagons": 0,
            "avg_processing_time": 0,
            "avg_fps": 0,
            "blur_detection_rate": 0,
            "ocr_success_rate": 0,
            "time_period": f"Last {hours} hours"
        }

@router.get("/camera/{camera_id}")
async def get_camera_analytics(
    camera_id: str,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific camera"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    total_frames = db.query(func.count(ProcessedFrame.id)).filter(
        and_(
            ProcessedFrame.camera_id == camera_id,
            ProcessedFrame.created_at >= cutoff_time
        )
    ).scalar()
    
    avg_stats = db.query(
        func.avg(ProcessedFrame.processing_time).label('avg_time'),
        func.avg(ProcessedFrame.fps).label('avg_fps')
    ).filter(
        and_(
            ProcessedFrame.camera_id == camera_id,
            ProcessedFrame.created_at >= cutoff_time
        )
    ).first()
    
    return {
        "camera_id": camera_id,
        "total_frames": total_frames or 0,
        "avg_processing_time": float(avg_stats.avg_time or 0) if avg_stats else 0,
        "avg_fps": float(avg_stats.avg_fps or 0) if avg_stats else 0,
        "time_period": f"Last {hours} hours"
    }
