"""
Low-light enhancement inference using Zero-DCE
"""

import cv2
import numpy as np
import torch
from typing import Optional
from pathlib import Path
import yaml

from ai_pipeline.low_light_enhancement.model import create_zero_dce


class LowLightEnhancer:
    """Zero-DCE based low-light enhancement"""
    
    def __init__(
        self,
        config_path: str = "ai_pipeline/configs/low_light.yaml",
        model_path: Optional[str] = None,
        device: str = "cpu"
    ):
        self.device = torch.device(device)
        
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize model
        model_type = self.config.get('model', {}).get('architecture', 'zero_dce')
        num_iterations = self.config.get('model', {}).get('num_iterations', 8)
        
        if 'plusplus' in model_type:
            self.model = create_zero_dce("plusplus", num_iterations)
        else:
            self.model = create_zero_dce("standard", num_iterations)
        
        self.model.to(self.device)
        self.model.eval()
        
        # Load checkpoint if available
        if model_path and Path(model_path).exists():
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            print(f"✓ Loaded low-light model from {model_path}")
        else:
            print("ℹ Using untrained model (for testing)")
        
        self.auto_detect = self.config.get('inference', {}).get('auto_detect_low_light', True)
        self.brightness_threshold = self.config.get('inference', {}).get('brightness_threshold', 50)
    
    def is_low_light(self, image: np.ndarray) -> bool:
        """
        Detect if image is low-light
        
        Args:
            image: Input image (BGR)
            
        Returns:
            True if low-light detected
        """
        # Convert to grayscale and compute mean brightness
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        return mean_brightness < self.brightness_threshold
    
    def preprocess(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image"""
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(rgb).float() / 255.0
        tensor = tensor.permute(2, 0, 1).unsqueeze(0)
        return tensor.to(self.device)
    
    def postprocess(self, tensor: torch.Tensor) -> np.ndarray:
        """Postprocess tensor to image"""
        output = tensor.squeeze(0).cpu()
        output = torch.clamp(output, 0, 1) * 255.0
        image = output.permute(1, 2, 0).numpy().astype(np.uint8)
        bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return bgr
    
    def enhance(self, image: np.ndarray, force: bool = False) -> np.ndarray:
        """
        Enhance low-light image
        
        Args:
            image: Input image (BGR)
            force: Force enhancement even if not detected as low-light
            
        Returns:
            Enhanced image
        """
        # Check if enhancement needed
        if self.auto_detect and not force:
            if not self.is_low_light(image):
                return image
        
        # Enhance
        input_tensor = self.preprocess(image)
        
        with torch.no_grad():
            enhanced_tensor = self.model(input_tensor)
        
        enhanced = self.postprocess(enhanced_tensor)
        return enhanced


# Test
if __name__ == "__main__":
    import sys
    
    enhancer = LowLightEnhancer()
    
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        image = cv2.imread(img_path)
    else:
        # Create dark test image
        image = np.random.randint(0, 80, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite("test_dark.jpg", image)
        img_path = "test_dark.jpg"
        print(f"Created dark test image: {img_path}\n")
    
    print(f"Processing: {img_path}")
    print(f"Is low-light: {enhancer.is_low_light(image)}\n")
    
    enhanced = enhancer.enhance(image, force=True)
    
    output_path = img_path.replace('.jpg', '_enhanced.jpg')
    cv2.imwrite(output_path, enhanced)
    print(f"Saved: {output_path}")
    
    # Comparison
    comparison = np.hstack([image, enhanced])
    cv2.imwrite(img_path.replace('.jpg', '_comparison.jpg'), comparison)
    
    print("\n✅ Enhancement completed!")
