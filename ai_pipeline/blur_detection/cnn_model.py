"""
CNN-based blur detection classifier
Lightweight model for real-time blur assessment
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class BlurClassifierCNN(nn.Module):
    """Lightweight CNN for binary blur classification"""
    
    def __init__(self, input_size: int = 224, num_classes: int = 2):
        """
        Initialize blur classifier
        
        Args:
            input_size: Input image size (assumes square images)
            num_classes: Number of classes (2 for blur/sharp)
        """
        super(BlurClassifierCNN, self).__init__()
        
        self.input_size = input_size
        self.num_classes = num_classes
        
        # Feature extraction layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=5, stride=2, padding=2)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Global average pooling
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Classifier
        self.fc1 = nn.Linear(256, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, num_classes)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Input tensor [batch_size, 3, height, width]
            
        Returns:
            Output logits [batch_size, num_classes]
        """
        # Feature extraction
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)
        
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.pool3(x)
        
        x = F.relu(self.bn4(self.conv4(x)))
        x = self.pool4(x)
        
        # Global pooling
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        
        # Classification
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x
    
    def predict(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Make prediction with confidence scores
        
        Args:
            x: Input tensor
            
        Returns:
            Tuple of (predicted_class, confidence_score)
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probs = F.softmax(logits, dim=1)
            confidence, predicted = torch.max(probs, dim=1)
        return predicted, confidence


class LightBlurClassifier(nn.Module):
    """Ultra-lightweight blur classifier for edge devices"""
    
    def __init__(self):
        super(LightBlurClassifier, self).__init__()
        
        # Depthwise separable convolutions for efficiency
        self.conv1 = nn.Conv2d(3, 32, 3, stride=2, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        
        self.dw_conv2 = nn.Conv2d(32, 32, 3, stride=2, padding=1, groups=32)
        self.pw_conv2 = nn.Conv2d(32, 64, 1)
        self.bn2 = nn.BatchNorm2d(64)
        
        self.dw_conv3 = nn.Conv2d(64, 64, 3, stride=2, padding=1, groups=64)
        self.pw_conv3 = nn.Conv2d(64, 128, 1)
        self.bn3 = nn.BatchNorm2d(128)
        
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(128, 2)
        
    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        
        x = self.dw_conv2(x)
        x = F.relu(self.bn2(self.pw_conv2(x)))
        
        x = self.dw_conv3(x)
        x = F.relu(self.bn3(self.pw_conv3(x)))
        
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        
        return x


def create_blur_classifier(model_type: str = "standard", pretrained: bool = False):
    """
    Factory function to create blur classifier
    
    Args:
        model_type: "standard" or "lightweight"
        pretrained: Load pretrained weights (if available)
        
    Returns:
        Blur classifier model
    """
    if model_type == "standard":
        model = BlurClassifierCNN()
    elif model_type == "lightweight":
        model = LightBlurClassifier()
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return model


# Test function
if __name__ == "__main__":
    # Test model creation and forward pass
    model = create_blur_classifier("standard")
    print(f"Model: {model.__class__.__name__}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    
    # Test forward pass
    batch_size = 4
    dummy_input = torch.randn(batch_size, 3, 224, 224)
    
    model.eval()
    with torch.no_grad():
        output = model(dummy_input)
        predicted, confidence = model.predict(dummy_input)
    
    print(f"\nInput shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Predictions: {predicted}")
    print(f"Confidence: {confidence}")
    
    # Test lightweight model
    print("\n" + "="*60)
    light_model = create_blur_classifier("lightweight")
    print(f"Lightweight Model: {light_model.__class__.__name__}")
    
    light_params = sum(p.numel() for p in light_model.parameters())
    print(f"Parameters: {light_params:,} ({light_params/total_params*100:.1f}% of standard)")
    
    with torch.no_grad():
        light_output = light_model(dummy_input)
    print(f"Output shape: {light_output.shape}")
    
    print("\n✅ Model test completed successfully!")
