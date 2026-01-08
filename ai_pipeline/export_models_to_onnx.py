"""
ONNX Model Export Utility
Exports all neural network models to ONNX format for TensorRT deployment on Jetson AGX

Author: Team Member 2 (CV & Motion Blur Specialist)
Purpose: Enable edge deployment via TensorRT optimization
"""

import os
import sys
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

# Only import ultralytics if YOLO is being used
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("WARNING: ultralytics not available. YOLO export skipped.")

class ONNXExporter:
    """
    Utility class to export models to ONNX format
    Opset 13 ensures TensorRT 8.0+ compatibility
    """
    
    def __init__(self, output_dir: str = "ai_pipeline/models"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.export_results = {}
    
    def export_yolo_detector(self, model_path: str, export_name: str = "yolov8m") -> Dict:
        """
        Export YOLOv8 wagon detector to ONNX
        
        Args:
            model_path: Path to .pt model file
            export_name: Output ONNX filename (without extension)
        
        Returns:
            Dictionary with export status and specs
        """
        if not YOLO_AVAILABLE:
            return {"status": "skipped", "reason": "ultralytics not installed"}
        
        try:
            print(f"\n[YOLO Export] Loading model from {model_path}...")
            model = YOLO(model_path)
            
            output_path = self.output_dir / f"{export_name}.onnx"
            
            print(f"[YOLO Export] Exporting to ONNX (opset=13, simplify=True)...")
            model.export(
                format='onnx',
                opset=13,
                simplify=True,
                dynamic=False,  # Static shape for Jetson
                imgsz=640
            )
            
            # Verify export
            if os.path.exists(output_path):
                file_size_mb = os.path.getsize(output_path) / (1024**2)
                result = {
                    "status": "success",
                    "output_file": str(output_path),
                    "file_size_mb": round(file_size_mb, 2),
                    "model_type": "YOLOv8 Wagon Detector",
                    "opset": 13,
                    "input_shape": (1, 3, 640, 640),
                    "output_type": "Detections + Confidence"
                }
                print(f"[YOLO Export] SUCCESS: {output_path} ({file_size_mb:.2f} MB)")
                return result
            else:
                return {"status": "failed", "reason": "Export file not created"}
        
        except Exception as e:
            print(f"[YOLO Export] ERROR: {str(e)}")
            return {"status": "failed", "reason": str(e)}
    
    def export_damage_classifier(self, model_path: str, export_name: str = "damage_classifier") -> Dict:
        """
        Export PyTorch damage classifier to ONNX
        Typical: ResNet50 or EfficientNet backbone
        
        Args:
            model_path: Path to .pt model file
            export_name: Output ONNX filename
        
        Returns:
            Dictionary with export status and specs
        """
        try:
            print(f"\n[Damage Classifier Export] Loading model from {model_path}...")
            model = torch.load(model_path, map_location='cpu')
            model.eval()
            
            # Create dummy input (batch_size=1, channels=3, height=224, width=224)
            dummy_input = torch.randn(1, 3, 224, 224)
            
            output_path = self.output_dir / f"{export_name}.onnx"
            
            print(f"[Damage Classifier Export] Exporting to ONNX (opset=13)...")
            torch.onnx.export(
                model,
                dummy_input,
                str(output_path),
                opset_version=13,
                input_names=['image'],
                output_names=['logits'],
                dynamic_axes=None,  # Static for Jetson
                verbose=False
            )
            
            if os.path.exists(output_path):
                file_size_mb = os.path.getsize(output_path) / (1024**2)
                result = {
                    "status": "success",
                    "output_file": str(output_path),
                    "file_size_mb": round(file_size_mb, 2),
                    "model_type": "Damage Classifier (ResNet50)",
                    "opset": 13,
                    "input_shape": (1, 3, 224, 224),
                    "output_classes": 3  # (no_damage, minor, severe)
                }
                print(f"[Damage Classifier Export] SUCCESS: {output_path} ({file_size_mb:.2f} MB)")
                return result
            else:
                return {"status": "failed", "reason": "Export file not created"}
        
        except Exception as e:
            print(f"[Damage Classifier Export] ERROR: {str(e)}")
            return {"status": "failed", "reason": str(e)}
    
    def export_all_models(self, config: Dict) -> Dict[str, Dict]:
        """
        Export all models based on config
        
        Args:
            config: Dictionary with paths to model files
        
        Returns:
            Dictionary mapping model names to export results
        """
        print("\n" + "="*70)
        print("ONNX MODEL EXPORT - JETSON AGX DEPLOYMENT")
        print("="*70)
        
        results = {}
        
        # Export YOLO detector
        if 'yolo_model_path' in config:
            results['yolo_detector'] = self.export_yolo_detector(
                config['yolo_model_path'],
                config.get('yolo_export_name', 'yolov8m')
            )
        
        # Export damage classifier
        if 'damage_classifier_path' in config:
            results['damage_classifier'] = self.export_damage_classifier(
                config['damage_classifier_path'],
                config.get('damage_export_name', 'damage_classifier')
            )
        
        print("\n" + "="*70)
        print("EXPORT SUMMARY")
        print("="*70)
        
        for model_name, result in results.items():
            status = result.get('status', 'unknown')
            print(f"\n{model_name}:")
            print(f"  Status: {status}")
            if status == 'success':
                print(f"  File: {result['output_file']}")
                print(f"  Size: {result['file_size_mb']} MB")
                print(f"  Type: {result.get('model_type', 'N/A')}")
                print(f"  Input Shape: {result.get('input_shape', 'N/A')}")
            else:
                print(f"  Reason: {result.get('reason', 'Unknown')}")
        
        self.export_results = results
        return results
    
    def generate_tensorrt_commands(self) -> List[str]:
        """
        Generate TensorRT conversion commands for Jetson deployment
        To be run ON the Jetson AGX device
        """
        commands = [
            "# Run these commands ON Jetson AGX after deployment",
            "# Requires: trtexec (part of TensorRT)",
            ""
        ]
        
        for model_name, result in self.export_results.items():
            if result.get('status') == 'success':
                onnx_file = result['output_file']
                engine_name = onnx_file.replace('.onnx', '.engine')
                
                if 'yolo' in model_name.lower():
                    cmd = f"trtexec --onnx={onnx_file} --saveEngine={engine_name} --fp16 --workspace=1024"
                else:
                    cmd = f"trtexec --onnx={onnx_file} --saveEngine={engine_name} --fp16 --workspace=512"
                
                commands.append(cmd)
        
        return commands


def main():
    """
    Example usage and export execution
    """
    exporter = ONNXExporter(output_dir="ai_pipeline/models")
    
    # Configuration: Point to your actual model files
    config = {
        # 'yolo_model_path': 'ai_pipeline/models/yolov8m.pt',  # Uncomment if available
        # 'damage_classifier_path': 'ai_pipeline/models/damage_classifier.pt',  # Uncomment if available
    }
    
    # Check if actual model files exist and add to config
    yolo_path = Path('ai_pipeline/models/yolov8m.pt')
    damage_path = Path('ai_pipeline/models/damage_classifier.pt')
    
    if yolo_path.exists():
        config['yolo_model_path'] = str(yolo_path)
    else:
        print(f"\nWARNING: YOLO model not found at {yolo_path}")
        print("  (Expected if using pretrained models loaded at runtime)")
    
    if damage_path.exists():
        config['damage_classifier_path'] = str(damage_path)
    else:
        print(f"\nWARNING: Damage classifier not found at {damage_path}")
        print("  (Expected if using transfer learning models)")
    
    # Export all available models
    results = exporter.export_all_models(config)
    
    # Generate TensorRT commands
    tensorrt_commands = exporter.generate_tensorrt_commands()
    
    print("\n" + "="*70)
    print("TENSORRT CONVERSION COMMANDS (for Jetson AGX)")
    print("="*70)
    for cmd in tensorrt_commands:
        print(cmd)
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Verify ONNX files in: ai_pipeline/models/
2. Transfer .onnx files to Jetson AGX
3. On Jetson, run the TensorRT commands above
4. Use generated .engine files in production
5. See EDGE_DEPLOYMENT_READINESS.md for detailed guide
    """)


if __name__ == "__main__":
    main()
