"""
Camera Stream Handler - Captures video from IP Webcam
Handles reconnection, frame buffering, and error recovery
Author: Member 1
"""

import cv2
import numpy as np
import time
import logging
from typing import Optional, Tuple, Dict
from threading import Thread, Lock
import queue

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CameraStream:
    """Thread-safe camera stream handler with automatic reconnection"""
    
    def __init__(
        self,
        camera_id: str,
        stream_url: str,
        buffer_size: int = 10,
        timeout: int = 5,
        reconnect_attempts: int = 3
    ):
        """
        Initialize camera stream
        
        Args:
            camera_id: Unique identifier for camera (e.g., "camera_1")
            stream_url: IP Webcam URL (e.g., "http://192.168.1.101:8080/video")
            buffer_size: Maximum frames to buffer before dropping old frames
            timeout: Connection timeout in seconds
            reconnect_attempts: Number of reconnection attempts on failure
        """
        self.camera_id = camera_id
        self.stream_url = stream_url
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.reconnect_attempts = reconnect_attempts
        
        # Thread-safe frame buffer
        self.frame_buffer = queue.Queue(maxsize=buffer_size)
        self.capture = None
        self.is_running = False
        self.thread = None
        self.lock = Lock()
        
        # Statistics
        self.frame_count = 0
        self.dropped_frames = 0
        self.error_count = 0
        self.start_time = None
        self.last_frame_time = None
        
    def start(self) -> bool:
        """
        Start camera stream capture in background thread
        
        Returns:
            bool: True if camera started successfully, False otherwise
        """
        if self.is_running:
            logger.warning(f"Camera {self.camera_id} already running")
            return True
            
        logger.info(f"Starting camera {self.camera_id} from {self.stream_url}")
        
        # Attempt initial connection
        for attempt in range(self.reconnect_attempts):
            try:
                self.capture = cv2.VideoCapture(self.stream_url)
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize latency
                
                if self.capture.isOpened():
                    # Test read
                    ret, test_frame = self.capture.read()
                    if ret and test_frame is not None:
                        self.is_running = True
                        self.start_time = time.time()
                        self.last_frame_time = self.start_time
                        
                        # Start capture thread
                        self.thread = Thread(target=self._capture_loop, daemon=True)
                        self.thread.start()
                        
                        logger.info(
                            f"✓ Camera {self.camera_id} started successfully "
                            f"(Resolution: {test_frame.shape[1]}x{test_frame.shape[0]})"
                        )
                        return True
                    else:
                        logger.warning(f"Camera {self.camera_id} opened but cannot read frames")
                        
            except Exception as e:
                logger.error(f"Camera {self.camera_id} connection error: {e}")
            
            logger.warning(
                f"Camera {self.camera_id} connection attempt {attempt + 1}/{self.reconnect_attempts} failed"
            )
            time.sleep(2)
        
        logger.error(f"✗ Failed to connect to camera {self.camera_id} after {self.reconnect_attempts} attempts")
        return False
    
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        consecutive_failures = 0
        max_consecutive_failures = 10
        
        while self.is_running:
            try:
                ret, frame = self.capture.read()
                
                if not ret or frame is None:
                    consecutive_failures += 1
                    self.error_count += 1
                    
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(
                            f"Camera {self.camera_id}: {consecutive_failures} consecutive frame read failures"
                        )
                        self._handle_reconnection()
                        consecutive_failures = 0
                    
                    time.sleep(0.1)
                    continue
                
                # Successful frame read
                consecutive_failures = 0
                self.frame_count += 1
                self.last_frame_time = time.time()
                
                # Add frame to buffer (non-blocking)
                try:
                    self.frame_buffer.put(frame, block=False)
                except queue.Full:
                    # Buffer full - drop oldest frame and add new one
                    self.dropped_frames += 1
                    try:
                        self.frame_buffer.get(block=False)
                        self.frame_buffer.put(frame, block=False)
                    except Exception as e:
                        logger.debug(f"Camera {self.camera_id}: Buffer management error: {e}")
                        
            except Exception as e:
                logger.error(f"Camera {self.camera_id} capture error: {e}")
                self.error_count += 1
                time.sleep(0.5)
    
    def _handle_reconnection(self):
        """Handle camera disconnection and attempt reconnection"""
        logger.warning(f"Camera {self.camera_id} disconnected, attempting reconnection...")
        
        # Release current capture
        if self.capture:
            try:
                self.capture.release()
            except:
                pass
        
        # Attempt reconnection
        for attempt in range(self.reconnect_attempts):
            time.sleep(2)
            
            try:
                self.capture = cv2.VideoCapture(self.stream_url)
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                if self.capture.isOpened():
                    ret, test_frame = self.capture.read()
                    if ret and test_frame is not None:
                        logger.info(f"✓ Camera {self.camera_id} reconnected successfully")
                        return
            except Exception as e:
                logger.error(f"Camera {self.camera_id} reconnection error: {e}")
        
        logger.error(f"✗ Camera {self.camera_id} reconnection failed - stopping stream")
        self.is_running = False
    
    def read(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Read latest frame from buffer
        
        Args:
            timeout: Maximum time to wait for frame in seconds
            
        Returns:
            Frame as numpy array (BGR format) or None if no frame available
        """
        if not self.is_running:
            return None
            
        try:
            frame = self.frame_buffer.get(timeout=timeout)
            return frame
        except queue.Empty:
            logger.debug(f"Camera {self.camera_id}: No frame available within timeout")
            return None
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """
        Get most recent frame, discarding all older buffered frames
        
        Returns:
            Most recent frame or None
        """
        latest_frame = None
        
        # Drain buffer to get latest
        while not self.frame_buffer.empty():
            try:
                latest_frame = self.frame_buffer.get(block=False)
            except queue.Empty:
                break
        
        return latest_frame
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get comprehensive camera stream statistics
        
        Returns:
            Dictionary containing stream statistics
        """
        current_time = time.time()
        
        if self.start_time and self.frame_count > 0:
            elapsed = current_time - self.start_time
            fps = self.frame_count / max(elapsed, 0.001)
            
            # Calculate time since last frame
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
        """
        Check if camera stream is healthy
        
        Args:
            max_time_since_frame: Maximum acceptable time since last frame (seconds)
            
        Returns:
            True if stream is healthy
        """
        if not self.is_running:
            return False
        
        if self.last_frame_time is None:
            return False
        
        time_since_last = time.time() - self.last_frame_time
        return time_since_last < max_time_since_frame
    
    def stop(self):
        """Stop camera stream and cleanup resources"""
        if not self.is_running:
            return
            
        logger.info(f"Stopping camera {self.camera_id}...")
        self.is_running = False
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        # Release capture
        if self.capture:
            try:
                self.capture.release()
            except:
                pass
        
        # Clear buffer
        while not self.frame_buffer.empty():
            try:
                self.frame_buffer.get(block=False)
            except:
                break
        
        logger.info(f"✓ Camera {self.camera_id} stopped (Total frames: {self.frame_count})")


# Test function
if __name__ == "__main__":
    import sys
    
    # Get camera URL from command line or use default
    if len(sys.argv) > 1:
        camera_url = sys.argv[1]
    else:
        camera_url = "http://192.168.1.101:8080/video"
        print(f"Usage: python camera_stream.py <camera_url>")
        print(f"Using default: {camera_url}\n")
    
    # Create and test camera
    camera = CameraStream(
        camera_id="test_camera",
        stream_url=camera_url,
        buffer_size=5
    )
    
    print(f"Testing camera stream from: {camera_url}\n")
    
    if camera.start():
        print("✅ Camera started successfully!\n")
        print("Capturing 20 frames...")
        
        for i in range(20):
            frame = camera.read(timeout=2.0)
            
            if frame is not None:
                print(f"  Frame {i+1:2d}: Shape {frame.shape}, Size {frame.nbytes} bytes")
                
                # Save first frame
                if i == 0:
                    output_path = "test_frame_captured.jpg"
                    cv2.imwrite(output_path, frame)
                    print(f"  → Saved first frame to: {output_path}")
            else:
                print(f"  Frame {i+1:2d}: ✗ No frame available")
            
            time.sleep(0.3)
        
        # Print final statistics
        print("\n📊 Final Statistics:")
        stats = camera.get_stats()
        for key, value in stats.items():
            print(f"  {key:25s}: {value}")
        
        print(f"\n  Health check: {'✓ Healthy' if camera.is_healthy() else '✗ Unhealthy'}")
        
        camera.stop()
        print("\n✅ Test completed successfully!")
        
    else:
        print("✗ Failed to start camera")
        print("\nTroubleshooting:")
        print("  1. Check if phone IP Webcam app is running")
        print("  2. Verify phone and PC are on same WiFi")
        print("  3. Test URL in browser: " + camera_url)
        print("  4. Check firewall settings")
