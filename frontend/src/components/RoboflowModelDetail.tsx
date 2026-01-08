import React, { useState } from 'react';
import { ChevronLeft, Download, Zap } from 'lucide-react';

const RoboflowModelDetail: React.FC = () => {
  const [confidenceThreshold, setConfidenceThreshold] = useState(50);
  const [overlapThreshold, setOverlapThreshold] = useState(50);
  const [opacityThreshold, setOpacityThreshold] = useState(75);

  const testSamples = [
    '/api/placeholder?w=150&h=100',
    '/api/placeholder?w=150&h=100',
    '/api/placeholder?w=150&h=100',
    '/api/placeholder?w=150&h=100',
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-56 bg-gradient-to-b from-purple-900 to-purple-800 text-white p-6 overflow-y-auto">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded bg-white/20"></div>
          <span className="text-xs font-bold uppercase tracking-wider">FREEDOM SHIELD</span>
        </div>

        <div className="mb-6">
          <button className="flex items-center gap-2 text-sm hover:bg-white/10 rounded px-3 py-2 w-full transition">
            <ChevronLeft size={16} />
            Back
          </button>
        </div>

        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-16 h-12 rounded bg-gradient-to-br from-blue-400 to-purple-500"></div>
            <div>
              <h3 className="font-bold text-sm">Wagons defect</h3>
              <p className="text-xs text-purple-200">Object Detection</p>
            </div>
          </div>
          <button className="text-xs font-semibold bg-white/20 hover:bg-white/30 rounded px-3 py-2 w-full transition">Edit</button>
        </div>

        <nav className="space-y-1 text-sm">
          <button className="block w-full text-left px-3 py-2 hover:bg-white/10 rounded font-semibold">📊 Analytics</button>
          <button className="block w-full text-left px-3 py-2 hover:bg-white/10 rounded">🏷️ Classes & Tags</button>
          <div className="px-3 py-2 font-semibold mt-4 mb-2 uppercase text-xs text-purple-200">MODELS</div>
          <button className="block w-full text-left px-3 py-2 bg-white/20 rounded font-semibold">📈 Models</button>
          <button className="block w-full text-left px-3 py-2 hover:bg-white/10 rounded">🔍 Visualize</button>
          <div className="px-3 py-2 font-semibold mt-4 mb-2 uppercase text-xs text-purple-200">DEPLOY</div>
          <button className="block w-full text-left px-3 py-2 hover:bg-white/10 rounded">🚀 Deployments</button>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <ChevronLeft size={20} className="text-gray-600 cursor-pointer" />
              <h1 className="text-2xl font-bold text-gray-900">Wagons defect 1</h1>
            </div>
            <div className="flex items-center gap-3">
              <button className="px-4 py-2 border-2 border-gray-300 rounded text-gray-700 hover:bg-gray-50 font-semibold text-sm flex items-center gap-2">
                <Zap size={16} /> Visualize
              </button>
              <button className="px-4 py-2 border-2 border-gray-300 rounded text-gray-700 hover:bg-gray-50 font-semibold text-sm flex items-center gap-2">
                <Download size={16} /> Download Weights
              </button>
              <button className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 font-semibold text-sm flex items-center gap-2">
                <Zap size={16} /> Deploy Model
              </button>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-8 py-8">
          {/* Model Info Grid */}
          <div className="grid grid-cols-4 gap-4 mb-8 bg-white p-6 rounded-lg border border-gray-200">
            <div>
              <p className="text-xs text-gray-600 font-semibold mb-1">MODEL URL</p>
              <p className="text-sm text-gray-900 font-mono">wagons-defect-9foh2/1</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-semibold mb-1">CHECKPOINT</p>
              <p className="text-sm text-gray-900">-</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-semibold mb-1">DATASET VERSION</p>
              <p className="text-sm text-gray-900">2026-01-08 11:39pm</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-semibold mb-1">UPDATED ON</p>
              <p className="text-sm text-gray-900">1/9/26, 12:08 AM</p>
            </div>
          </div>

          {/* Metrics */}
          <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
            <div className="flex items-center gap-2 mb-4">
              <h2 className="text-lg font-bold text-gray-900">Metrics</h2>
              <span className="text-gray-400 cursor-help">ℹ️</span>
            </div>
            <div className="grid grid-cols-3 gap-6">
              {[
                { label: 'mAP@50', value: '85.6%' },
                { label: 'Precision', value: '88.1%' },
                { label: 'Recall', value: '69.0%' },
              ].map((m) => (
                <div key={m.label} className="text-center">
                  <p className="text-sm text-gray-600 mb-2">{m.label}</p>
                  <div className="w-full flex justify-center">
                    <div className="w-16 h-24 bg-gradient-to-t from-blue-500 to-blue-200 rounded flex items-center justify-center">
                      <span className="text-white font-bold text-sm">{m.value}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Preview Model */}
          <div className="grid grid-cols-3 gap-8">
            <div className="col-span-2 bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Preview Model</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">Samples from Test Set</h4>
                  <div className="grid grid-cols-4 gap-3">
                    {testSamples.map((_, i) => (
                      <div key={i} className="aspect-video bg-gray-300 rounded flex items-center justify-center">
                        <span className="text-gray-500 text-xs">Sample {i + 1}</span>
                      </div>
                    ))}
                  </div>
                  <button className="text-purple-600 font-semibold text-sm mt-3 hover:underline">View Test Set →</button>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">Upload Image or Video File</h4>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 hover:bg-gray-50 cursor-pointer transition">
                    <p className="text-sm text-gray-600">Drop file here or click to upload</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Controls */}
            <div className="bg-white p-6 rounded-lg border border-gray-200 h-fit">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-semibold text-gray-700 block mb-2">
                    Confidence Threshold: <span className="text-purple-600">{confidenceThreshold}%</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={confidenceThreshold}
                    onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                    className="w-full accent-purple-600"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0%</span>
                    <span>100%</span>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-semibold text-gray-700 block mb-2">
                    Overlap Threshold: <span className="text-purple-600">{overlapThreshold}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={overlapThreshold}
                    onChange={(e) => setOverlapThreshold(Number(e.target.value))}
                    className="w-full accent-purple-600"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0%</span>
                    <span>100%</span>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-semibold text-gray-700 block mb-2">
                    Opacity Threshold: <span className="text-purple-600">{opacityThreshold}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={opacityThreshold}
                    onChange={(e) => setOpacityThreshold(Number(e.target.value))}
                    className="w-full accent-purple-600"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0%</span>
                    <span>100%</span>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-semibold text-gray-700 block mb-2">Label Display Mode</label>
                  <select className="w-full border border-gray-300 rounded px-3 py-2 text-sm text-gray-700 bg-white hover:border-gray-400">
                    <option>Draw Confidence</option>
                    <option>Draw Label Only</option>
                    <option>Draw Bounding Box Only</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoboflowModelDetail;
