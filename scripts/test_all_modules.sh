#!/bin/bash

echo "======================================"
echo "Testing All AI Modules"
echo "======================================"
echo ""

# Activate venv
source venv/bin/activate

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test function
test_module() {
    echo "Testing: $1"
    if python3 "$2" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $1 passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $1 failed${NC}"
        return 1
    fi
}

# Run tests
test_module "Camera Stream" "ai_pipeline/ingestion/camera_stream.py"
test_module "Blur Detection Model" "ai_pipeline/blur_detection/cnn_model.py"
test_module "Classical Metrics" "ai_pipeline/blur_detection/classical_metrics.py"
test_module "NAFNet Model" "ai_pipeline/deblurring/model.py"
test_module "Zero-DCE Model" "ai_pipeline/low_light_enhancement/model.py"
test_module "Config Validator" "scripts/validate_configs.py"

echo ""
echo "======================================"
echo "Test Suite Complete"
echo "======================================"
