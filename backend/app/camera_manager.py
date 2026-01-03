import cv2
import asyncio
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class IPCameraManager:
    def __init__(self):
        self.cameras: Dict[str, dict] = {}
        self.active_streams: Dict[str, cv2.VideoCapture] = {}
    
    def add_camera(self, camera_id: str, ip_address: str, port: int = 8080):
        """Add an IP camera to the manager"""
        # IP Webcam video stream URL format
        stream_url = f"http://{ip_address}:{port}/video"
        
        self.cameras[camera_id] = {
            "ip": ip_address,
            "port": port,
            "stream_url": stream_url,
            "status": "inactive",
            "last_frame": None,
            "last_update": None
        }
        
        logger.info(f"Added camera {camera_id} at {stream_url}")
    
    def start_stream(self, camera_id: str) -> bool:
        """Start streaming from a camera"""
        if camera_id not in self.cameras:
            logger.error(f"Camera {camera_id} not found")
            return False
        
        camera_info = self.cameras[camera_id]
        
        try:
            cap = cv2.VideoCapture(camera_info["stream_url"])
            
            if not cap.isOpened():
                logger.error(f"Failed to open stream for {camera_id}")
                return False
            
            self.active_streams[camera_id] = cap
            self.cameras[camera_id]["status"] = "active"
            logger.info(f"Started stream for {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream for {camera_id}: {e}")
            return False
    
    def stop_stream(self, camera_id: str):
        """Stop streaming from a camera"""
        if camera_id in self.active_streams:
            self.active_streams[camera_id].release()
            del self.active_streams[camera_id]
            self.cameras[camera_id]["status"] = "inactive"
            logger.info(f"Stopped stream for {camera_id}")
    
    def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """Get the latest frame from a camera"""
        if camera_id not in self.active_streams:
            return None
        
        try:
            cap = self.active_streams[camera_id]
            ret, frame = cap.read()
            
            if ret:
                self.cameras[camera_id]["last_frame"] = frame
                self.cameras[camera_id]["last_update"] = datetime.utcnow()
                return frame
            else:
                logger.warning(f"Failed to read frame from {camera_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting frame from {camera_id}: {e}")
            return None
    
    def get_all_cameras(self) -> Dict[str, dict]:
        """Get info about all cameras"""
        return {
            cam_id: {
                "ip": info["ip"],
                "port": info["port"],
                "status": info["status"],
                "last_update": info["last_update"].isoformat() if info["last_update"] else None
            }
            for cam_id, info in self.cameras.items()
        }
    
    def cleanup(self):
        """Release all camera streams"""
        for camera_id in list(self.active_streams.keys()):
            self.stop_stream(camera_id)

# Global camera manager instance
camera_manager = IPCameraManager()
