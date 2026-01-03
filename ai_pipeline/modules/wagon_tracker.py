import numpy as np
from typing import List, Dict
import time

class WagonTracker:
    def __init__(self, iou_threshold: float = 0.3):
        """
        Initialize wagon tracker
        
        Args:
            iou_threshold: IoU threshold for matching wagons across frames
        """
        self.iou_threshold = iou_threshold
        self.tracked_wagons = {}
        self.next_wagon_id = 1
        
    def calculate_iou(self, box1: tuple, box2: tuple) -> float:
        """Calculate IoU between two bounding boxes"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Calculate intersection
        xi1 = max(x1, x2)
        yi1 = max(y1, y2)
        xi2 = min(x1 + w1, x2 + w2)
        yi2 = min(y1 + h1, y2 + h2)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        
        # Calculate union
        box1_area = w1 * h1
        box2_area = w2 * h2
        union_area = box1_area + box2_area - inter_area
        
        # Calculate IoU
        iou = inter_area / union_area if union_area > 0 else 0
        
        return iou
    
    def update(self, wagons: List[Dict], camera_id: str) -> List[Dict]:
        """
        Update tracked wagons with new detections
        
        Args:
            wagons: List of detected wagons
            camera_id: Camera identifier
            
        Returns:
            List of tracked wagons with IDs
        """
        tracked = []
        current_time = time.time()
        
        for wagon in wagons:
            bbox = wagon['bbox']
            
            # Try to match with existing tracked wagons
            matched = False
            best_match_id = None
            best_iou = 0
            
            for wagon_id, tracked_wagon in self.tracked_wagons.items():
                if tracked_wagon['camera_id'] != camera_id:
                    continue
                
                iou = self.calculate_iou(bbox, tracked_wagon['bbox'])
                
                if iou > self.iou_threshold and iou > best_iou:
                    best_iou = iou
                    best_match_id = wagon_id
                    matched = True
            
            if matched and best_match_id:
                # Update existing wagon
                wagon_id = best_match_id
                self.tracked_wagons[wagon_id]['bbox'] = bbox
                self.tracked_wagons[wagon_id]['last_seen'] = current_time
            else:
                # Create new tracked wagon
                wagon_id = f"W{self.next_wagon_id:04d}"
                self.next_wagon_id += 1
                
                self.tracked_wagons[wagon_id] = {
                    'wagon_id': wagon_id,
                    'bbox': bbox,
                    'camera_id': camera_id,
                    'first_seen': current_time,
                    'last_seen': current_time
                }
            
            # Add to tracked list
            tracked_wagon = wagon.copy()
            tracked_wagon['wagon_id'] = wagon_id
            tracked.append(tracked_wagon)
        
        # Clean up old wagons (not seen for 10 seconds)
        timeout = 10.0
        to_remove = []
        for wagon_id, wagon_data in self.tracked_wagons.items():
            if current_time - wagon_data['last_seen'] > timeout:
                to_remove.append(wagon_id)
        
        for wagon_id in to_remove:
            del self.tracked_wagons[wagon_id]
        
        return tracked
