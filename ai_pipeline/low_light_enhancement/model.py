"""
Zero-DCE: Zero-Reference Deep Curve Estimation
Lightweight low-light image enhancement without paired training data
Based on: https://arxiv.org/abs/2001.06826
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class DCENet(nn.Module):
    """
    Deep Curve Estimation Network
    Predicts pixel-wise curve parameters for enhancement
    """
    
    def __init__(self, num_iterations=8, num_filters=32):
        """
        Initialize DCE-Net
        
        Args:
            num_iterations: Number of curve adjustment iterations
            num_filters: Number of convolutional filters
        """
        super(DCENet, self).__init__()
        
        self.num_iterations = num_iterations
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, num_filters, 3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(num_filters, num_filters, 3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(num_filters, num_filters, 3, stride=1, padding=1)
        self.conv4 = nn.Conv2d(num_filters, num_filters, 3, stride=1, padding=1)
        
        # Output layer - predicts curve parameters
        self.conv5 = nn.Conv2d(num_filters, 3 * num_iterations, 3, stride=1, padding=1)
        
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Input image [B, 3, H, W]
            
        Returns:
            Curve parameters [B, num_iterations*3, H, W]
        """
        x1 = F.relu(self.conv1(x))
        x2 = F.relu(self.conv2(x1))
        x3 = F.relu(self.conv3(x2))
        x4 = F.relu(self.conv4(x3))
        
        # Predict curve parameters
        curve_params = torch.tanh(self.conv5(x4))
        
        return curve_params


class ZeroDCE(nn.Module):
    """Complete Zero-DCE enhancement pipeline"""
    
    def __init__(self, num_iterations=8, num_filters=32):
        super(ZeroDCE, self).__init__()
        
        self.dce_net = DCENet(num_iterations, num_filters)
        self.num_iterations = num_iterations
        
    def enhance(self, image, curve_params):
        """
        Apply curve enhancement to image
        
        Args:
            image: Input image [B, 3, H, W]
            curve_params: Curve parameters [B, num_iterations*3, H, W]
            
        Returns:
            Enhanced image [B, 3, H, W]
        """
        # Split curve parameters for each iteration
        curve_params = torch.split(curve_params, 3, dim=1)
        
        enhanced = image
        for params in curve_params:
            # Apply pixel-wise curve: enhanced = enhanced + params * enhanced * (1 - enhanced)
            enhanced = enhanced + params * (torch.pow(enhanced, 2) - enhanced)
        
        return enhanced
    
    def forward(self, image):
        """
        Full forward pass: predict parameters and enhance
        
        Args:
            image: Input low-light image [B, 3, H, W]
            
        Returns:
            Enhanced image [B, 3, H, W]
        """
        curve_params = self.dce_net(image)
        enhanced = self.enhance(image, curve_params)
        return enhanced


class ZeroDCEPlusPlus(nn.Module):
    """
    Enhanced Zero-DCE++ with better performance
    Adds attention mechanisms and residual connections
    """
    
    def __init__(self, num_iterations=8, num_filters=32):
        super(ZeroDCEPlusPlus, self).__init__()
        
        self.num_iterations = num_iterations
        
        # Encoder
        self.conv1 = nn.Conv2d(3, num_filters, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(num_filters)
        
        self.conv2 = nn.Conv2d(num_filters, num_filters*2, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(num_filters*2)
        
        self.conv3 = nn.Conv2d(num_filters*2, num_filters*2, 3, padding=1)
        self.bn3 = nn.BatchNorm2d(num_filters*2)
        
        # Attention module
        self.attention = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(num_filters*2, num_filters//4, 1),
            nn.ReLU(),
            nn.Conv2d(num_filters//4, num_filters*2, 1),
            nn.Sigmoid()
        )
        
        # Decoder
        self.conv4 = nn.Conv2d(num_filters*2, num_filters, 3, padding=1)
        self.bn4 = nn.BatchNorm2d(num_filters)
        
        self.conv5 = nn.Conv2d(num_filters, 3 * num_iterations, 3, padding=1)
        
    def forward(self, x):
        # Encoder
        x1 = F.relu(self.bn1(self.conv1(x)))
        x2 = F.relu(self.bn2(self.conv2(x1)))
        x3 = F.relu(self.bn3(self.conv3(x2)))
        
        # Attention
        att = self.attention(x3)
        x3 = x3 * att
        
        # Decoder
        x4 = F.relu(self.bn4(self.conv4(x3)))
        curve_params = torch.tanh(self.conv5(x4))
        
        # Enhance
        curve_params = torch.split(curve_params, 3, dim=1)
        enhanced = x
        for params in curve_params:
            enhanced = enhanced + params * (torch.pow(enhanced, 2) - enhanced)
        
        return enhanced


def create_zero_dce(model_type="standard", num_iterations=8):
    """
    Factory function for Zero-DCE models
    
    Args:
        model_type: "standard" or "plusplus"
        num_iterations: Number of enhancement iterations
        
    Returns:
        Zero-DCE model
    """
    if model_type == "standard":
        return ZeroDCE(num_iterations=num_iterations)
    elif model_type == "plusplus":
        return ZeroDCEPlusPlus(num_iterations=num_iterations)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# Test
if __name__ == "__main__":
    print("Testing Zero-DCE models...\n")
    
    # Test input
    input_image = torch.randn(2, 3, 256, 256)
    
    for model_type in ["standard", "plusplus"]:
        print(f"Testing {model_type} model:")
        model = create_zero_dce(model_type, num_iterations=8)
        model.eval()
        
        # Count parameters
        params = sum(p.numel() for p in model.parameters())
        print(f"  Parameters: {params:,}")
        
        # Forward pass
        with torch.no_grad():
            output = model(input_image)
        
        print(f"  Input shape: {input_image.shape}")
        print(f"  Output shape: {output.shape}")
        print(f"  Output range: [{output.min():.3f}, {output.max():.3f}]")
        print()
    
    print("✅ All models tested successfully!")
