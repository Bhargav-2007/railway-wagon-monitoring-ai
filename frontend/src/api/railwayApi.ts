import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || `https://${window.location.hostname.replace('-3000', '-8000')}/api/v1`;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface FrameProcessResponse {
  frame_id: number;
  camera_id: string;
  is_blurred: boolean;
  blur_score: number;
  was_deblurred: boolean;
  was_enhanced: boolean;
  num_wagons: number;
  wagon_ids: string[];
  processing_time: number;
  fps: number;
  timestamp: string;
}

export interface SystemHealth {
  status: string;
  database: string;
  redis: string;
  ai_pipeline: string;
  cameras_active: number;
  uptime_seconds: number;
}

export interface Analytics {
  total_frames: number;
  total_wagons: number;
  avg_processing_time: number;
  avg_fps: number;
  blur_detection_rate: number;
  ocr_success_rate: number;
  time_period: string;
}

export const railwayApi = {
  getHealth: async (): Promise<SystemHealth> => {
    const response = await api.get('/health/');
    return response.data;
  },

  processFrame: async (file: File, cameraId: string = 'dashboard'): Promise<FrameProcessResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/frames/process?camera_id=${cameraId}&skip_heavy=true`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getRecentFrames: async (limit: number = 10): Promise<FrameProcessResponse[]> => {
    const response = await api.get(`/frames/recent?limit=${limit}`);
    return response.data;
  },

  getAnalytics: async (hours: number = 24): Promise<Analytics> => {
    const response = await api.get(`/analytics/summary?hours=${hours}`);
    return response.data;
  },
};

export default api;
