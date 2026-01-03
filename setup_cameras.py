import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def setup_cameras():
    """Setup all cameras from config file"""
    
    # Load camera config
    with open('camera_config.json', 'r') as f:
        config = json.load(f)
    
    print("🎥 Setting up IP cameras...")
    print("=" * 60)
    
    for camera in config['cameras']:
        print(f"\n📱 Adding {camera['camera_id']}...")
        print(f"   IP: {camera['ip_address']}:{camera['port']}")
        print(f"   Position: {camera['position']}")
        
        # Add camera
        response = requests.post(
            f"{API_BASE}/stream/cameras/add",
            json=camera
        )
        
        if response.status_code == 200:
            print(f"   ✅ Added successfully")
            
            # Start camera stream
            start_response = requests.post(
                f"{API_BASE}/stream/cameras/{camera['camera_id']}/start"
            )
            
            if start_response.status_code == 200:
                print(f"   ✅ Stream started")
            else:
                print(f"   ⚠️  Failed to start stream: {start_response.text}")
        else:
            print(f"   ❌ Failed to add camera: {response.text}")
    
    print("\n" + "=" * 60)
    print("✅ Camera setup complete!")
    print("\nView cameras at:")
    print("  http://localhost:3000  (Dashboard)")
    print("\nTest endpoints:")
    for camera in config['cameras']:
        cam_id = camera['camera_id']
        print(f"  http://localhost:8000/api/v1/stream/cameras/{cam_id}/snapshot")

if __name__ == "__main__":
    setup_cameras()
