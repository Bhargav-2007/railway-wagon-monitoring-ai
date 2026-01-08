import React from 'react';
import { ChevronLeft, ChevronRight, Play, Pause } from 'lucide-react';
import '../styles/CameraSection.css';

const CameraSection: React.FC<{selectedImage: number; setSelectedImage: (idx: number) => void}> = ({ selectedImage, setSelectedImage }) => {
  const images = ['https://via.placeholder.com/500x400?text=Camera+1', 'https://via.placeholder.com/500x400?text=Camera+2', 'https://via.placeholder.com/500x400?text=Camera+3'];
  return (
    <div className="camera-section">
      <div className="camera-header">
        <h3>Live Camera Feed</h3>
        <div className="camera-controls">
          <button className="control-btn"><Play size={18} /></button>
          <button className="control-btn"><Pause size={18} /></button>
        </div>
      </div>
      <div className="camera-display">
        <img src={images[selectedImage]} alt="Camera feed" className="camera-image" />
        <div className="camera-overlay"><span className="status-badge">Live</span></div>
      </div>
      <div className="camera-thumbnails">
        <button onClick={() => setSelectedImage(Math.max(0, selectedImage - 1))}><ChevronLeft size={18} /></button>
        {images.map((_, idx) => (
          <div key={idx} className={`thumbnail ${selectedImage === idx ? 'active' : ''}`} onClick={() => setSelectedImage(idx)}>
            <img src={images[idx]} alt={`Thumb ${idx}`} />
          </div>
        ))}
        <button onClick={() => setSelectedImage(Math.min(images.length - 1, selectedImage + 1))}><ChevronRight size={18} /></button>
      </div>
      <div className="camera-info">
        <div className="info-item"><span className="label">Quality:</span><span className="value">1080p</span></div>
        <div className="info-item"><span className="label">FPS:</span><span className="value">30</span></div>
        <div className="info-item"><span className="label">Status:</span><span className="value healthy">Healthy</span></div>
      </div>
    </div>
  );
};
export default CameraSection;
