import cv2
import os
from ai_pipeline.modules.blur_detection import BlurDetector

print("\n" + "="*80)
print("COMPREHENSIVE BLUR DETECTION TEST")
print("="*80)

# Test images
test_images = {
    '166.jpg': 'BLURRED (motion blur car)',
    'test_frame_captured.jpg': 'Unknown quality'
}

# Add any other images you have
for f in os.listdir('.'):
    if f.endswith(('.jpg', '.png', '.jpeg')) and f not in test_images:
        test_images[f] = 'Unknown'

# Test with different thresholds
thresholds = [80, 100, 150, 200]

for threshold in thresholds:
    print(f"\n{'='*80}")
    print(f"TESTING WITH THRESHOLD: {threshold}")
    print(f"{'='*80}")
    
    detector = BlurDetector(threshold=threshold)
    
    for img_path, expected in test_images.items():
        try:
            img = cv2.imread(img_path)
            if img is None:
                continue
            
            result = detector.detect_blur(img)
            
            status = "🔴 BLURRED" if result['is_blurred'] else "🟢 SHARP"
            
            print(f"\n📸 {img_path}")
            print(f"   Expected: {expected}")
            print(f"   Result: {status} ({result['quality']})")
            print(f"   Score: {result['blur_score']:.2f}")
            print(f"   Laplacian: {result['laplacian_var']:.2f}")
            print(f"   Confidence: {result['confidence']:.2%}")
            
        except Exception as e:
            print(f"\n❌ Error with {img_path}: {e}")

print("\n" + "="*80)
print("📊 RECOMMENDATION:")
print("   Choose threshold where:")
print("   - Blurred images show: 🔴 BLURRED")
print("   - Sharp images show: 🟢 SHARP")
print("   Suggested: threshold = 100")
print("="*80)
