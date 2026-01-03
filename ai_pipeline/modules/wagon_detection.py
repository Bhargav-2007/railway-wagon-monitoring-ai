import cv2
import numpy as np
from typing import List, Dict

class WagonDetector:
    def __init__(self):
        """Initialize wagon detector using classical CV methods"""
        self.min_area = 5000  # Minimum wagon area in pixels
        self.max_area = 500000  # Maximum wagon area
        
    def detect_wagons(self, image: np.ndarray) -> List[Dict]:
        """
        Detect wagons in image using contour detection
        
        Args:
            image: Input image (BGR)
            
        Returns:
            List of detected wagons with bounding boxes
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        wagons = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area
            if self.min_area < area < self.max_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio (wagons are usually wide)
                aspect_ratio = w / h if h > 0 else 0
                
                if 1.5 < aspect_ratio < 8.0:  # Reasonable aspect ratio for wagons
                    wagons.append({
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'confidence': min(area / self.max_area, 1.0)
                    })
        
        # Sort by area (largest first)
        wagons.sort(key=lambda x: x['area'], reverse=True)
        
        return wagons

def detect_wagons(image: np.ndarray) -> List[Dict]:
    """Simple wagon detection function"""
    detector = WagonDetector()
    return detector.detect_wagons(image)
