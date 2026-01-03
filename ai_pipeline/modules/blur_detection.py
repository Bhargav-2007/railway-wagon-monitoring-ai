import cv2
import numpy as np
from typing import Dict, Tuple

class BlurDetector:
    def __init__(self, threshold: float = 100.0):
        """
        Balanced blur detector
        
        Laplacian Variance ranges:
        - < 50: Severely blurred (motion blur, out of focus)
        - 50-100: Moderately blurred
        - 100-200: Borderline (depends on threshold)
        - 200-500: Good quality
        - > 500: Very sharp
        
        Args:
            threshold: Default 100 works for most cases
        """
        self.threshold = threshold
        
    def calculate_blur_metrics(self, image: np.ndarray) -> Dict:
        """Calculate multiple blur metrics for better accuracy"""
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Metric 1: Laplacian Variance (most reliable)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_var = laplacian.var()
        
        # Metric 2: Gradient magnitude (Tenengrad)
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = np.sqrt(gx**2 + gy**2).mean()
        
        # Metric 3: Edge strength
        edges = cv2.Canny(gray, 100, 200)
        edge_ratio = np.sum(edges > 0) / edges.size
        
        return {
            'laplacian_var': laplacian_var,
            'gradient_mag': gradient_mag,
            'edge_ratio': edge_ratio
        }
    
    def detect_blur(self, image: np.ndarray) -> Dict:
        """
        Detect blur with balanced approach
        """
        
        # Get metrics
        metrics = self.calculate_blur_metrics(image)
        
        # Use Laplacian variance as primary metric
        laplacian_var = metrics['laplacian_var']
        
        # Normalize other metrics for weighting
        gradient_score = min(metrics['gradient_mag'] * 2, 500)
        edge_score = metrics['edge_ratio'] * 1000
        
        # Weighted combination
        # Laplacian variance is most reliable, give it 70% weight
        blur_score = (
            laplacian_var * 0.7 +
            gradient_score * 0.2 +
            edge_score * 0.1
        )
        
        # Determine blur status
        is_blurred = blur_score < self.threshold
        
        # Calculate confidence
        distance_from_threshold = abs(blur_score - self.threshold)
        confidence = min(distance_from_threshold / self.threshold, 1.0)
        
        # Classification
        if blur_score < 50:
            quality = "Severely Blurred"
        elif blur_score < 100:
            quality = "Moderately Blurred"
        elif blur_score < 200:
            quality = "Acceptable"
        elif blur_score < 500:
            quality = "Good Quality"
        else:
            quality = "Very Sharp"
        
        return {
            'is_blurred': bool(is_blurred),
            'blur_score': float(blur_score),
            'threshold': self.threshold,
            'confidence': float(confidence),
            'quality': quality,
            'laplacian_var': float(laplacian_var),
            'gradient_mag': float(metrics['gradient_mag']),
            'edge_ratio': float(metrics['edge_ratio']),
            'method': 'balanced_multi_metric'
        }

def detect_blur(image: np.ndarray, threshold: float = 100.0) -> Tuple[bool, float]:
    """Simple blur detection function"""
    detector = BlurDetector(threshold=threshold)
    result = detector.detect_blur(image)
    return result['is_blurred'], result['blur_score']
