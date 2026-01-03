import React, { useEffect, useState } from 'react';
import { railwayApi, SystemHealth, Analytics, FrameProcessResponse } from '../api/railwayApi';
import { MetricCard } from '../components/MetricCard';
import { Card } from '../components/Card';
import { UploadZone } from '../components/UploadZone';
import { format } from 'date-fns';
import { CameraGrid } from '../components/CameraGrid';

export const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [recentFrames, setRecentFrames] = useState<FrameProcessResponse[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastResult, setLastResult] = useState<FrameProcessResponse | null>(null);
  const [connectionError, setConnectionError] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [healthData, analyticsData, framesData] = await Promise.all([
        railwayApi.getHealth(),
        railwayApi.getAnalytics(24),
        railwayApi.getRecentFrames(5),
      ]);
      setHealth(healthData);
      setAnalytics(analyticsData);
      setRecentFrames(framesData);
      setConnectionError(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setConnectionError(true);
    }
  };

  const handleFileSelect = async (file: File) => {
    setIsProcessing(true);
    try {
      const result = await railwayApi.processFrame(file);
      setLastResult(result);
      fetchData();
    } catch (error) {
      console.error('Error processing frame:', error);
      alert('Error processing image. Make sure backend is running on http://localhost:8000');
    } finally {
      setIsProcessing(false);
    }
  };

  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-4xl">🚂</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Railway Wagon Monitoring System
                </h1>
                <p className="text-sm text-gray-500">
                  AI-Powered Motion Blur Detection & Analysis
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {connectionError ? (
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <span className="text-sm font-medium text-red-700">Backend Offline</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${health?.status === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`}></div>
                  <span className="text-sm font-medium text-gray-700">
                    {health?.status === 'healthy' ? 'System Online' : 'System Degraded'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Frames"
            value={analytics?.total_frames || 0}
            subtitle="All time"
            icon={<span className="text-4xl">📸</span>}
          />
          <MetricCard
            title="Wagons Detected"
            value={analytics?.total_wagons || 0}
            subtitle="Total count"
            icon={<span className="text-4xl">🚃</span>}
          />
          <MetricCard
            title="Processing Speed"
            value={`${analytics?.avg_fps?.toFixed(1) || 0} FPS`}
            subtitle="Average"
            icon={<span className="text-4xl">⚡</span>}
          />
          <MetricCard
            title="Blur Detection"
            value={`${analytics?.blur_detection_rate?.toFixed(1) || 0}%`}
            subtitle="Detection rate"
            icon={<span className="text-4xl">🔍</span>}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <Card title="📤 Upload Frame for Analysis">
              <UploadZone onFileSelect={handleFileSelect} isProcessing={isProcessing} />
            </Card>

            {lastResult && (
              <Card title="📊 Latest Analysis Result">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">Blur Status</p>
                    <p className="text-xl font-bold">
                      {lastResult.is_blurred ? '❌ Blurred' : '✅ Sharp'}
                    </p>
                    <p className="text-sm text-gray-400">Score: {lastResult.blur_score.toFixed(2)}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">Wagons Found</p>
                    <p className="text-xl font-bold">{lastResult.num_wagons}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">Processing Time</p>
                    <p className="text-xl font-bold">{lastResult.processing_time.toFixed(3)}s</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">Frame Rate</p>
                    <p className="text-xl font-bold">{lastResult.fps.toFixed(1)} FPS</p>
                  </div>
                </div>
                {lastResult.wagon_ids.length > 0 && (
                  <div className="mt-4 p-4 bg-purple-50 rounded">
                    <p className="text-sm font-medium text-purple-900 mb-2">Detected Wagon IDs:</p>
                    <div className="flex flex-wrap gap-2">
                      {lastResult.wagon_ids.map((id: string, idx: number) => (
                        <span key={idx} className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm">
                          {id}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            )}
          </div>

          <div className="space-y-6">
            <Card title="🏥 System Health">
              <div className="space-y-3">
                <StatusItem label="Database" status={health?.database || 'unknown'} />
                <StatusItem label="AI Pipeline" status={health?.ai_pipeline || 'unknown'} />
                <StatusItem label="Redis" status={health?.redis || 'unknown'} />
                <div className="pt-3 border-t">
                  <p className="text-sm text-gray-500">Uptime</p>
                  <p className="text-lg font-semibold">
                    {formatUptime(health?.uptime_seconds || 0)}
                  </p>
                </div>
              </div>
            </Card>

            <Card title="🕐 Recent Activity">
              <div className="space-y-2">
                {recentFrames.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-4">No recent activity</p>
                ) : (
                  recentFrames.map((frame) => (
                    <div key={frame.frame_id} className="p-3 bg-gray-50 rounded hover:bg-gray-100 transition">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-sm font-medium">
                            {frame.is_blurred ? '❌ Blurred' : '✅ Sharp'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {frame.num_wagons} wagons • {frame.fps.toFixed(1)} FPS
                          </p>
                        </div>
                        <p className="text-xs text-gray-400">
                          {format(new Date(frame.timestamp), 'HH:mm:ss')}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatusItem: React.FC<{ label: string; status: string }> = ({ label, status }) => {
  const isHealthy = status === 'healthy' || status === 'ready';
  return (
    <div className="flex justify-between items-center">
      <span className="text-sm text-gray-600">{label}</span>
      <span className={`text-sm font-medium ${isHealthy ? 'text-green-600' : 'text-yellow-600'}`}>
        {isHealthy ? '✓ ' : '⚠ '}
        {status}
      </span>
    </div>
  );
};
