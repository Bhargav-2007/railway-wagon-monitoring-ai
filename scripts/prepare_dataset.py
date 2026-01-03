"""
Prepare and organize training dataset
Expects a zip file with training images
"""

import os
import zipfile
from pathlib import Path
import shutil
import cv2
import json
from datetime import datetime


def setup_dataset_structure():
    """Create dataset directory structure"""
    base_dir = Path("data/datasets")
    
    dirs = [
        "raw",                           # Original dataset
        "processed/blur_detection/train",
        "processed/blur_detection/val",
        "processed/blur_detection/test",
        "processed/deblurring/train/blurred",
        "processed/deblurring/train/sharp",
        "processed/deblurring/val/blurred",
        "processed/deblurring/val/sharp",
        "processed/ocr/train",
        "processed/ocr/val",
        "processed/wagon_detection/train/images",
        "processed/wagon_detection/train/labels",
        "processed/wagon_detection/val/images",
        "processed/wagon_detection/val/labels",
    ]
    
    for d in dirs:
        (base_dir / d).mkdir(parents=True, exist_ok=True)
    
    print("✓ Dataset structure created")
    return base_dir


def extract_dataset(zip_path: str, output_dir: Path):
    """Extract dataset zip file"""
    print(f"Extracting {zip_path}...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir / "raw")
    
    print(f"✓ Extracted to {output_dir / 'raw'}")


def analyze_dataset(data_dir: Path):
    """Analyze dataset contents"""
    print("\n" + "="*60)
    print("DATASET ANALYSIS")
    print("="*60)
    
    image_files = list(data_dir.rglob("*.jpg")) + list(data_dir.rglob("*.png"))
    
    print(f"Total images found: {len(image_files)}")
    
    # Categorize by blur
    blur_counts = {"sharp": 0, "blurred": 0}
    sizes = []
    
    for img_path in image_files[:100]:  # Sample first 100
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            sizes.append(img.shape)
            
            # Quick blur check using Laplacian variance
            laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
            if laplacian_var < 100:
                blur_counts["blurred"] += 1
            else:
                blur_counts["sharp"] += 1
    
    print(f"\nSample analysis (first 100 images):")
    print(f"  Sharp images: {blur_counts['sharp']}")
    print(f"  Blurred images: {blur_counts['blurred']}")
    
    if sizes:
        print(f"\nCommon image sizes:")
        from collections import Counter
        size_counts = Counter(sizes)
        for size, count in size_counts.most_common(5):
            print(f"  {size[1]}x{size[0]}: {count} images")
    
    print("="*60)


def create_dataset_manifest(base_dir: Path):
    """Create manifest file with dataset info"""
    manifest = {
        "created_at": datetime.now().isoformat(),
        "structure": {
            "blur_detection": "Binary classification (sharp/blurred)",
            "deblurring": "Image restoration (blurred -> sharp pairs)",
            "ocr": "Wagon number plate recognition",
            "wagon_detection": "Object detection (bounding boxes)"
        },
        "formats": {
            "blur_detection": "Images in train/val folders with class labels",
            "deblurring": "Paired blurred/sharp images",
            "wagon_detection": "YOLO format (images + txt labels)"
        }
    }
    
    with open(base_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("\n✓ Created dataset manifest")


def main():
    """Main dataset preparation"""
    print("="*60)
    print("RAILWAY DATASET PREPARATION")
    print("="*60 + "\n")
    
    # Setup structure
    base_dir = setup_dataset_structure()
    
    # Check for zip file
    zip_file = input("\nEnter path to dataset zip file (or press Enter to skip): ").strip()
    
    if zip_file and Path(zip_file).exists():
        extract_dataset(zip_file, base_dir)
        analyze_dataset(base_dir / "raw")
    else:
        print("\nNo zip file provided. Place your dataset in:")
        print(f"  {base_dir / 'raw'}")
    
    # Create manifest
    create_dataset_manifest(base_dir)
    
    print("\n" + "="*60)
    print("✅ DATASET PREPARATION COMPLETE")
    print("="*60)
    print(f"\nDataset location: {base_dir}")
    print("\nNext steps:")
    print("1. Place training images in data/datasets/raw/")
    print("2. Run training scripts for each model")
    print("3. Trained models will be saved to ai_pipeline/*/models/")


if __name__ == "__main__":
    main()
