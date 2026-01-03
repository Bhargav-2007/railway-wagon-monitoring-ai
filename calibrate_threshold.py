import cv2
from ai_pipeline.modules.blur_detection import BlurDetector

# Your images
blurred_image = '166.jpg'  # Known blurred
sharp_image = 'sharp_test.jpg'  # Known sharp (if you have one)

print("\n" + "="*80)
print("THRESHOLD CALIBRATION")
print("="*80)

# Test blurred image
print("\n🔴 Testing BLURRED image (166.jpg):")
img_blur = cv2.imread(blurred_image)
if img_blur is not None:
    for thresh in [80, 100, 120, 150]:
        detector = BlurDetector(threshold=thresh)
        result = detector.detect_blur(img_blur)
        status = "✅ Correct" if result['is_blurred'] else "❌ Wrong"
        print(f"   Threshold {thresh}: {status} (score: {result['blur_score']:.1f})")

# Test sharp image (if available)
print("\n🟢 Testing SHARP image:")
try:
    img_sharp = cv2.imread(sharp_image)
    if img_sharp is not None:
        for thresh in [80, 100, 120, 150]:
            detector = BlurDetector(threshold=thresh)
            result = detector.detect_blur(img_sharp)
            status = "✅ Correct" if not result['is_blurred'] else "❌ Wrong"
            print(f"   Threshold {thresh}: {status} (score: {result['blur_score']:.1f})")
    else:
        print("   No sharp test image found")
except:
    print("   No sharp test image available")

print("\n" + "="*80)
print("💡 RECOMMENDED THRESHOLD:")
print("   Use the threshold where BOTH images are correctly detected")
print("   Typically: 100-120 works best")
print("="*80)
