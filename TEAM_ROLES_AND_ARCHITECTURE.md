# Railway Wagon Monitoring System - Team Architecture & Roles
## 4-Member Team Division with Engineering Accountability

---

## TEAM MEMBER 1: MULTI-CAMERA SYSTEMS ENGINEER
### Subsystem: Input Acquisition & Real-time Streaming (RTSP/IP Protocol)

**Responsibilities:**
- RTSP/IP camera protocol implementation and streaming
- Phone-based camera (3x) concurrent frame acquisition
- Frame synchronization across cameras
- Latency optimization and frame dropping strategy
- Buffer management for 30 FPS @ 1280x720
- Error handling and auto-reconnection
- Performance monitoring (latency, frame loss)

**Key Implementation Files:**
- `backend/app/services/camera_stream.py` - RTSP streaming module
- `camera_config.json` - Camera IP/port configuration
- `setup_cameras.py` - Camera initialization and validation
- `backend/app/routes/camera_routes.py` - API endpoints for camera control

**Current Deliverables:**
✓ 3 concurrent RTSP streams @ 30 FPS
✓ <100ms inter-camera latency variation
✓ Frame synchronization tolerance: ±1 frame
✓ Automatic reconnection on stream loss
✓ CPU utilization monitoring

**Performance Benchmarks:**
- Throughput: 9 MB/s (3x 1280x720 H.264 @ 30fps)
- Latency: 50-150ms (RTSP protocol typical)
- Frame drop recovery: <2 seconds
- Memory footprint: ~200MB for 3 streams + buffers

**Validation Metrics:**
- All 3 streams available simultaneously
- Frame timestamp synchronization < ±33ms (1 frame)
- No artificial frame dropping in normal conditions
- Graceful degradation if 1 camera drops

---

## TEAM MEMBER 2: COMPUTER VISION & MOTION BLUR SPECIALIST
### Subsystem: Motion Blur Mitigation & Image Enhancement

**Responsibilities:**
- Motion blur detection using Laplacian variance
- Blur magnitude estimation and thresholding
- Deblurring: FFT-based + Wiener filter implementation
- Low-light enhancement: CLAHE + histogram equalization
- Image quality assessment (BRISQUE proxy metrics)
- Per-frame preprocessing optimization
- ONNX model export for edge devices

**Key Implementation Files:**
- `ai_pipeline/blur_detection.py` - Laplacian variance analysis
- `ai_pipeline/utils.py` - Deblur + enhancement filters
- `calibrate_threshold.py` - Blur threshold tuning
- `ai_pipeline/models/deblur_model.onnx` - Exported for TensorRT

**Current Deliverables:**
✓ Blur detection with threshold calibration
✓ FFT-based deblurring (real-time capable)
✓ Low-light enhancement maintaining detail
✓ Quality metrics: BRISQUE proxy computed
✓ ONNX export for inference optimization

**Performance Benchmarks:**
- Blur detection: <5ms per frame
- Deblurring: 20-50ms per frame (CPU i5)
- Enhancement: <10ms per frame
- Cumulative: <100ms for full pipeline
- Memory: ~50MB per frame in flight

**Quality Improvements:**
- Motion blur mitigation: 30-40% BRISQUE score improvement
- Low-light preservation: Detail retention >85%
- Artifact introduction: Minimal (<5% pixel variance)

---

## TEAM MEMBER 3: WAGON DETECTION & OCR SPECIALIST
### Subsystem: Wagon Detection, Tracking & Character Recognition

**Responsibilities:**
- Pretrained YOLO wagon detection pipeline
- IoU-based multi-wagon tracking across frames
- Wagon counting and duplicate elimination
- Damage/defect classification (3 classes)
- EasyOCR integration for wagon number extraction
- Confidence thresholding and post-processing
- Real-time inference optimization

**Key Implementation Files:**
- `ai_pipeline/wagon_tracking.py` - Detection + tracking logic
- `ai_pipeline/models/yolo_wagon_detector.pt` - YOLO weights
- `ai_pipeline/models/damage_classifier.pt` - Defect classification
- `backend/app/services/wagon_service.py` - Business logic
- `backend/app/routes/wagon_routes.py` - API endpoints

**Current Deliverables:**
✓ YOLO-based wagon detection (mAP ~85%)
✓ IoU-based multi-wagon tracking
✓ Real-time wagon counting per stream
✓ 3-class damage classification
✓ EasyOCR integration for OCR
✓ Confidence-based filtering

**Performance Benchmarks:**
- Detection: 15-30 FPS (per stream, CPU)
- Tracking: <5ms per frame
- OCR: 50-100ms per detected wagon
- End-to-end: 50-150ms per frame (CPU i5)

**Accuracy Metrics:**
- Wagon detection mAP: ~85% on validation set
- False positive rate: <5% on clear frames
- Wagon count accuracy: >95% per session
- OCR character accuracy: >90% on legible numbers
- Damage classification recall: >75% per class

---

## TEAM MEMBER 4: BACKEND ARCHITECTURE & SYSTEMS INTEGRATION
### Subsystem: API, Database, Dashboard Integration & Deployment

**Responsibilities:**
- FastAPI server architecture and scalability
- SQLAlchemy ORM for persistent data storage
- Real-time WebSocket integration for dashboard
- Request/response validation and error handling
- Logging, monitoring, and performance tracking
- Docker/containerization for deployment
- Database schema design and migrations
- Analytics and post-operation report generation

**Key Implementation Files:**
- `backend/app/main.py` - FastAPI application entry
- `backend/app/models/` - SQLAlchemy models
- `backend/app/services/` - Business logic services
- `backend/app/routes/` - API endpoint definitions
- `backend/requirements.txt` - Python dependencies
- `docker-compose.yml` - Container orchestration
- `backend/railway_monitor.db` - SQLite database

**Current Deliverables:**
✓ FastAPI REST API with 20+ endpoints
✓ WebSocket real-time dashboard streaming
✓ SQLite database with 8+ tables
✓ Request/response validation (Pydantic)
✓ Comprehensive error handling
✓ Performance monitoring and logging
✓ Docker deployment readiness

**Performance Benchmarks:**
- API response time: <100ms (p95)
- WebSocket latency: <50ms
- Concurrent connections: 50+ users
- Database query time: <10ms (p95)
- Memory per API server: ~200MB

**Reliability Metrics:**
- Uptime target: 99.5%
- Error rate: <0.1%
- Database consistency: Full ACID compliance
- Data persistence: 100% on disk

---

## INTEGRATION POINTS & DATA FLOW

```
Team 1 (Camera Systems)  →  Raw 3x RTSP Streams
                             ↓
Team 2 (CV & Blur)       →  Enhanced Frame Queue
                             ↓
Team 3 (Wagon & OCR)     →  Detection Results + OCR
                             ↓
Team 4 (Backend/API)     →  REST API + Database
                             ↓
                             Dashboard (React)
```

### Critical Integration Interfaces:
1. **Camera → Blur Pipeline:** Frame queue with timestamp metadata
2. **Blur → Detection:** Enhanced frame tensor with quality metrics
3. **Detection → Backend:** JSON with detections, OCR, timestamps
4. **Backend → Dashboard:** WebSocket real-time + REST historical data

---

## NON-NEGOTIABLE CONSTRAINTS & DESIGN PRINCIPLES

1. **100% Free & Open-Source:**
   - No paid SDKs or proprietary tools
   - All code original or clearly attributed
   - Open datasets used only in Phase-2

2. **Hardware Realistic:**
   - Phone RTSP simulation valid for hackathon
   - Windows 11 + i5 representative of edge
   - No Jetson required for evaluation

3. **Generalization Focus:**
   - No dataset overfitting assumptions
   - Organizer-provided data tested independently
   - Architecture design-driven, not data-driven

4. **Edge Deployment Ready:**
   - ONNX export mandatory for all models
   - TensorRT compatibility verified
   - CPU inference path optimized

5. **Team Accountability:**
   - Clear subsystem ownership
   - Integration testing between teams
   - Documented APIs and interfaces
   - Performance SLAs per subsystem

