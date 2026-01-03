from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2
import asyncio
import io
import sys
import os
from typing import Optional
import numpy as np

# Add ai_pipeline to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

router = APIRouter()

# Import camera manager
try:
    from app.camera_manager import camera_manager
    print("✓ Camera manager imported")
except Exception as e:
    print(f"⚠ Camera manager import failed: {e}")
    camera_manager = None

# Import AI pipeline
try:
    from ai_pipeline.pipelines.realtime_pipeline import RailwayMonitoringPipeline
    ai_pipeline = RailwayMonitoringPipeline()
    print("✓ AI Pipeline initialized for streaming")
except Exception as e:
    print(f"⚠ Failed to initialize AI pipeline: {e}")
    ai_pipeline = None

class CameraConfig(BaseModel):
    camera_id: str
    ip_address: str
    port: int = 8080
    position: str = "unknown"

@router.post("/cameras/add")
async def add_camera(config: CameraConfig):
    """Add a new IP camera"""
    if not camera_manager:
        raise HTTPException(status_code=500, detail="Camera manager not available")
    
    camera_manager.add_camera(
        camera_id=config.camera_id,
        ip_address=config.ip_address,
        port=config.port
    )
    return {
        "status": "success",
        "message": f"Camera {config.camera_id} added",
        "camera": config.dict()
    }

@router.post("/cameras/{camera_id}/start")
async def start_camera(camera_id: str):
    """Start streaming from a camera"""
    if not camera_manager:
        raise HTTPException(status_code=500, detail="Camera manager not available")
    
    success = camera_manager.start_stream(camera_id)
    if success:
        return {"status": "success", "message": f"Camera {camera_id} started"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to start camera {camera_id}")

@router.post("/cameras/{camera_id}/stop")
async def stop_camera(camera_id: str):
    """Stop streaming from a camera"""
    if not camera_manager:
        raise HTTPException(status_code=500, detail="Camera manager not available")
    
    camera_manager.stop_stream(camera_id)
    return {"status": "success", "message": f"Camera {camera_id} stopped"}

@router.get("/cameras")
async def list_cameras():
    """List all cameras and their status"""
    if not camera_manager:
        return {"cameras": {}, "total": 0}
    
    return {
        "cameras": camera_manager.get_all_cameras(),
        "total": len(camera_manager.cameras)
    }

@router.get("/cameras/{camera_id}/snapshot")
async def get_snapshot(camera_id: str):
    """Get a single frame from camera"""
    if not camera_manager:
        raise HTTPException(status_code=500, detail="Camera manager not available")
    
    frame = camera_manager.get_frame(camera_id)
    
    if frame is None:
        raise HTTPException(status_code=404, detail=f"No frame available from {camera_id}")
    
    # Process frame with AI pipeline if available
    if ai_pipeline:
        try:
            result = ai_pipeline.process_frame(frame, camera_id)
            if result.get('visualization') is not None:
                frame = result['visualization']
        except Exception as e:
            print(f"Error processing frame: {e}")
    
    # Encode frame as JPEG
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        raise HTTPException(status_code=500, detail="Failed to encode frame")
    
    return StreamingResponse(
        io.BytesIO(buffer.tobytes()),
        media_type="image/jpeg"
    )

async def generate_frames(camera_id: str):
    """Generate frames for video streaming"""
    while True:
        if not camera_manager:
            break
            
        frame = camera_manager.get_frame(camera_id)
        
        if frame is None:
            await asyncio.sleep(0.1)
            continue
        
        # Process with AI pipeline
        if ai_pipeline:
            try:
                result = ai_pipeline.process_frame(frame, camera_id)
                if result.get('visualization') is not None:
                    frame = result['visualization']
            except Exception as e:
                print(f"Error processing frame: {e}")
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
        if not ret:
            continue
        
        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        await asyncio.sleep(0.033)  # ~30 FPS

@router.get("/cameras/{camera_id}/stream")
async def stream_camera(camera_id: str):
    """Stream video from camera with AI processing"""
    if not camera_manager:
        raise HTTPException(status_code=500, detail="Camera manager not available")
    
    if camera_id not in camera_manager.active_streams:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not active")
    
    return StreamingResponse(
        generate_frames(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/cameras/{camera_id}/stats")
async def get_camera_stats(camera_id: str):
    """Get processing stats for a camera"""
    if not camera_manager:
        raise HTTPException(status_code=500, detail="Camera manager not available")
    
    frame = camera_manager.get_frame(camera_id)
    
    if frame is None:
        raise HTTPException(status_code=404, detail=f"No frame available from {camera_id}")
    
    if not ai_pipeline:
        return {"error": "AI pipeline not available"}
    
    try:
        result = ai_pipeline.process_frame(frame, camera_id)
        return {
            "camera_id": camera_id,
            "blur_detected": result.get('is_blurred', False),
            "blur_score": result.get('blur_score', 0),
            "num_wagons": result.get('num_wagons', 0),
            "wagon_ids": result.get('wagon_ids', []),
            "processing_time": result.get('processing_time', 0),
            "fps": result.get('fps', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
