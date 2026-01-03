"""
Complete system demonstration
Shows all features working together
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import json
from datetime import datetime
from ai_pipeline.pipelines.realtime_pipeline import RailwayMonitoringPipeline


def demo_complete_system():
    """Demonstrate complete railway monitoring system"""
    
    print("\n" + "="*70)
    print("🚂 RAILWAY WAGON MONITORING SYSTEM - COMPLETE DEMO")
    print("="*70 + "\n")
    
    # Initialize pipeline
    print("Initializing AI Pipeline...")
    pipeline = RailwayMonitoringPipeline(device="cpu")
    
    # Test images
    test_images = [
        "test_frame_captured.jpg",
    ]
    
    # Find more test images
    test_dir = Path("data/datasets/processed/blur_detection/test")
    if test_dir.exists():
        sharp_imgs = list((test_dir / "sharp").glob("*.jpg"))[:2]
        blur_imgs = list((test_dir / "blurred").glob("*.jpg"))[:2]
        test_images.extend([str(img) for img in sharp_imgs + blur_imgs])
    
    print(f"\nProcessing {len(test_images)} test images...\n")
    
    results_summary = []
    
    for idx, img_path in enumerate(test_images, 1):
        if not Path(img_path).exists():
            print(f"⚠ Skipping {img_path} (not found)")
            continue
        
        print(f"\n{'='*70}")
        print(f"IMAGE {idx}: {Path(img_path).name}")
        print(f"{'='*70}")
        
        # Load image
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"❌ Could not load {img_path}")
            continue
        
        print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
        
        # Process
        results = pipeline.process_frame(frame, skip_heavy=True)
        
        # Display results
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"├─ Blur Detected: {'YES ❌' if results['blur']['is_blurred'] else 'NO ✓'}")
        print(f"├─ Blur Score: {results['blur']['score']:.2f}")
        print(f"├─ Processing Time: {results['processing_time']:.3f}s")
        print(f"├─ FPS: {results['fps']:.1f}")
        print(f"├─ Wagons Detected: {results['wagons']['total_count']}")
        print(f"└─ Wagon IDs: {len(results['ocr']['wagon_ids'])}")
        
        if results['ocr']['wagon_ids']:
            for wagon in results['ocr']['wagon_ids']:
                print(f"    └─ {wagon['text']} (confidence: {wagon['confidence']:.2f})")
        
        # Save visualization
        vis = pipeline.visualize_results(results['processed_frame'], results)
        output_path = f"demo_output_{idx}_{Path(img_path).stem}.jpg"
        cv2.imwrite(output_path, vis)
        print(f"\n✓ Saved visualization: {output_path}")
        
        # Store summary
        results_summary.append({
            "image": Path(img_path).name,
            "blur_detected": results['blur']['is_blurred'],
            "blur_score": results['blur']['score'],
            "wagons": results['wagons']['total_count'],
            "wagon_ids": [w['text'] for w in results['ocr']['wagon_ids']],
            "processing_time": results['processing_time'],
            "fps": results['fps']
        })
    
    # Final summary
    print("\n" + "="*70)
    print("📈 SYSTEM PERFORMANCE SUMMARY")
    print("="*70)
    
    if results_summary:
        total_images = len(results_summary)
        blurred_count = sum(1 for r in results_summary if r['blur_detected'])
        avg_time = sum(r['processing_time'] for r in results_summary) / total_images
        avg_fps = sum(r['fps'] for r in results_summary) / total_images
        total_wagons = sum(r['wagons'] for r in results_summary)
        
        print(f"Total Images Processed: {total_images}")
        print(f"Blurred Images: {blurred_count} ({blurred_count/total_images*100:.1f}%)")
        print(f"Total Wagons Detected: {total_wagons}")
        print(f"Average Processing Time: {avg_time:.3f}s")
        print(f"Average FPS: {avg_fps:.1f}")
        
        # Save JSON report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_images": total_images,
                "blurred_count": blurred_count,
                "total_wagons": total_wagons,
                "avg_processing_time": avg_time,
                "avg_fps": avg_fps
            },
            "details": results_summary
        }
        
        with open("demo_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Detailed report saved: demo_report.json")
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE - System fully operational!")
    print("="*70)
    print("\n💡 Next Steps:")
    print("  1. Start backend: cd backend && python -m uvicorn app.main:app --reload")
    print("  2. Open dashboard: firefox frontend/simple_dashboard.html")
    print("  3. Upload images and see real-time results!")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    demo_complete_system()
