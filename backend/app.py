from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Model status data matching Roboflow dashboard
MODEL_DATA = {
    "modelName": "Wagons defect",
    "version": "1",
    "modelType": "RF-DETR (Medium)",
    "timestamp": "2026-01-08 11:39pm",
    "createdBy": "Bhargav Umetiya",
    "datasetSize": 113,
    "metrics": {
        "mAP50": 85.6,
        "precision": 88.1,
        "recall": 69.0
    },
    "modelUrl": "wagons-defect-9foh2/1",
    "checkpoint": "-",
    "updatedOn": "1/9/26, 12:08 AM",
    "status": "completed"
}

@app.route('/api/model-status', methods=['GET'])
def get_model_status():
    """Get current model training status and metrics"""
    return jsonify(MODEL_DATA)

@app.route('/api/model-metrics', methods=['GET'])
def get_model_metrics():
    """Get detailed model metrics"""
    return jsonify({
        "mAP50": 85.6,
        "precision": 88.1,
        "recall": 69.0,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Railway Wagon Monitoring AI Backend is running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get complete model information"""
    return jsonify({
        "model": MODEL_DATA,
        "deployment_ready": True,
        "recommended_action": "Ready for Export & Deployment"
    })

if __name__ == '__main__':
    print("🚀 Railway Wagon Monitoring AI Backend")
    print("📊 Starting Flask API server...")
    print("🔗 Model Status: " + MODEL_DATA['status'])
    print("📈 Metrics: mAP50={}, Precision={}, Recall={}".format(
        MODEL_DATA['metrics']['mAP50'],
        MODEL_DATA['metrics']['precision'],
        MODEL_DATA['metrics']['recall']
    ))
    print("\n✅ Server running at http://0.0.0.0:5000")
    print("📍 Health Check: http://localhost:5000/api/health\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
