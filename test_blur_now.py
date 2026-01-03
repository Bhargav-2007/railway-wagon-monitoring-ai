import cv2
from ai_pipeline.modules.blur_detection import BlurDetector

# Test images
images = ['166.jpg', 'test_frame_captured.jpg']

print("\n" + "="*70)
print("BLUR DETECTION TEST")
print("="*70)

for img_path in images:
    try:
        img = cv2.imread(img_path)
        if img is None:
            print(f"\n❌ {img_path} not found")
            continue
            
        print(f"\n📸 Testing: {img_path}")
        print("-" * 70)
        
        detector = BlurDetector(threshold=150.0)
        result = detector.detect_blur(img)
        
        status = "🔴 BLURRED" if result['is_blurred'] else "🟢 SHARP"
        print(f"Result: {status}")
        print(f"Score: {result['blur_score']:.2f}")
        print(f"Threshold: {result['threshold']:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*70)
