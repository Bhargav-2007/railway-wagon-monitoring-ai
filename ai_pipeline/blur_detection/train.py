"""
Train blur detection CNN model
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from pathlib import Path
from PIL import Image
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tqdm import tqdm
from ai_pipeline.blur_detection.cnn_model import create_blur_classifier


class BlurDataset(Dataset):
    """Blur detection dataset"""
    
    def __init__(self, data_dir, transform=None):
        self.data_dir = Path(data_dir)
        self.transform = transform
        
        # Load images
        self.samples = []
        
        # Blurred images (label = 1)
        blurred_dir = self.data_dir / "blurred"
        if blurred_dir.exists():
            for img_path in blurred_dir.glob("*.[jp][pn]g"):
                self.samples.append((img_path, 1))
            for img_path in blurred_dir.glob("*.[JP][PN]G"):
                self.samples.append((img_path, 1))
        
        # Sharp images (label = 0)
        sharp_dir = self.data_dir / "sharp"
        if sharp_dir.exists():
            for img_path in sharp_dir.glob("*.[jp][pn]g"):
                self.samples.append((img_path, 0))
            for img_path in sharp_dir.glob("*.[JP][PN]G"):
                self.samples.append((img_path, 0))
        
        print(f"Loaded {len(self.samples)} samples from {data_dir}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        try:
            # Load image
            image = Image.open(img_path).convert('RGB')
            
            if self.transform:
                image = self.transform(image)
            
            return image, label
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            # Return a dummy sample
            return torch.zeros(3, 224, 224), 0


def train_blur_detector():
    """Train blur detection model"""
    
    print("="*60)
    print("TRAINING BLUR DETECTION MODEL")
    print("="*60 + "\n")
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}\n")
    
    # Data transforms
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Datasets
    train_dataset = BlurDataset("data/datasets/processed/blur_detection/train", transform)
    val_dataset = BlurDataset("data/datasets/processed/blur_detection/val", transform)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)  # num_workers=0 for Windows
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=0)
    
    # Model
    model = create_blur_classifier().to(device)
    
    # FIXED: Use CrossEntropyLoss for 2-class output
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)
    
    # Training
    num_epochs = 20
    best_val_acc = 0.0
    
    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch+1}/{num_epochs}")
        print("-" * 40)
        
        # Train phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        
        for images, labels in tqdm(train_loader, desc="Training"):
            images = images.to(device)
            labels = labels.to(device)  # Keep as long tensor for CrossEntropyLoss
            
            # Forward
            optimizer.zero_grad()
            outputs = model(images)  # Shape: [batch_size, 2]
            loss = criterion(outputs, labels)
            
            # Backward
            loss.backward()
            optimizer.step()
            
            # Stats
            train_loss += loss.item()
            predictions = outputs.argmax(dim=1)  # Get predicted class
            train_correct += (predictions == labels).sum().item()
        
        train_loss /= len(train_loader)
        train_acc = train_correct / len(train_dataset) * 100
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        
        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc="Validation"):
                images = images.to(device)
                labels = labels.to(device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                predictions = outputs.argmax(dim=1)
                val_correct += (predictions == labels).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = val_correct / len(val_dataset) * 100
        
        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_path = Path("ai_pipeline/blur_detection/models")
            save_path.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), save_path / "blur_classifier_best.pth")
            print(f"✓ Saved best model (accuracy: {val_acc:.2f}%)")
    
    print("\n" + "="*60)
    print(f"✅ TRAINING COMPLETE")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print("="*60)
    print(f"\nModel saved to: ai_pipeline/blur_detection/models/blur_classifier_best.pth")


if __name__ == "__main__":
    train_blur_detector()
