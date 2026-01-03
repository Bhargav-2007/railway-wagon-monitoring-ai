"""
Simple wagon tracker using IoU matching
Tracks wagons across frames for counting
"""

import numpy as np
from typing import List, Dict
from collections import defaultdict


class WagonTracker:
    """Track wagons across video frames"""
    
    def __init__(self, iou_threshold: float = 0.3, max_age: int = 30):
        """
        Initialize tracker
        
        Args:
            iou_threshold: Minimum IoU for matching
            max_age: Maximum frames to keep track without detection
        """
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        
        self.next_id = 0
        self.tracks = {}  # track_id -> track_info
        self.total_count = 0
        
    def compute_iou(self, box1: List[int], box2: List[int]) -> float:
        """Compute IoU between two boxes"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Intersection
        xi_min = max(x1_min, x2_min)
        yi_min = max(y1_min, y2_min)
        xi_max = min(x1_max, x2_max)
        yi_max = min(y1_max, y2_max)
        
        if xi_max < xi_min or yi_max < yi_min:
            return 0.0
        
        intersection = (xi_max - xi_min) * (yi_max - yi_min)
        
        # Union
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union = area1 + area2 - intersection
        
        return intersection / (union + 1e-6)
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        """
        Update tracks with new detections
        
        Args:
            detections: List of detections in current frame
            
        Returns:
            List of tracked objects with IDs
        """
        # Match detections to existing tracks
        matched_tracks = set()
        tracked_objects = []
        
        for det in detections:
            det_box = det['bbox']
            best_iou = 0.0
            best_track_id = None
            
            # Find best matching track
            for track_id, track in self.tracks.items():
                iou = self.compute_iou(det_box, track['bbox'])
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id
            
            if best_track_id is not None:
                # Update existing track
                self.tracks[best_track_id]['bbox'] = det_box
                self.tracks[best_track_id]['age'] = 0
                self.tracks[best_track_id]['confidence'] = det['confidence']
                matched_tracks.add(best_track_id)
                
                tracked_objects.append({
                    'track_id': best_track_id,
                    'bbox': det_box,
                    'confidence': det['confidence']
                })
            else:
                # Create new track
                track_id = self.next_id
                self.next_id += 1
                self.total_count += 1
                
                self.tracks[track_id] = {
                    'bbox': det_box,
                    'age': 0,
                    'confidence': det['confidence'],
                    'first_seen': True
                }
                
                tracked_objects.append({
                    'track_id': track_id,
                    'bbox': det_box,
                    'confidence': det['confidence'],
                    'new': True
                })
        
        # Age unmatched tracks
        tracks_to_remove = []
        for track_id in self.tracks:
            if track_id not in matched_tracks:
                self.tracks[track_id]['age'] += 1
                if self.tracks[track_id]['age'] > self.max_age:
                    tracks_to_remove.append(track_id)
        
        # Remove old tracks
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
        
        return tracked_objects
    
    def get_count(self) -> int:
        """Get total wagon count"""
        return self.total_count
    
    def reset(self):
        """Reset tracker"""
        self.tracks.clear()
        self.total_count = 0
        self.next_id = 0


# Test
if __name__ == "__main__":
    tracker = WagonTracker()
    
    # Simulate detections across 5 frames
    frames = [
        [{'bbox': [100, 100, 200, 150], 'confidence': 0.9}],
        [{'bbox': [110, 100, 210, 150], 'confidence': 0.9}],  # Same wagon moved
        [{'bbox': [120, 100, 220, 150], 'confidence': 0.9},
         {'bbox': [300, 100, 400, 150], 'confidence': 0.85}],  # New wagon
        [{'bbox': [130, 100, 230, 150], 'confidence': 0.9},
         {'bbox': [310, 100, 410, 150], 'confidence': 0.85}],
        [{'bbox': [320, 100, 420, 150], 'confidence': 0.85}],  # First wagon left frame
    ]
    
    print("Tracking simulation:\n")
    for frame_idx, detections in enumerate(frames):
        tracked = tracker.update(detections)
        print(f"Frame {frame_idx}: {len(tracked)} wagons tracked")
        for obj in tracked:
            new_flag = " (NEW)" if obj.get('new', False) else ""
            print(f"  Track ID: {obj['track_id']}{new_flag}")
    
    print(f"\nTotal wagons counted: {tracker.get_count()}")
    print("\n✅ Tracking test completed!")
