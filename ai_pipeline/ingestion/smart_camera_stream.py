"""
Smart Camera Stream - Auto-detects best connection method
Tries video stream first, falls back to image polling if needed
"""

import logging
from typing import Optional
import numpy as np
from camera_stream import CameraStream
from image_polling_stream import ImagePollingStream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartCameraStream:
    """Auto-detecting camera stream wrapper"""
    
    def __init__(self, camera_id: str, base_url: str, **kwargs):
        """
        Initialize smart camera stream
        
        Args:
            camera_id: Camera identifier
            base_url: Base URL (e.g., http://192.168.1.8:8080)
            **kwargs: Additional parameters passed to stream handlers
        """
        self.camera_id = camera_id
        self.base_url = base_url.rstrip('/')
        self.kwargs = kwargs
        self.stream = None
        self.stream_type = None
        
    def start(self) -> bool:
        """Auto-detect and start best stream method"""
        
        # Try video stream endpoints first
        video_endpoints = ['/video', '/videofeed', '/mjpegfeed']
        
        for endpoint in video_endpoints:
            video_url = f"{self.base_url}{endpoint}"
            logger.info(f"Trying video stream: {video_url}")
            
            stream = CameraStream(
                camera_id=self.camera_id,
                stream_url=video_url,
                reconnect_attempts=1,  # Quick fail for testing
                **self.kwargs
            )
            
            if stream.start():
                # Test if actually getting frames
                import time
                time.sleep(1)
                
                if stream.is_healthy():
                    self.stream = stream
                    self.stream_type = "video"
                    logger.info(
                        f"✓ Using video stream for {self.camera_id}: {video_url}"
                    )
                    return True
                else:
                    stream.stop()
        
        # Fall back to image polling
        logger.info(f"Video streams failed, trying image polling...")
        snapshot_url = f"{self.base_url}/shot.jpg"
        
        stream = ImagePollingStream(
            camera_id=self.camera_id,
            snapshot_url=snapshot_url,
            poll_interval=0.033,  # 30 FPS
            **self.kwargs
        )
        
        if stream.start():
            self.stream = stream
            self.stream_type = "polling"
            logger.info(
                f"✓ Using image polling for {self.camera_id}: {snapshot_url}"
            )
            return True
        
        logger.error(f"✗ All connection methods failed for {self.camera_id}")
        return False
    
    def read(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """Read frame from underlying stream"""
        if self.stream:
            return self.stream.read(timeout)
        return None
    
    def get_stats(self):
        """Get stream statistics"""
        if self.stream:
            stats = self.stream.get_stats()
            stats['stream_type'] = self.stream_type
            return stats
        return {}
    
    def is_healthy(self) -> bool:
        """Check stream health"""
        if self.stream:
            return self.stream.is_healthy()
        return False
    
    def stop(self):
        """Stop stream"""
        if self.stream:
            self.stream.stop()


# Test
if __name__ == "__main__":
    import sys
    import time
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.1.8:8080"
    
    camera = SmartCameraStream("smart_test", base_url)
    
    if camera.start():
        print("✅ Camera started!\n")
        
        for i in range(10):
            frame = camera.read()
            if frame is not None:
                print(f"Frame {i+1}: {frame.shape}")
            time.sleep(0.5)
        
        print(f"\nStats: {camera.get_stats()}")
        camera.stop()
