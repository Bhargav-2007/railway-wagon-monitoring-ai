"""
Organize blur/sharp dataset for training
Input: data/datasets/raw/blurred/ and data/datasets/raw/sharp/
Output: Organized train/val/test splits
"""

import os
import shutil
from pathlib import Path
import random
from PIL import Image
import json

def organize_dataset():
    """Organize blur detection and deblurring datasets"""
    
    print("="*60)
    print("ORGANIZING BLUR DATASET")
    print("="*60 + "\n")
    
    # Paths
    raw_dir = Path("data/datasets/raw")
    blurred_dir = raw_dir / "blurred"
    sharp_dir = raw_dir / "sharp"
    
    # Check if directories exist
    if not blurred_dir.exists() or not sharp_dir.exists():
        print("❌ Error: Dataset directories not found!")
        print(f"Expected:")
        print(f"  - {blurred_dir}")
        print(f"  - {sharp_dir}")
        print("\nPlease copy your dataset first:")
        print("  cp /mnt/d/blurred_sharp/blurred/* data/datasets/raw/blurred/")
        print("  cp /mnt/d/blurred_sharp/sharp/* data/datasets/raw/sharp/")
        return
    
    # Count images
    blurred_images = list(blurred_dir.glob("*.[jp][pn]g")) + list(blurred_dir.glob("*.[JP][PN]G"))
    sharp_images = list(sharp_dir.glob("*.[jp][pn]g")) + list(sharp_dir.glob("*.[JP][PN]G"))
    
    print(f"Found {len(blurred_images)} blurred images")
    print(f"Found {len(sharp_images)} sharp images")
    
    if len(blurred_images) == 0 or len(sharp_images) == 0:
        print("\n❌ No images found! Check the file extensions.")
        return
    
    # Create output directories
    output_base = Path("data/datasets/processed")
    
    # For blur detection (classification)
    blur_det_dirs = {
        'train/blurred': output_base / "blur_detection/train/blurred",
        'train/sharp': output_base / "blur_detection/train/sharp",
        'val/blurred': output_base / "blur_detection/val/blurred",
        'val/sharp': output_base / "blur_detection/val/sharp",
        'test/blurred': output_base / "blur_detection/test/blurred",
        'test/sharp': output_base / "blur_detection/test/sharp",
    }
    
    # For deblurring (paired images)
    deblur_dirs = {
        'train/blurred': output_base / "deblurring/train/blurred",
        'train/sharp': output_base / "deblurring/train/sharp",
        'val/blurred': output_base / "deblurring/val/blurred",
        'val/sharp': output_base / "deblurring/val/sharp",
    }
    
    # Create all directories
    for dir_path in list(blur_det_dirs.values()) + list(deblur_dirs.values()):
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("\n✓ Created output directories")
    
    # Split ratios
    train_ratio = 0.7  # 70% training
    val_ratio = 0.15   # 15% validation
    test_ratio = 0.15  # 15% testing
    
    # Process blurred images
    print(f"\nProcessing blurred images...")
    random.shuffle(blurred_images)
    
    n_train = int(len(blurred_images) * train_ratio)
    n_val = int(len(blurred_images) * val_ratio)
    
    train_blur = blurred_images[:n_train]
    val_blur = blurred_images[n_train:n_train+n_val]
    test_blur = blurred_images[n_train+n_val:]
    
    print(f"  Train: {len(train_blur)}")
    print(f"  Val:   {len(val_blur)}")
    print(f"  Test:  {len(test_blur)}")
    
    # Copy blurred images
    for img in train_blur:
        shutil.copy(img, blur_det_dirs['train/blurred'] / img.name)
        shutil.copy(img, deblur_dirs['train/blurred'] / img.name)
    
    for img in val_blur:
        shutil.copy(img, blur_det_dirs['val/blurred'] / img.name)
        shutil.copy(img, deblur_dirs['val/blurred'] / img.name)
    
    for img in test_blur:
        shutil.copy(img, blur_det_dirs['test/blurred'] / img.name)
    
    # Process sharp images
    print(f"\nProcessing sharp images...")
    random.shuffle(sharp_images)
    
    train_sharp = sharp_images[:n_train]
    val_sharp = sharp_images[n_train:n_train+n_val]
    test_sharp = sharp_images[n_train+n_val:]
    
    print(f"  Train: {len(train_sharp)}")
    print(f"  Val:   {len(val_sharp)}")
    print(f"  Test:  {len(test_sharp)}")
    
    # Copy sharp images
    for img in train_sharp:
        shutil.copy(img, blur_det_dirs['train/sharp'] / img.name)
        shutil.copy(img, deblur_dirs['train/sharp'] / img.name)
    
    for img in val_sharp:
        shutil.copy(img, blur_det_dirs['val/sharp'] / img.name)
        shutil.copy(img, deblur_dirs['val/sharp'] / img.name)
    
    for img in test_sharp:
        shutil.copy(img, blur_det_dirs['test/sharp'] / img.name)
    
    print("\n✓ Images organized successfully!")
    
    # Create metadata
    metadata = {
        "total_images": {
            "blurred": len(blurred_images),
            "sharp": len(sharp_images)
        },
        "splits": {
            "train": {"blurred": len(train_blur), "sharp": len(train_sharp)},
            "val": {"blurred": len(val_blur), "sharp": len(val_sharp)},
            "test": {"blurred": len(test_blur), "sharp": len(test_sharp)}
        },
        "ratios": {
            "train": train_ratio,
            "val": val_ratio,
            "test": test_ratio
        }
    }
    
    with open(output_base / "dataset_info.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ DATASET ORGANIZATION COMPLETE")
    print("="*60)
    print(f"\nDatasets created:")
    print(f"1. Blur Detection: {output_base / 'blur_detection'}")
    print(f"2. Deblurring: {output_base / 'deblurring'}")
    print(f"\nMetadata saved: {output_base / 'dataset_info.json'}")
    print("\nReady for training! 🚀")


if __name__ == "__main__":
    organize_dataset()
