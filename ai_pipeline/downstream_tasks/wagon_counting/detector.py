"""
Wagon detection using YOLOv8
Falls back to simple contour detection if YOLO unavailable
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple
import yaml

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class WagonDetector:
    """Detect wagons in frame"""
    
    def __init__(self, model_path: str = None, config_path: str = "ai_pipeline/configs/inference.yaml"):
        """Initialize wagon detector"""
        self.use_yolo = YOLO_AVAILABLE and model_path is not None
        
        if self.use_yolo:
            self.model = YOLO(model_path)
            print(f"✓ YOLO model loaded: {model_path}")
        else:
            print("ℹ Using classical wagon detection (no YOLO)")
        
        self.confidence_threshold = 0.5
    
    def detect_yolo(self, image: np.ndarray) -> List[Dict]:
        """Detect using YOLO"""
        results = self.model(image, conf=self.confidence_threshold, verbose=False)
        
        detections = []
        for r in results:
            boxes = r.boxes
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                detections.append({
                    'id': i,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': confidence,
                    'class_id': class_id
                })
        
        return detections
    
    def detect_classical(self, image: np.ndarray) -> List[Dict]:
        """
        Classical detection using edge detection and contours
        Assumes wagons are large rectangular objects
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        h, w = image.shape[:2]
        min_area = (h * w) * 0.05  # At least 5% of frame
        
        detections = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            x, y, cw, ch = cv2.boundingRect(contour)
            aspect_ratio = cw / (ch + 1e-6)
            
            # Filter by aspect ratio (wagons are wider than tall)
            if 1.5 < aspect_ratio < 6:
                detections.append({
                    'id': i,
                    'bbox': [x, y, x+cw, y+ch],
                    'confidence': 0.8,  # Fixed confidence for classical
                    'class_id': 0
                })
        
        return detections
    
    def detect(self, image: np.ndarray) -> List[Dict]:
        """Detect wagons in image"""
        if self.use_yolo:
            return self.detect_yolo(image)
        else:
            return self.detect_classical(image)
    
    def visualize(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw detections"""
        vis = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Wagon {conf:.2f}"
            cv2.putText(vis, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return vis


# Test
if __name__ == "__main__":
    import sys
    
    detector = WagonDetector()
    
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        img_path = "test_frame_captured.jpg"
    
    image = cv2.imread(img_path)
    print(f"Detecting wagons in: {img_path}\n")
    
    detections = detector.detect(image)
    print(f"Found {len(detections)} wagons")
    
    for det in detections:
        print(f"  Wagon {det['id']}: bbox={det['bbox']}, conf={det['confidence']:.2f}")
    
    vis = detector.visualize(image, detections)
    output_path = img_path.replace('.jpg', '_wagons.jpg')
    cv2.imwrite(output_path, vis)
    print(f"\nSaved: {output_path}")
