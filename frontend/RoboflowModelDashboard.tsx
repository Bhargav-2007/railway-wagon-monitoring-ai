import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface ModelMetrics {
  mAP50: number;
  precision: number;
  recall: number;
}

interface ModelData {
  modelName: string;
  version: string;
  modelType: string;
  timestamp: string;
  createdBy: string;
  datasetSize: number;
  metrics: ModelMetrics;
  modelUrl: string;
  checkpoint: string;
  updatedOn: string;
  status: 'completed' | 'training';
}

interface RoboflowModelDashboardProps {
  data?: ModelData;
  apiEndpoint?: string;
}

const RoboflowModelDashboard: React.FC<RoboflowModelDashboardProps> = ({
  data,
  apiEndpoint = '/api/model-status',
}) => {
  const [modelData, setModelData] = useState<ModelData | null>(data || null);
  const [loading, setLoading] = useState(!data);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchModelData = async () => {
      if (data) {
        setModelData(data);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await axios.get(apiEndpoint);
        setModelData(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch model data:', err);
        setError('Failed to load model data');
      } finally {
        setLoading(false);
      }
    };

    fetchModelData();
  }, [data, apiEndpoint]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading model data...</p>
        </div>
      </div>
    );
  }

  if (error || !modelData) {
    return (
      <div className="min-h-screen bg-white p-8">
        <div className="max-w-4xl mx-auto">
          <p className="text-red-600 text-lg">{error || 'No model data available'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Versions</h1>
          <p className="text-gray-600">Manage your model versions</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Version Card */}
          <div className="lg:col-span-1">
            <div className="border-2 border-purple-500 rounded-lg p-6 bg-gradient-to-br from-purple-50 to-white">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Versions</h3>
              
              <div className="bg-gray-900 text-white rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-400 mb-2">Version</p>
                <p className="text-xl font-bold text-purple-400 mb-4">{modelData.timestamp}</p>
                <div className="flex gap-2 flex-wrap">
                  <span className="bg-purple-600 text-white text-xs font-bold px-3 py-1 rounded">
                    v{modelData.version}
                  </span>
                  <span className="bg-gray-700 text-gray-300 text-xs font-bold px-3 py-1 rounded flex items-center gap-1">
                    📊 {modelData.datasetSize}
                  </span>
                  <span className="bg-purple-900 text-purple-200 text-xs font-bold px-3 py-1 rounded flex items-center gap-1">
                    ⚙️ {modelData.modelType}
                  </span>
                </div>
                <div className="mt-3 pt-3 border-t border-gray-700">
                  <p className="text-xs text-gray-400 mb-1">Created by</p>
                  <p className="text-sm text-blue-400 flex items-center gap-1">
                    👤 {modelData.createdBy}
                  </p>
                </div>
              </div>

              <button className="w-full py-2 px-4 bg-gray-200 text-gray-900 rounded font-medium hover:bg-gray-300 transition">
                Edit
              </button>
            </div>
          </div>

          {/* Right Column - Model Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Model Status */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  {modelData.modelName}
                </h2>
                <button className="px-4 py-2 border-2 border-gray-900 text-gray-900 rounded font-medium hover:bg-gray-50 transition">
                  View Model →
                </button>
              </div>
            </div>

            {/* Model Info Grid */}
            <div className="grid grid-cols-2 gap-4 bg-gray-50 p-6 rounded-lg">
              <div>
                <p className="text-sm text-gray-600 mb-1">Model URL:</p>
                <p className="text-gray-900 font-mono text-sm">{modelData.modelUrl}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Checkpoint:</p>
                <p className="text-gray-900">{modelData.checkpoint}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Updated On:</p>
                <p className="text-gray-900">{modelData.updatedOn}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Model Type:</p>
                <p className="text-gray-900">{modelData.modelType}</p>
              </div>
            </div>

            {/* Metrics Section */}
            <div className="border-2 border-gray-300 rounded-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                Metrics
                <span className="text-blue-600 cursor-help">ℹ️</span>
              </h3>

              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-2">mAP@50</p>
                  <div className="flex items-center justify-center mb-2">
                    <div className="w-16 h-24 bg-gradient-to-t from-blue-500 to-blue-200 rounded relative">
                      <span className="absolute bottom-1 left-1/2 transform -translate-x-1/2 text-white font-bold text-sm">
                        {modelData.metrics.mAP50.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-2">Precision</p>
                  <div className="flex items-center justify-center mb-2">
                    <div className="w-16 h-24 bg-gradient-to-t from-purple-500 to-purple-200 rounded relative">
                      <span className="absolute bottom-1 left-1/2 transform -translate-x-1/2 text-white font-bold text-sm">
                        {modelData.metrics.precision.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-2">Recall</p>
                  <div className="flex items-center justify-center mb-2">
                    <div className="w-16 h-24 bg-gradient-to-t from-orange-500 to-orange-200 rounded relative">
                      <span className="absolute bottom-1 left-1/2 transform -translate-x-1/2 text-white font-bold text-sm">
                        {modelData.metrics.recall.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button className="flex-1 py-3 px-4 bg-gray-100 text-gray-900 rounded font-medium hover:bg-gray-200 transition">
                📥 Download Dataset
              </button>
              <button className="flex-1 py-3 px-4 bg-gray-100 text-gray-900 rounded font-medium hover:bg-gray-200 transition">
                ⋯ Edit
              </button>
            </div>
          </div>
        </div>

        {/* Model Evaluation Section */}
        <div className="mt-8 border-l-4 border-orange-500 bg-orange-50 p-6 rounded">
          <h3 className="text-xl font-bold text-orange-700 mb-2">🔍 Model Evaluation</h3>
          <p className="text-orange-600">Additional model evaluation tools and options available in deployment section</p>
        </div>
      </div>
    </div>
  );
};

export default RoboflowModelDashboard;
