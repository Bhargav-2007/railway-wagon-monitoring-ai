"""
Train NAFNet deblurring model
Simplified training script
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from pathlib import Path
from PIL import Image
from tqdm import tqdm

from model import create_nafnet_deblur


class DeblurDataset(Dataset):
    """Paired blur/sharp dataset"""
    
    def __init__(self, data_dir, transform=None):
        self.data_dir = Path(data_dir)
        self.transform = transform
        
        # Load paired images
        blurred_dir = self.data_dir / "blurred"
        sharp_dir = self.data_dir / "sharp"
        
        self.blurred_images = sorted(list(blurred_dir.glob("*.[jp][pn]g")))
        self.sharp_images = sorted(list(sharp_dir.glob("*.[jp][pn]g")))
        
        # Match by filename
        self.pairs = []
        for blur_path in self.blurred_images:
            sharp_path = sharp_dir / blur_path.name
            if sharp_path.exists():
                self.pairs.append((blur_path, sharp_path))
        
        print(f"Loaded {len(self.pairs)} image pairs from {data_dir}")
    
    def __len__(self):
        return len(self.pairs)
    
    def __getitem__(self, idx):
        blur_path, sharp_path = self.pairs[idx]
        
        blur_img = Image.open(blur_path).convert('RGB')
        sharp_img = Image.open(sharp_path).convert('RGB')
        
        if self.transform:
            blur_img = self.transform(blur_img)
            sharp_img = self.transform(sharp_img)
        
        return blur_img, sharp_img


def train_deblur_model():
    """Train deblurring model"""
    
    print("="*60)
    print("TRAINING DEBLURRING MODEL")
    print("="*60 + "\n")
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}\n")
    
    # Transforms
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor()
    ])
    
    # Datasets
    train_dataset = DeblurDataset("data/datasets/processed/deblurring/train", transform)
    val_dataset = DeblurDataset("data/datasets/processed/deblurring/val", transform)
    
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False, num_workers=2)
    
    # Model
    model = create_nafnet_deblur().to(device)
    
    # Loss
    criterion = nn.L1Loss()
    
    # Optimizer
    optimizer = optim.Adam(model.parameters(), lr=0.0001)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)
    
    # Training
    num_epochs = 50
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch+1}/{num_epochs}")
        print("-" * 40)
        
        # Train
        model.train()
        train_loss = 0.0
        
        for blur, sharp in tqdm(train_loader, desc="Training"):
            blur = blur.to(device)
            sharp = sharp.to(device)
            
            optimizer.zero_grad()
            output = model(blur)
            loss = criterion(output, sharp)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for blur, sharp in tqdm(val_loader, desc="Validation"):
                blur = blur.to(device)
                sharp = sharp.to(device)
                
                output = model(blur)
                loss = criterion(output, sharp)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        
        print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        
        scheduler.step()
        
        # Save best
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "ai_pipeline/deblurring/models/nafnet_deblur_best.pth")
            print(f"✓ Saved best model (loss: {val_loss:.4f})")
    
    print("\n" + "="*60)
    print(f"✅ TRAINING COMPLETE")
    print(f"Best validation loss: {best_val_loss:.4f}")
    print("="*60)


if __name__ == "__main__":
    train_deblur_model()
