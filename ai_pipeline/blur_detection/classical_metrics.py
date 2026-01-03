"""
Classical Blur Detection Metrics
Laplacian variance, Sobel gradient, FFT-based methods
"""

import cv2
import numpy as np
from typing import Dict, Tuple
import sys  # Add this for command-line testing

class BlurDetector:
    """Classical blur detection using multiple metrics"""
    
    @staticmethod
    def laplacian_variance(image: np.ndarray) -> float:
        """
        Compute Laplacian variance (most common blur metric)
        Lower values indicate more blur
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Variance of Laplacian (higher = sharper)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        return float(variance)
    
    @staticmethod
    def sobel_gradient(image: np.ndarray) -> float:
        """
        Compute average Sobel gradient magnitude
        
        Args:
            image: Input image
            
        Returns:
            Average gradient magnitude
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Compute gradients in x and y directions
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Compute magnitude
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        avg_magnitude = np.mean(magnitude)
        
        return float(avg_magnitude)
    
    @staticmethod
    def fft_frequency_analysis(image: np.ndarray) -> float:
        """
        Analyze frequency content using FFT
        Blurred images have less high-frequency content
        
        Args:
            image: Input image
            
        Returns:
            High frequency ratio (0-1, higher = sharper)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Compute FFT
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        # Calculate center region (low frequencies)
        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2
        center_radius = min(rows, cols) // 4
        
        # Create masks for low and high frequencies
        y, x = np.ogrid[:rows, :cols]
        center_mask = ((x - ccol)**2 + (y - crow)**2) <= center_radius**2
        
        # Calculate energy in high frequencies
        total_energy = np.sum(magnitude_spectrum)
        center_energy = np.sum(magnitude_spectrum[center_mask])
        high_freq_ratio = 1.0 - (center_energy / (total_energy + 1e-8))
        
        return float(high_freq_ratio)
    
    @staticmethod
    def detect_blur(
        image: np.ndarray,
        threshold: float = 100.0,
        method: str = "laplacian"
    ) -> Tuple[bool, float, Dict[str, float]]:
        """
        Detect if image is blurred
        
        Args:
            image: Input image
            threshold: Blur threshold (for Laplacian method)
            method: Detection method ("laplacian", "sobel", "fft", "combined")
            
        Returns:
            Tuple of (is_blurred, score, all_metrics)
        """
        detector = BlurDetector()
        
        # Compute all metrics
        lap_var = detector.laplacian_variance(image)
        sobel_grad = detector.sobel_gradient(image)
        fft_ratio = detector.fft_frequency_analysis(image)
        
        metrics = {
            "laplacian_variance": lap_var,
            "sobel_gradient": sobel_grad,
            "fft_high_freq_ratio": fft_ratio
        }
        
        # Determine blur based on method
        if method == "laplacian":
            is_blurred = lap_var < threshold
            score = lap_var
        elif method == "sobel":
            is_blurred = sobel_grad < (threshold / 10)
            score = sobel_grad
        elif method == "fft":
            is_blurred = fft_ratio < 0.3
            score = fft_ratio * 100
        elif method == "combined":
            # Normalized combined score
            lap_norm = min(lap_var / threshold, 1.0)
            sobel_norm = min(sobel_grad / (threshold / 10), 1.0)
            fft_norm = fft_ratio
            
            combined_score = (lap_norm + sobel_norm + fft_norm) / 3.0 * 100
            is_blurred = combined_score < 50.0
            score = combined_score
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return is_blurred, score, metrics


# Test function
if __name__ == "__main__":
    # Test with a sample image
    import sys
    
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        # Create synthetic test image
        img_path = None
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite("test_sharp.jpg", image)
        
        # Create blurred version
        blurred = cv2.GaussianBlur(image, (15, 15), 0)
        cv2.imwrite("test_blurred.jpg", blurred)
        
        print("Created test images: test_sharp.jpg, test_blurred.jpg")
        img_path = "test_sharp.jpg"
    
    # Load and test
    image = cv2.imread(img_path)
    is_blurred, score, metrics = BlurDetector.detect_blur(
        image,
        threshold=100.0,
        method="combined"
    )
    
    print(f"\nImage: {img_path}")
    print(f"Is Blurred: {is_blurred}")
    print(f"Overall Score: {score:.2f}")
    print("\nDetailed Metrics:")
    for metric_name, value in metrics.items():
        print(f"  {metric_name}: {value:.2f}")
