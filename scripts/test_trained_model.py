"""
Test trained blur detection model
"""

import torch
from torchvision import transforms
from PIL import Image
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_pipeline.blur_detection.cnn_model import create_blur_classifier


def test_model(image_path, model_path="ai_pipeline/blur_detection/models/blur_classifier_best.pth"):
    """Test trained model on single image"""
    
    # Load model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = create_blur_classifier().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # Prepare image
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.softmax(output, dim=1)
        prediction = output.argmax(dim=1).item()
    
    # Results
    sharp_prob = probabilities[0][0].item() * 100
    blur_prob = probabilities[0][1].item() * 100
    
    print("="*60)
    print(f"Testing image: {image_path}")
    print("="*60)
    print(f"Prediction: {'BLURRED' if prediction == 1 else 'SHARP'}")
    print(f"Sharp probability: {sharp_prob:.2f}%")
    print(f"Blur probability: {blur_prob:.2f}%")
    print("="*60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_model(sys.argv[1])
    else:
        print("Usage: python3 scripts/test_trained_model.py <image_path>")
        print("\nExample:")
        print("  python3 scripts/test_trained_model.py test_frame_captured.jpg")
