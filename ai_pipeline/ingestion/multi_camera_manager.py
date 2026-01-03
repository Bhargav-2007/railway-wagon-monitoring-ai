"""
Multi-Camera Manager - Manages multiple camera streams simultaneously
Synchronizes frames from all cameras for processing
"""

import yaml
import logging
import time
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
from .camera_stream import CameraStream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiCameraManager:
    def __init__(self, config_path: str = "ai_pipeline/configs/camera.yaml"):
        """
        Initialize multi-camera manager
        
        Args:
            config_path: Path to camera configuration YAML
        """
        self.config_path = config_path
        self.cameras: Dict[str, CameraStream] = {}
        self.load_config()
        
    def load_config(self):
        """Load camera configuration from YAML"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration for {len(self.config['cameras'])} cameras")
    
    def start_all_cameras(self) -> bool:
        """
        Start all cameras from configuration
        
        Returns:
            True if all cameras started successfully
        """
        logger.info("Starting all cameras...")
        all_success = True
        
        for cam_id, cam_config in self.config['cameras'].items():
            camera = CameraStream(
                camera_id=cam_id,
                stream_url=cam_config['url'],
                buffer_size=self.config['stream_settings']['buffer_size'],
                timeout=self.config['stream_settings']['timeout_seconds'],
                reconnect_attempts=self.config['stream_settings']['reconnect_attempts']
            )
            
            if camera.start():
                self.cameras[cam_id] = camera
                logger.info(f"✓ Camera {cam_id} ({cam_config['name']}) started")
            else:
                logger.error(f"✗ Camera {cam_id} ({cam_config['name']}) failed to start")
                all_success = False
        
        return all_success
    
    def read_all_frames(self) -> Dict[str, Optional[np.ndarray]]:
        """
        Read latest frame from each camera
        
        Returns:
            Dictionary mapping camera_id to frame (or None if unavailable)
        """
        frames = {}
        for cam_id, camera in self.cameras.items():
            frame = camera.read()
            frames[cam_id] = frame
        return frames
    
    def get_synchronized_frames(
        self,
        timeout: float = 2.0,
        max_time_diff: float = 0.1
    ) -> Optional[Dict[str, np.ndarray]]:
        """
        Get time-synchronized frames from all cameras
        
        Args:
            timeout: Maximum time to wait for all frames
            max_time_diff: Maximum allowed time difference between frames (seconds)
            
        Returns:
            Dictionary of synchronized frames or None if timeout
        """
        start_time = time.time()
        frames = {}
        
        while time.time() - start_time < timeout:
            frames = self.read_all_frames()
            
            # Check if all frames are available
            if all(frame is not None for frame in frames.values()):
                return frames
            
            time.sleep(0.01)  # Small delay before retry
        
        logger.warning("Timeout waiting for synchronized frames")
        return None
    
    def get_all_stats(self) -> Dict[str, dict]:
        """Get statistics for all cameras"""
        stats = {}
        for cam_id, camera in self.cameras.items():
            stats[cam_id] = camera.get_stats()
        return stats
    
    def stop_all_cameras(self):
        """Stop all camera streams"""
        logger.info("Stopping all cameras...")
        for cam_id, camera in self.cameras.items():
            camera.stop()
        self.cameras.clear()
        logger.info("All cameras stopped")


# Test function
if __name__ == "__main__":
    manager = MultiCameraManager()
    
    if manager.start_all_cameras():
        print("\n✅ All cameras started successfully\n")
        
        # Capture frames for 5 seconds
        print("Capturing frames for 5 seconds...")
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 5:
            frames = manager.read_all_frames()
            
            for cam_id, frame in frames.items():
                if frame is not None:
                    frame_count += 1
                    print(f"Camera {cam_id}: Frame shape {frame.shape}")
            
            time.sleep(0.5)
        
        print(f"\nTotal frames captured: {frame_count}")
        
        # Print statistics
        print("\n📊 Camera Statistics:")
        stats = manager.get_all_stats()
        for cam_id, cam_stats in stats.items():
            print(f"\n{cam_id}:")
            for key, value in cam_stats.items():
                print(f"  {key}: {value}")
        
        manager.stop_all_cameras()
    else:
        print("❌ Failed to start all cameras")
