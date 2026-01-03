"""
Deblurring inference using NAFNet
Processes blurred images to restore sharp details
"""

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from typing import Optional, Tuple
from pathlib import Path
import yaml

from ai_pipeline.deblurring.model import create_nafnet_deblur


class DeblurInference:
    """NAFNet-based motion deblurring inference"""
    
    def __init__(
        self,
        config_path: str = "ai_pipeline/configs/deblurring.yaml",
        model_path: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Initialize deblurring inference
        
        Args:
            config_path: Path to configuration file
            model_path: Path to trained model checkpoint
            device: Device to run on ("cpu" or "cuda")
        """
        self.device = torch.device(device)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize model
        model_size = self.config.get('model', {}).get('architecture', 'nafnet')
        width = self.config.get('model', {}).get('width', 32)
        
        # Create model based on width
        if width <= 16:
            size = "tiny"
        elif width <= 32:
            size = "small"
        elif width <= 48:
            size = "medium"
        else:
            size = "large"
        
        self.model = create_nafnet_deblur(size)
        self.model.to(self.device)
        self.model.eval()
        
        # Load checkpoint if provided
        if model_path and Path(model_path).exists():
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            print(f"✓ Loaded deblurring model from {model_path}")
        else:
            print("ℹ Using untrained model (for testing/demo)")
        
        self.tile_size = self.config.get('inference', {}).get('tile_size', 512)
        self.tile_overlap = self.config.get('inference', {}).get('tile_overlap', 32)
        
    def preprocess(self, image: np.ndarray) -> torch.Tensor:
        """
        Preprocess image for model
        
        Args:
            image: Input image (BGR format, uint8)
            
        Returns:
            Preprocessed tensor [1, 3, H, W]
        """
        # Convert BGR to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to float and normalize to [0, 1]
        tensor = torch.from_numpy(rgb).float() / 255.0
        
        # Permute to [C, H, W] and add batch dimension
        tensor = tensor.permute(2, 0, 1).unsqueeze(0)
        
        return tensor.to(self.device)
    
    def postprocess(self, tensor: torch.Tensor) -> np.ndarray:
        """
        Postprocess model output to image
        
        Args:
            tensor: Model output [1, 3, H, W]
            
        Returns:
            Output image (BGR format, uint8)
        """
        # Remove batch dimension and move to CPU
        output = tensor.squeeze(0).cpu()
        
        # Clamp to [0, 1] and convert to [0, 255]
        output = torch.clamp(output, 0, 1) * 255.0
        
        # Convert to numpy and permute to [H, W, C]
        image = output.permute(1, 2, 0).numpy().astype(np.uint8)
        
        # Convert RGB back to BGR
        bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        return bgr
    
    def deblur(self, image: np.ndarray, use_tiling: bool = False) -> np.ndarray:
        """
        Deblur single image
        
        Args:
            image: Input blurred image (BGR format)
            use_tiling: Use tiled inference for large images
            
        Returns:
            Deblurred image (BGR format)
        """
        h, w = image.shape[:2]
        
        # Use tiling for large images to save memory
        if use_tiling and (h > self.tile_size or w > self.tile_size):
            return self._deblur_tiled(image)
        else:
            return self._deblur_full(image)
    
    def _deblur_full(self, image: np.ndarray) -> np.ndarray:
        """Deblur entire image at once"""
        input_tensor = self.preprocess(image)
        
        with torch.no_grad():
            output_tensor = self.model(input_tensor)
        
        output_image = self.postprocess(output_tensor)
        return output_image
    
    def _deblur_tiled(self, image: np.ndarray) -> np.ndarray:
        """
        Deblur large image using overlapping tiles
        Prevents memory issues and handles arbitrary sizes
        """
        h, w = image.shape[:2]
        tile_size = self.tile_size
        overlap = self.tile_overlap
        stride = tile_size - overlap
        
        # Calculate number of tiles
        n_tiles_h = (h - overlap) // stride + 1
        n_tiles_w = (w - overlap) // stride + 1
        
        # Initialize output
        output = np.zeros_like(image, dtype=np.float32)
        weight_map = np.zeros((h, w), dtype=np.float32)
        
        # Process each tile
        for i in range(n_tiles_h):
            for j in range(n_tiles_w):
                # Calculate tile coordinates
                y1 = i * stride
                x1 = j * stride
                y2 = min(y1 + tile_size, h)
                x2 = min(x1 + tile_size, w)
                
                # Extract tile
                tile = image[y1:y2, x1:x2]
                
                # Deblur tile
                tile_deblurred = self._deblur_full(tile)
                
                # Compute blend weights (higher in center)
                tile_h, tile_w = tile.shape[:2]
                weight = self._compute_tile_weights(tile_h, tile_w, overlap)
                
                # Accumulate
                output[y1:y2, x1:x2] += tile_deblurred.astype(np.float32) * weight[:, :, np.newaxis]
                weight_map[y1:y2, x1:x2] += weight
        
        # Normalize by weights
        output = output / (weight_map[:, :, np.newaxis] + 1e-8)
        output = np.clip(output, 0, 255).astype(np.uint8)
        
        return output
    
    def _compute_tile_weights(self, h: int, w: int, overlap: int) -> np.ndarray:
        """
        Compute blending weights for tile
        Center has weight 1, edges fade to 0
        """
        weight = np.ones((h, w), dtype=np.float32)
        
        # Fade edges
        fade_size = overlap // 2
        if fade_size > 0:
            # Top
            weight[:fade_size, :] *= np.linspace(0, 1, fade_size)[:, np.newaxis]
            # Bottom
            weight[-fade_size:, :] *= np.linspace(1, 0, fade_size)[:, np.newaxis]
            # Left
            weight[:, :fade_size] *= np.linspace(0, 1, fade_size)[np.newaxis, :]
            # Right
            weight[:, -fade_size:] *= np.linspace(1, 0, fade_size)[np.newaxis, :]
        
        return weight
    
    def batch_deblur(self, images: list) -> list:
        """
        Deblur batch of images
        
        Args:
            images: List of input images
            
        Returns:
            List of deblurred images
        """
        results = []
        for image in images:
            deblurred = self.deblur(image)
            results.append(deblurred)
        return results


# Test function
if __name__ == "__main__":
    import sys
    import time
    
    print("Initializing deblurring model...\n")
    deblurrer = DeblurInference(device="cpu")
    
    if len(sys.argv) > 1:
        # Test with provided image
        img_path = sys.argv[1]
        image = cv2.imread(img_path)
        
        if image is None:
            print(f"Error: Cannot load {img_path}")
            sys.exit(1)
        
        print(f"Processing: {img_path}")
        print(f"Image size: {image.shape[1]}x{image.shape[0]}\n")
        
    else:
        # Create synthetic blurred test image
        print("Creating synthetic blurred image...\n")
        sharp = cv2.imread("test_frame_captured.jpg")
        if sharp is None:
            # Create random image
            sharp = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Apply motion blur
        kernel_size = 15
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size-1)/2), :] = np.ones(kernel_size)
        kernel = kernel / kernel_size
        
        image = cv2.filter2D(sharp, -1, kernel)
        cv2.imwrite("test_blurred_for_deblur.jpg", image)
        img_path = "test_blurred_for_deblur.jpg"
        print(f"Created blurred test image: {img_path}\n")
    
    # Deblur
    print("Deblurring...")
    start_time = time.time()
    
    deblurred = deblurrer.deblur(image, use_tiling=False)
    
    elapsed = time.time() - start_time
    print(f"✓ Deblurring completed in {elapsed:.2f}s\n")
    
    # Save result
    output_path = img_path.replace('.jpg', '_deblurred.jpg')
    cv2.imwrite(output_path, deblurred)
    print(f"Saved deblurred image: {output_path}")
    
    # Create comparison
    if image.shape == deblurred.shape:
        comparison = np.hstack([image, deblurred])
        comparison_path = img_path.replace('.jpg', '_comparison.jpg')
        cv2.imwrite(comparison_path, comparison)
        print(f"Saved comparison: {comparison_path}")
    
    print("\n✅ Test completed!")
