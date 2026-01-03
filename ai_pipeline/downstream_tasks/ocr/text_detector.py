"""
Text detection for wagon number plates
Uses PaddleOCR detection model
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import yaml
from pathlib import Path

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    print("⚠ PaddleOCR not available, using fallback methods")


class TextDetector:
    """Detect text regions in images"""
    
    def __init__(self, config_path: str = "ai_pipeline/configs/ocr.yaml"):
        """Initialize text detector"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.det_config = self.config.get('detection', {})
        self.use_paddle = PADDLE_AVAILABLE and self.det_config.get('model') == 'paddleocr'
        
        if self.use_paddle:
            # Initialize PaddleOCR detector
            self.paddle_ocr = PaddleOCR(
                use_angle_cls=False,
                lang='en',
                det=True,
                rec=False,
                show_log=False
            )
            print("✓ PaddleOCR detector initialized")
        else:
            print("ℹ Using classical text detection methods")
        
        self.score_threshold = self.det_config.get('score_threshold', 0.5)
        
    def detect_paddle(self, image: np.ndarray) -> List[np.ndarray]:
        """Detect text using PaddleOCR"""
        result = self.paddle_ocr.ocr(image, det=True, rec=False, cls=False)
        
        if result is None or len(result) == 0:
            return []
        
        # Extract bounding boxes
        boxes = []
        for line in result[0]:
            box = np.array(line, dtype=np.float32)
            boxes.append(box)
        
        return boxes
    
    def detect_classical(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Detect text regions using classical CV methods
        Fallback when PaddleOCR not available
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations to connect text regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        dilated = cv2.dilate(binary, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by aspect ratio and area
        h, w = image.shape[:2]
        min_area = (h * w) * 0.001  # At least 0.1% of image
        boxes = []
        
        for contour in contours:
            x, y, cw, ch = cv2.boundingRect(contour)
            area = cw * ch
            aspect_ratio = cw / (ch + 1e-6)
            
            # Filter: reasonable size and horizontal aspect
            if area > min_area and 2 < aspect_ratio < 20:
                # Convert to 4-point format
                box = np.array([
                    [x, y],
                    [x + cw, y],
                    [x + cw, y + ch],
                    [x, y + ch]
                ], dtype=np.float32)
                boxes.append(box)
        
        return boxes
    
    def detect(self, image: np.ndarray) -> List[dict]:
        """
        Detect text regions in image
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of detected text regions with bounding boxes
        """
        if self.use_paddle:
            boxes = self.detect_paddle(image)
        else:
            boxes = self.detect_classical(image)
        
        # Convert to standard format
        detections = []
        for i, box in enumerate(boxes):
            detections.append({
                'id': i,
                'box': box,
                'score': 1.0  # Confidence score (1.0 for classical)
            })
        
        return detections
    
    def visualize(self, image: np.ndarray, detections: List[dict]) -> np.ndarray:
        """Draw detection boxes on image"""
        vis = image.copy()
        
        for det in detections:
            box = det['box'].astype(np.int32)
            cv2.polylines(vis, [box], True, (0, 255, 0), 2)
            
            # Draw score if available
            if 'score' in det:
                score = det['score']
                cv2.putText(
                    vis, f"{score:.2f}",
                    tuple(box[0]), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 1
                )
        
        return vis


# Test
if __name__ == "__main__":
    import sys
    
    detector = TextDetector()
    
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        image = cv2.imread(img_path)
    else:
        # Create test image with text
        image = np.ones((400, 600, 3), dtype=np.uint8) * 255
        cv2.putText(
            image, "WAGON12345", (50, 200),
            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3
        )
        cv2.imwrite("test_text_image.jpg", image)
        img_path = "test_text_image.jpg"
        print(f"Created test image: {img_path}\n")
    
    print(f"Detecting text in: {img_path}")
    detections = detector.detect(image)
    
    print(f"Found {len(detections)} text regions\n")
    for det in detections:
        box = det['box']
        print(f"Detection {det['id']}: {box[0]} -> {box[2]}")
    
    # Visualize
    vis = detector.visualize(image, detections)
    output_path = img_path.replace('.jpg', '_detected.jpg')
    cv2.imwrite(output_path, vis)
    print(f"\nSaved visualization: {output_path}")
    
    print("\n✅ Text detection completed!")
