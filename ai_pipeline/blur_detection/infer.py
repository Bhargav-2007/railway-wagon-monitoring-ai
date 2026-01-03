"""
Blur detection inference - combines classical + CNN methods
"""

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, Tuple, Optional
from pathlib import Path
import yaml

from ai_pipeline.blur_detection.classical_metrics import BlurDetector
from ai_pipeline.blur_detection.cnn_model import create_blur_classifier


class BlurDetectionInference:
    """Combined blur detection using classical and CNN methods"""
    
    def __init__(
        self,
        config_path: str = "ai_pipeline/configs/blur_detection.yaml",
        model_path: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Initialize blur detection inference
        
        Args:
            config_path: Path to configuration file
            model_path: Path to trained CNN model (optional)
            device: Device to run model on ("cpu" or "cuda")
        """
        self.device = torch.device(device)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize classical detector
        self.classical_detector = BlurDetector()
        
        # Initialize CNN model if path provided
        self.use_cnn = model_path is not None and Path(model_path).exists()
        if self.use_cnn:
            self.model = create_blur_classifier("standard")
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            print(f"✓ Loaded CNN model from {model_path}")
        else:
            self.model = None
            print("ℹ Using classical metrics only (no CNN model)")
        
        self.input_size = self.config['model']['input_size']
        self.threshold = self.config['model']['classical_threshold']
        
    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """
        Preprocess image for CNN inference
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Preprocessed tensor [1, 3, H, W]
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize
        resized = cv2.resize(rgb_image, (self.input_size, self.input_size))
        
        # Normalize to [0, 1]
        normalized = resized.astype(np.float32) / 255.0
        
        # Convert to tensor and add batch dimension
        tensor = torch.from_numpy(normalized).permute(2, 0, 1).unsqueeze(0)
        
        return tensor.to(self.device)
    
    def detect_blur(
        self,
        image: np.ndarray,
        method: str = "hybrid"
    ) -> Dict[str, any]:
        """
        Detect blur in image
        
        Args:
            image: Input image (BGR format)
            method: "classical", "cnn", or "hybrid"
            
        Returns:
            Dictionary with detection results
        """
        results = {
            "is_blurred": False,
            "confidence": 0.0,
            "method": method,
            "classical_metrics": {},
            "cnn_prediction": None
        }
        
        # Classical metrics (always compute)
        is_blurred_classical, classical_score, metrics = \
            self.classical_detector.detect_blur(
                image,
                threshold=self.threshold,
                method="combined"
            )
        
        results["classical_metrics"] = metrics
        results["classical_score"] = classical_score
        results["is_blurred_classical"] = is_blurred_classical
        
        # CNN prediction (if available and requested)
        if self.use_cnn and method in ["cnn", "hybrid"]:
            input_tensor = self.preprocess_image(image)
            
            with torch.no_grad():
                logits = self.model(input_tensor)
                probs = F.softmax(logits, dim=1)
                
                # Class 0: sharp, Class 1: blurred
                blur_prob = probs[0, 1].item()
                is_blurred_cnn = blur_prob > 0.5
                
                results["cnn_prediction"] = {
                    "blur_probability": blur_prob,
                    "is_blurred": is_blurred_cnn
                }
        
        # Final decision based on method
        if method == "classical":
            results["is_blurred"] = is_blurred_classical
            results["confidence"] = classical_score / 100.0
            
        elif method == "cnn" and self.use_cnn:
            cnn_pred = results["cnn_prediction"]
            results["is_blurred"] = cnn_pred["is_blurred"]
            results["confidence"] = cnn_pred["blur_probability"]
            
        elif method == "hybrid" and self.use_cnn:
            # Combine both methods
            cnn_pred = results["cnn_prediction"]
            
            # Weighted voting
            classical_vote = 1 if is_blurred_classical else 0
            cnn_vote = 1 if cnn_pred["is_blurred"] else 0
            
            # CNN has slightly higher weight
            combined_vote = (classical_vote * 0.4 + cnn_vote * 0.6)
            results["is_blurred"] = combined_vote > 0.5
            
            # Combined confidence
            classical_conf = min(classical_score / 100.0, 1.0)
            cnn_conf = cnn_pred["blur_probability"]
            results["confidence"] = (classical_conf * 0.4 + cnn_conf * 0.6)
            
        else:
            # Fallback to classical
            results["is_blurred"] = is_blurred_classical
            results["confidence"] = classical_score / 100.0
        
        return results
    
    def batch_detect(self, images: list) -> list:
        """
        Detect blur in batch of images
        
        Args:
            images: List of images
            
        Returns:
            List of detection results
        """
        results = []
        for image in images:
            result = self.detect_blur(image)
            results.append(result)
        return results


# Test function
if __name__ == "__main__":
    import sys
    
    # Initialize detector (without trained model for now)
    detector = BlurDetectionInference()
    
    if len(sys.argv) > 1:
        # Test with provided image
        img_path = sys.argv[1]
        image = cv2.imread(img_path)
        
        if image is None:
            print(f"Error: Cannot load image from {img_path}")
            sys.exit(1)
        
        print(f"Testing blur detection on: {img_path}\n")
        
    else:
        # Create test images
        print("Creating synthetic test images...\n")
        
        # Sharp image (high frequency content)
        sharp = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite("test_sharp_synthetic.jpg", sharp)
        
        # Blurred image
        blurred = cv2.GaussianBlur(sharp, (21, 21), 0)
        cv2.imwrite("test_blurred_synthetic.jpg", blurred)
        
        image = sharp
        img_path = "test_sharp_synthetic.jpg"
    
    # Run detection
    result = detector.detect_blur(image, method="classical")
    
    print("="*60)
    print(f"Image: {img_path}")
    print("="*60)
    print(f"Is Blurred: {result['is_blurred']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Method: {result['method']}")
    print("\nClassical Metrics:")
    for metric, value in result['classical_metrics'].items():
        print(f"  {metric}: {value:.2f}")
    
    if result['cnn_prediction']:
        print("\nCNN Prediction:")
        print(f"  Blur probability: {result['cnn_prediction']['blur_probability']:.2f}")
        print(f"  Is blurred: {result['cnn_prediction']['is_blurred']}")
    
    print("\n✅ Detection completed!")
    
    # Test with blurred image if we created synthetic ones
    if len(sys.argv) == 1:
        print("\n" + "="*60)
        print("Testing blurred image...")
        print("="*60 + "\n")
        
        blurred_img = cv2.imread("test_blurred_synthetic.jpg")
        result_blur = detector.detect_blur(blurred_img)
        
        print(f"Is Blurred: {result_blur['is_blurred']}")
        print(f"Confidence: {result_blur['confidence']:.2f}")
        print(f"Laplacian Variance: {result_blur['classical_metrics']['laplacian_variance']:.2f}")
