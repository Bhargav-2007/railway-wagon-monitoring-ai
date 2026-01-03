"""
Automatically fix all import paths in the project
"""
import os
from pathlib import Path

def fix_file_imports(file_path):
    """Fix imports in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # Define replacements
    replacements = {
        'from classical_metrics import': 'from ai_pipeline.blur_detection.classical_metrics import',
        'from cnn_model import': 'from ai_pipeline.blur_detection.cnn_model import',
        'from model import create_nafnet_deblur': 'from ai_pipeline.deblurring.model import create_nafnet_deblur',
        'from model import create_zero_dce': 'from ai_pipeline.low_light_enhancement.model import create_zero_dce',
        'from text_detector import TextDetector': 'from ai_pipeline.downstream_tasks.ocr.text_detector import TextDetector',
        'from text_recognizer import TextRecognizer': 'from ai_pipeline.downstream_tasks.ocr.recognizer import TextRecognizer',
    }
    
    # Apply replacements
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Write back if changed
    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all Python files"""
    project_root = Path('ai_pipeline')
    python_files = list(project_root.rglob('*.py'))
    
    print("Fixing import paths...\n")
    fixed_count = 0
    
    for py_file in python_files:
        if fix_file_imports(py_file):
            print(f"✓ Fixed: {py_file}")
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
