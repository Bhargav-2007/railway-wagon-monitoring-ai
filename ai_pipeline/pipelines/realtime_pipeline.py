import cv2
import numpy as np
import time
import sys
import os
from typing import Dict, Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_pipeline.modules.blur_detection import BlurDetector
from ai_pipeline.modules.wagon_detection import WagonDetector
from ai_pipeline.modules.wagon_tracker import WagonTracker

class RailwayMonitoringPipeline:
    def __init__(self, blur_threshold: float = 120.0, use_cnn: bool = False):
        """
        Initialize pipeline with balanced threshold
        
        Args:
            blur_threshold: 120.0 is balanced (adjust based on testing)
                          - Lower (80-100): More sensitive to blur
                          - Higher (150-200): Less sensitive
        """
        print("\nInitializing Railway Monitoring Pipeline...\n")
        
        self.blur_threshold = blur_threshold
        self.blur_detector = BlurDetector(threshold=blur_threshold)
        print(f"  ✓ Blur detector (threshold: {blur_threshold})")
        
        self.wagon_detector = WagonDetector()
        print("  ✓ Wagon detector")
        
        self.wagon_tracker = WagonTracker()
        print("  ✓ Wagon tracker")
        
        print("\n✓ Pipeline initialized\n")
    
    def process_frame(self, frame: np.ndarray, camera_id: str = "default") -> Dict:
        """Process a single frame"""
        start_time = time.time()
        
        # 1. Blur Detection
        blur_result = self.blur_detector.detect_blur(frame)
        is_blurred = blur_result['is_blurred']
        blur_score = blur_result['blur_score']
        quality = blur_result.get('quality', 'Unknown')
        
        # 2. Wagon Detection
        wagons = self.wagon_detector.detect_wagons(frame)
        num_wagons = len(wagons)
        
        # 3. Wagon Tracking
        tracked_wagons = self.wagon_tracker.update(wagons, camera_id)
        wagon_ids = [w.get('wagon_id', '') for w in tracked_wagons if w.get('wagon_id')]
        
        # 4. Visualization
        vis_frame = frame.copy()
        
        # Draw blur status with quality indicator
        color = (0, 0, 255) if is_blurred else (0, 255, 0)
        status_text = f"{'BLURRED' if is_blurred else 'SHARP'} - {quality}"
        cv2.putText(vis_frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Draw score
        score_text = f"Score: {blur_score:.1f}"
        cv2.putText(vis_frame, score_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw wagon boxes
        for i, wagon in enumerate(wagons):
            x, y, w, h = wagon['bbox']
            cv2.rectangle(vis_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            label = f"Wagon {i+1}"
            if i < len(wagon_ids) and wagon_ids[i]:
                label += f": {wagon_ids[i]}"
            
            cv2.putText(vis_frame, label, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Add wagon count
        cv2.putText(vis_frame, f"Wagons: {num_wagons}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Calculate timing
        processing_time = time.time() - start_time
        fps = 1.0 / processing_time if processing_time > 0 else 0
        
        cv2.putText(vis_frame, f"FPS: {fps:.1f}", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return {
            'camera_id': camera_id,
            'is_blurred': is_blurred,
            'blur_score': blur_score,
            'quality': quality,
            'was_deblurred': False,
            'was_enhanced': False,
            'num_wagons': num_wagons,
            'wagon_ids': wagon_ids,
            'wagons': wagons,
            'tracked_wagons': tracked_wagons,
            'processing_time': processing_time,
            'fps': fps,
            'visualization': vis_frame,
            'timestamp': time.time()
        }

def process_frame(frame: np.ndarray, camera_id: str = "default") -> Dict:
    pipeline = RailwayMonitoringPipeline()
    return pipeline.process_frame(frame, camera_id)
