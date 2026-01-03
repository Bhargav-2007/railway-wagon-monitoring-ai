"""
Image Polling Stream - For cameras that only provide snapshot endpoints
Continuously polls /shot.jpg to simulate video stream
"""

import cv2
import numpy as np
import time
import logging
import requests
from typing import Optional, Dict
from threading import Thread, Lock
import queue
from io import BytesIO

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImagePollingStream:
    """Camera stream that polls static image endpoint"""
    
    def __init__(
        self,
        camera_id: str,
        snapshot_url: str,
        poll_interval: float = 0.033,  # ~30 FPS
        buffer_size: int = 10,
        timeout: int = 5
    ):
        """
        Initialize image polling stream
        
        Args:
            camera_id: Unique camera identifier
            snapshot_url: URL to snapshot image (e.g., http://IP:8080/shot.jpg)
            poll_interval: Time between image polls in seconds (default: 0.033 = 30fps)
            buffer_size: Maximum frames to buffer
            timeout: HTTP request timeout in seconds
        """
        self.camera_id = camera_id
        self.snapshot_url = snapshot_url
        self.poll_interval = poll_interval
        self.buffer_size = buffer_size
        self.timeout = timeout
        
        self.frame_buffer = queue.Queue(maxsize=buffer_size)
        self.is_running = False
        self.thread = None
        self.lock = Lock()
        
        # Statistics
        self.frame_count = 0
        self.dropped_frames = 0
        self.error_count = 0
        self.start_time = None
        self.last_frame_time = None
        
        # HTTP session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'RailwayWagonMonitor/1.0'})
        
    def start(self) -> bool:
        """Start image polling thread"""
        if self.is_running:
            logger.warning(f"Camera {self.camera_id} already running")
            return True
        
        logger.info(f"Starting camera {self.camera_id} from {self.snapshot_url}")
        
        # Test initial connection
        try:
            response = self.session.get(self.snapshot_url, timeout=self.timeout)
            if response.status_code == 200:
                # Try to decode image
                img_array = np.frombuffer(response.content, dtype=np.uint8)
                test_frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                if test_frame is not None:
                    self.is_running = True
                    self.start_time = time.time()
                    self.last_frame_time = self.start_time
                    
                    # Start polling thread
                    self.thread = Thread(target=self._polling_loop, daemon=True)
                    self.thread.start()
                    
                    logger.info(
                        f"✓ Camera {self.camera_id} started successfully "
                        f"(Resolution: {test_frame.shape[1]}x{test_frame.shape[0]}, "
                        f"Poll interval: {self.poll_interval:.3f}s)"
                    )
                    return True
                else:
                    logger.error(f"Camera {self.camera_id}: Cannot decode image")
            else:
                logger.error(
                    f"Camera {self.camera_id}: HTTP {response.status_code}"
                )
        except Exception as e:
            logger.error(f"Camera {self.camera_id} connection error: {e}")
        
        return False
    
    def _polling_loop(self):
        """Main polling loop in separate thread"""
        consecutive_failures = 0
        max_consecutive_failures = 10
        
        while self.is_running:
            loop_start = time.time()
            
            try:
                # Fetch image
                response = self.session.get(
                    self.snapshot_url,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    # Decode image
                    img_array = np.frombuffer(response.content, dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        # Successful frame
                        consecutive_failures = 0
                        self.frame_count += 1
                        self.last_frame_time = time.time()
                        
                        # Add to buffer
                        try:
                            self.frame_buffer.put(frame, block=False)
                        except queue.Full:
                            self.dropped_frames += 1
                            try:
                                self.frame_buffer.get(block=False)
                                self.frame_buffer.put(frame, block=False)
                            except:
                                pass
                    else:
                        consecutive_failures += 1
                        self.error_count += 1
                else:
                    consecutive_failures += 1
                    self.error_count += 1
                    logger.warning(
                        f"Camera {self.camera_id}: HTTP {response.status_code}"
                    )
                
            except Exception as e:
                consecutive_failures += 1
                self.error_count += 1
                logger.debug(f"Camera {self.camera_id} polling error: {e}")
            
            # Check for too many failures
            if consecutive_failures >= max_consecutive_failures:
                logger.error(
                    f"Camera {self.camera_id}: {consecutive_failures} "
                    f"consecutive failures - stopping"
                )
                self.is_running = False
                break
            
            # Maintain polling interval
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.poll_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def read(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """Read latest frame from buffer"""
        if not self.is_running:
            return None
        
        try:
            frame = self.frame_buffer.get(timeout=timeout)
            return frame
        except queue.Empty:
            return None
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get most recent frame, discarding older ones"""
        latest_frame = None
        while not self.frame_buffer.empty():
            try:
                latest_frame = self.frame_buffer.get(block=False)
            except queue.Empty:
                break
        return latest_frame
    
    def get_stats(self) -> Dict[str, any]:
        """Get stream statistics"""
        current_time = time.time()
        
        if self.start_time and self.frame_count > 0:
            elapsed = current_time - self.start_time
            fps = self.frame_count / max(elapsed, 0.001)
            
            if self.last_frame_time:
                time_since_last = current_time - self.last_frame_time
            else:
                time_since_last = 0
        else:
            fps = 0.0
            time_since_last = 0
        
        return {
            "camera_id": self.camera_id,
            "is_running": self.is_running,
            "frame_count": self.frame_count,
            "dropped_frames": self.dropped_frames,
            "error_count": self.error_count,
            "fps": round(fps, 2),
            "buffer_size": self.frame_buffer.qsize(),
            "time_since_last_frame": round(time_since_last, 2),
            "drop_rate_percent": round(
                (self.dropped_frames / max(self.frame_count, 1)) * 100, 2
            )
        }
    
    def is_healthy(self, max_time_since_frame: float = 5.0) -> bool:
        """Check if stream is healthy"""
        if not self.is_running:
            return False
        
        if self.last_frame_time is None:
            return False
        
        time_since_last = time.time() - self.last_frame_time
        return time_since_last < max_time_since_frame
    
    def stop(self):
        """Stop polling and cleanup"""
        if not self.is_running:
            return
        
        logger.info(f"Stopping camera {self.camera_id}...")
        self.is_running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        # Close session
        self.session.close()
        
        # Clear buffer
        while not self.frame_buffer.empty():
            try:
                self.frame_buffer.get(block=False)
            except:
                break
        
        logger.info(
            f"✓ Camera {self.camera_id} stopped "
            f"(Total frames: {self.frame_count})"
        )


# Test function
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        snapshot_url = sys.argv[1]
    else:
        snapshot_url = "http://192.168.1.8:8080/shot.jpg"
        print(f"Usage: python image_polling_stream.py <snapshot_url>")
        print(f"Using default: {snapshot_url}\n")
    
    # Create polling stream
    camera = ImagePollingStream(
        camera_id="polling_test",
        snapshot_url=snapshot_url,
        poll_interval=0.1,  # 10 FPS for testing
        buffer_size=5
    )
    
    print(f"Testing image polling from: {snapshot_url}\n")
    
    if camera.start():
        print("✅ Camera started successfully!\n")
        print("Capturing 20 frames...")
        
        for i in range(20):
            frame = camera.read(timeout=2.0)
            
            if frame is not None:
                print(
                    f"  Frame {i+1:2d}: Shape {frame.shape}, "
                    f"Size {frame.nbytes // 1024}KB"
                )
                
                # Save first frame
                if i == 0:
                    output_path = "test_polling_frame.jpg"
                    cv2.imwrite(output_path, frame)
                    print(f"  → Saved: {output_path}")
            else:
                print(f"  Frame {i+1:2d}: ✗ No frame")
            
            time.sleep(0.3)
        
        # Statistics
        print("\n📊 Final Statistics:")
        stats = camera.get_stats()
        for key, value in stats.items():
            print(f"  {key:25s}: {value}")
        
        print(
            f"\n  Health: "
            f"{'✓ Healthy' if camera.is_healthy() else '✗ Unhealthy'}"
        )
        
        camera.stop()
        print("\n✅ Test completed!")
    else:
        print("✗ Failed to start camera")
