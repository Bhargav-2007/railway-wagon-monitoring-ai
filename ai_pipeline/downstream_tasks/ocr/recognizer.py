"""
Text recognition for wagon numbers
"""

import cv2
import numpy as np
from typing import List, Dict, Optional
import re
import yaml


try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False


class TextRecognizer:
    """Recognize text from detected regions"""
    
    def __init__(self, config_path: str = "ai_pipeline/configs/ocr.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.rec_config = self.config.get('recognition', {})
        self.post_config = self.config.get('postprocessing', {})
        
        self.use_paddle = PADDLE_AVAILABLE
        
        if self.use_paddle:
            self.paddle_ocr = PaddleOCR(
                use_angle_cls=False,
                lang='en',
                det=False,
                rec=True,
                show_log=False
            )
            print("✓ PaddleOCR recognizer initialized")
        else:
            print("ℹ Recognition requires PaddleOCR (pip install paddleocr)")
        
        # Wagon ID pattern (e.g., ABCD1234)
        self.wagon_pattern = self.post_config.get(
            'wagon_id_pattern',
            r'^[A-Z]{2,4}[0-9]{4,8}$'
        )
        self.min_confidence = self.post_config.get('min_confidence', 0.6)
        
    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess text region for better OCR"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Threshold
        _, binary = cv2.threshold(
            enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        return binary
    
    def recognize_region(self, image: np.ndarray, box: np.ndarray) -> Dict:
        """
        Recognize text in specific region
        
        Args:
            image: Full image
            box: Bounding box coordinates
            
        Returns:
            Recognition result dict
        """
        # Crop region
        box = box.astype(np.int32)
        x_min = max(0, box[:, 0].min())
        y_min = max(0, box[:, 1].min())
        x_max = min(image.shape[1], box[:, 0].max())
        y_max = min(image.shape[0], box[:, 1].max())
        
        roi = image[y_min:y_max, x_min:x_max]
        
        if roi.size == 0:
            return {'text': '', 'confidence': 0.0}
        
        # Preprocess
        processed = self.preprocess_for_ocr(roi)
        
        # Recognize
        if self.use_paddle:
            result = self.paddle_ocr.ocr(processed, det=False, rec=True, cls=False)
            
            if result and len(result) > 0 and len(result[0]) > 0:
                text, confidence = result[0][0]
                return {
                    'text': text,
                    'confidence': confidence,
                    'method': 'paddleocr'
                }
        
        # Fallback: return empty
        return {'text': '', 'confidence': 0.0, 'method': 'none'}
    
    def postprocess_text(self, text: str) -> str:
        """Clean up recognized text"""
        # Remove special characters
        if self.post_config.get('filter_special_chars', True):
            allowed = self.post_config.get('allowed_chars', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-')
            text = ''.join(c for c in text if c in allowed)
        
        # Convert to uppercase
        text = text.upper()
        
        return text
    
    def validate_wagon_id(self, text: str) -> bool:
        """Check if text matches wagon ID pattern"""
        pattern = re.compile(self.wagon_pattern)
        return bool(pattern.match(text))
    
    def recognize(self, image: np.ndarray, detections: List[dict]) -> List[dict]:
        """
        Recognize all detected text regions
        
        Args:
            image: Input image
            detections: List of text detections with boxes
            
        Returns:
            List of recognition results
        """
        results = []
        
        for det in detections:
            box = det['box']
            rec_result = self.recognize_region(image, box)
            
            # Postprocess
            text = self.postprocess_text(rec_result['text'])
            confidence = rec_result['confidence']
            
            # Validate
            is_valid = self.validate_wagon_id(text)
            
            results.append({
                'detection_id': det['id'],
                'box': box,
                'text': text,
                'confidence': confidence,
                'is_valid_wagon_id': is_valid,
                'method': rec_result.get('method', 'none')
            })
        
        return results


# Test
if __name__ == "__main__":
    import sys
    from ai_pipeline.downstream_tasks.ocr.text_detector import TextDetector
    
    detector = TextDetector()
    recognizer = TextRecognizer()
    
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        img_path = "test_text_image.jpg"
    
    image = cv2.imread(img_path)
    print(f"Processing: {img_path}\n")
    
    # Detect
    detections = detector.detect(image)
    print(f"Detected {len(detections)} text regions")
    
    # Recognize
    results = recognizer.recognize(image, detections)
    
    print("\nRecognition Results:")
    print("="*60)
    for res in results:
        print(f"Text: {res['text']}")
        print(f"Confidence: {res['confidence']:.2f}")
        print(f"Valid Wagon ID: {res['is_valid_wagon_id']}")
        print("-"*60)
    
    print("\n✅ OCR completed!")
