"""
Complete OCR inference pipeline
Detection + Recognition integrated
"""

import cv2
import numpy as np
from typing import List, Dict
import time

from ai_pipeline.downstream_tasks.ocr.text_detector import TextDetector
from ai_pipeline.downstream_tasks.ocr.recognizer import TextRecognizer


class OCRPipeline:
    """End-to-end OCR for wagon identification"""
    
    def __init__(self, config_path: str = "ai_pipeline/configs/ocr.yaml"):
        """Initialize OCR pipeline"""
        self.detector = TextDetector(config_path)
        self.recognizer = TextRecognizer(config_path)
        print("✓ OCR Pipeline initialized")
    
    def process_image(self, image: np.ndarray) -> Dict:
        """
        Process single image through full OCR pipeline
        
        Args:
            image: Input image (BGR)
            
        Returns:
            Dictionary with OCR results
        """
        start_time = time.time()
        
        # Detect text regions
        det_start = time.time()
        detections = self.detector.detect(image)
        det_time = time.time() - det_start
        
        # Recognize text
        rec_start = time.time()
        recognitions = self.recognizer.recognize(image, detections)
        rec_time = time.time() - rec_start
        
        total_time = time.time() - start_time
        
        # Extract valid wagon IDs
        wagon_ids = [
            r for r in recognitions 
            if r['is_valid_wagon_id'] and r['confidence'] > 0.6
        ]
        
        return {
            'num_detections': len(detections),
            'num_recognized': len(recognitions),
            'wagon_ids': wagon_ids,
            'all_recognitions': recognitions,
            'timing': {
                'detection': det_time,
                'recognition': rec_time,
                'total': total_time
            }
        }
    
    def visualize_results(self, image: np.ndarray, results: Dict) -> np.ndarray:
        """Draw OCR results on image"""
        vis = image.copy()
        
        for rec in results['all_recognitions']:
            box = rec['box'].astype(np.int32)
            text = rec['text']
            confidence = rec['confidence']
            is_valid = rec['is_valid_wagon_id']
            
            # Color: green if valid wagon ID, yellow otherwise
            color = (0, 255, 0) if is_valid else (0, 255, 255)
            
            # Draw box
            cv2.polylines(vis, [box], True, color, 2)
            
            # Draw text and confidence
            label = f"{text} ({confidence:.2f})"
            cv2.putText(
                vis, label, tuple(box[0]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )
        
        return vis


# Test
if __name__ == "__main__":
    import sys
    
    pipeline = OCRPipeline()
    
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        img_path = "test_text_image.jpg"
    
    image = cv2.imread(img_path)
    print(f"\nProcessing: {img_path}\n")
    
    # Run OCR
    results = pipeline.process_image(image)
    
    # Print results
    print("="*60)
    print(f"Detections: {results['num_detections']}")
    print(f"Recognized: {results['num_recognized']}")
    print(f"Valid Wagon IDs: {len(results['wagon_ids'])}")
    print("\nWagon IDs Found:")
    for wagon in results['wagon_ids']:
        print(f"  - {wagon['text']} (confidence: {wagon['confidence']:.2f})")
    
    print("\nTiming:")
    for key, value in results['timing'].items():
        print(f"  {key}: {value:.3f}s")
    
    # Visualize
    vis = pipeline.visualize_results(image, results)
    output_path = img_path.replace('.jpg', '_ocr_result.jpg')
    cv2.imwrite(output_path, vis)
    print(f"\nSaved: {output_path}")
    
    print("\n✅ OCR pipeline completed!")
