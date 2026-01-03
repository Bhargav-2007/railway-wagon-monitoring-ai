"""
Validate all YAML configuration files
"""
import yaml
from pathlib import Path

def validate_yaml(file_path):
    """Validate single YAML file"""
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"✓ {file_path.name:30s} - Valid")
        return True
    except yaml.YAMLError as e:
        print(f"✗ {file_path.name:30s} - ERROR: {e}")
        return False
    except FileNotFoundError:
        print(f"⚠ {file_path.name:30s} - File not found")
        return False

def main():
    config_dir = Path("ai_pipeline/configs")
    
    config_files = [
        "camera.yaml",
        "blur_detection.yaml",
        "deblurring.yaml",
        "low_light.yaml",
        "ocr.yaml",
        "inference.yaml"
    ]
    
    print("="*60)
    print("YAML CONFIGURATION VALIDATION")
    print("="*60 + "\n")
    
    all_valid = True
    for filename in config_files:
        file_path = config_dir / filename
        if not validate_yaml(file_path):
            all_valid = False
    
    print("\n" + "="*60)
    if all_valid:
        print("✅ ALL CONFIGURATIONS VALID")
    else:
        print("❌ SOME CONFIGURATIONS HAVE ERRORS")
    print("="*60)

if __name__ == "__main__":
    main()
