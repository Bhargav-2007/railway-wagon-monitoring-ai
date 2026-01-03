import cv2
import numpy as np
from typing import Dict, Tuple

class BlurDetector:
    def __init__(self, threshold: float = 200.0):
        """
        Blur detector using classical computer vision methods
        
        Args:
            threshold: Blur threshold (higher = more sensitive)
                      - 100-150: Very sensitive
                      - 150-200: Moderate (recommended)
                      - 200-300: Less sensitive
        """
        self.threshold = threshold
        
    def detect_blur(self, image: np.ndarray) -> Dict:
        """
        Detect if image is blurred
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            Dictionary with blur detection results
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Method 1: Laplacian variance (primary method)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Method 2: Edge detection strength
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges) / edges.size
        
        # Combined score
        combined_score = laplacian_var * 0.7 + (edge_density * 1000) * 0.3
        
        # Determine if blurred
        is_blurred = combined_score < self.threshold
        
        # Calculate confidence
        confidence = abs(combined_score - self.threshold) / self.threshold
        confidence = min(confidence, 1.0)
        
        return {
            'is_blurred': bool(is_blurred),
            'blur_score': float(combined_score),
            'threshold': self.threshold,
            'confidence': float(confidence),
            'laplacian_var': float(laplacian_var),
            'edge_density': float(edge_density),
            'method': 'classical_combined'
        }

def detect_blur(image: np.ndarray, threshold: float = 200.0) -> Tuple[bool, float]:
    """Simple blur detection function"""
    detector = BlurDetector(threshold=threshold)
    result = detector.detect_blur(image)
    return result['is_blurred'], result['blur_score']
