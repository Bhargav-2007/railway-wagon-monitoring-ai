from fastapi import APIRouter, Depends, File, UploadFile, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from app.database import get_db
from app.models.frame import ProcessedFrame

router = APIRouter()

@router.post("/frames/process")
async def process_frame(
    file: UploadFile = File(...),
    camera_id: str = Query("default"),
    skip_heavy: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Process an uploaded frame"""
    try:
        # Import AI pipeline
        from ai_pipeline.pipelines.realtime_pipeline import RailwayMonitoringPipeline
        
        # Read image
        import cv2
        import numpy as np
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process with AI pipeline
        pipeline = RailwayMonitoringPipeline()
        result = pipeline.process_frame(frame, camera_id)
        
        # Save to database
        import json
        db_frame = ProcessedFrame(
            camera_id=camera_id,
            frame_timestamp=datetime.utcnow(),
            is_blurred=result.get('is_blurred', False),
            blur_score=result.get('blur_score', 0),
            was_deblurred=result.get('was_deblurred', False),
            was_enhanced=result.get('was_enhanced', False),
            num_wagons_detected=result.get('num_wagons', 0),
            wagon_ids=json.dumps(result.get('wagon_ids', [])),
            processing_time=result.get('processing_time', 0),
            fps=result.get('fps', 0)
        )
        db.add(db_frame)
        db.commit()
        db.refresh(db_frame)
        
        return {
            "frame_id": db_frame.id,
            "camera_id": camera_id,
            "is_blurred": result.get('is_blurred', False),
            "blur_score": result.get('blur_score', 0),
            "was_deblurred": result.get('was_deblurred', False),
            "was_enhanced": result.get('was_enhanced', False),
            "num_wagons": result.get('num_wagons', 0),
            "wagon_ids": result.get('wagon_ids', []),
            "processing_time": result.get('processing_time', 0),
            "fps": result.get('fps', 0),
            "timestamp": db_frame.created_at.isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/frames/recent")
async def get_recent_frames(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get recent processed frames"""
    import json
    frames = db.query(ProcessedFrame).order_by(desc(ProcessedFrame.created_at)).limit(limit).all()
    
    return [
        {
            "frame_id": f.id,
            "camera_id": f.camera_id,
            "is_blurred": f.is_blurred,
            "blur_score": f.blur_score,
            "was_deblurred": f.was_deblurred,
            "was_enhanced": f.was_enhanced,
            "num_wagons": f.num_wagons_detected,
            "wagon_ids": json.loads(f.wagon_ids) if f.wagon_ids else [],
            "processing_time": f.processing_time,
            "fps": f.fps,
            "timestamp": f.created_at.isoformat()
        }
        for f in frames
    ]
