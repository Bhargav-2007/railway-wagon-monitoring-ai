import React, { useState, useEffect } from 'react';
import { Card } from './Card';

interface Camera {
  camera_id: string;
  ip: string;
  port: number;
  status: string;
  last_update: string | null;
}

interface CameraStats {
  blur_detected: boolean;
  blur_score: number;
  num_wagons: number;
  wagon_ids: string[];
  processing_time: number;
  fps: number;
}

export const CameraGrid: React.FC = () => {
  const [cameras, setCameras] = useState<Record<string, Camera>>({});
  const [selectedCamera, setSelectedCamera] = useState<string | null>(null);
  const [stats, setStats] = useState<Record<string, CameraStats>>({});

  useEffect(() => {
    fetchCameras();
    const interval = setInterval(fetchCameras, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (Object.keys(cameras).length > 0) {
      fetchStats();
      const interval = setInterval(fetchStats, 2000);
      return () => clearInterval(interval);
    }
  }, [cameras]);

  const fetchCameras = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/stream/cameras');
      const data = await response.json();
      setCameras(data.cameras || {});
      
      if (!selectedCamera && Object.keys(data.cameras).length > 0) {
        setSelectedCamera(Object.keys(data.cameras)[0]);
      }
    } catch (error) {
      console.error('Error fetching cameras:', error);
    }
  };

  const fetchStats = async () => {
    const newStats: Record<string, CameraStats> = {};
    
    for (const camId of Object.keys(cameras)) {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/stream/cameras/${camId}/stats`);
        const data = await response.json();
        newStats[camId] = data;
      } catch (error) {
        console.error(`Error fetching stats for ${camId}:`, error);
      }
    }
    
    setStats(newStats);
  };

  const cameraList = Object.entries(cameras);

  if (cameraList.length === 0) {
    return (
      <Card title="📹 Live Camera Feeds">
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No cameras configured</p>
          <p className="text-sm text-gray-400">
            Run <code className="bg-gray-100 px-2 py-1 rounded">python setup_cameras.py</code> to setup cameras
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card title="📹 Live Camera Feeds">
        {/* Camera selector */}
        <div className="flex gap-2 mb-4">
          {cameraList.map(([camId, cam]) => (
            <button
              key={camId}
              onClick={() => setSelectedCamera(camId)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedCamera === camId
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {cam.status === 'active' ? '🟢' : '🔴'} {camId.replace(/_/g, ' ')}
            </button>
          ))}
        </div>

        {/* Live stream */}
        {selectedCamera && (
          <div className="space-y-4">
            <div className="relative bg-black rounded-lg overflow-hidden">
              <img
                src={`http://localhost:8000/api/v1/stream/cameras/${selectedCamera}/stream`}
                alt={`Camera ${selectedCamera}`}
                className="w-full h-auto"
                style={{ maxHeight: '500px', objectFit: 'contain' }}
              />
              
              {/* Overlay stats */}
              {stats[selectedCamera] && (
                <div className="absolute top-4 right-4 bg-black bg-opacity-75 text-white p-3 rounded-lg text-sm space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${stats[selectedCamera].blur_detected ? 'bg-red-500' : 'bg-green-500'}`}></span>
                    <span>{stats[selectedCamera].blur_detected ? 'Blurred' : 'Sharp'}</span>
                  </div>
                  <div>Wagons: {stats[selectedCamera].num_wagons}</div>
                  <div>FPS: {stats[selectedCamera].fps.toFixed(1)}</div>
                  <div>Time: {(stats[selectedCamera].processing_time * 1000).toFixed(0)}ms</div>
                </div>
              )}
            </div>

            {/* Camera info */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-xs text-gray-500">Camera ID</p>
                <p className="font-medium">{selectedCamera}</p>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-xs text-gray-500">Status</p>
                <p className="font-medium text-green-600">
                  {cameras[selectedCamera].status}
                </p>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-xs text-gray-500">IP Address</p>
                <p className="font-medium">{cameras[selectedCamera].ip}:{cameras[selectedCamera].port}</p>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* All cameras grid */}
      <Card title="🎥 All Cameras">
        <div className="grid grid-cols-3 gap-4">
          {cameraList.map(([camId, cam]) => (
            <div key={camId} className="space-y-2">
              <div className="relative bg-gray-900 rounded overflow-hidden" style={{ aspectRatio: '16/9' }}>
                <img
                  src={`http://localhost:8000/api/v1/stream/cameras/${camId}/snapshot?t=${Date.now()}`}
                  alt={camId}
                  className="w-full h-full object-cover"
                  onClick={() => setSelectedCamera(camId)}
                  style={{ cursor: 'pointer' }}
                />
              </div>
              <div className="text-sm">
                <p className="font-medium">{camId.replace(/_/g, ' ')}</p>
                <p className="text-xs text-gray-500">
                  {stats[camId] ? `${stats[camId].num_wagons} wagons • ${stats[camId].fps.toFixed(1)} FPS` : 'Loading...'}
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
