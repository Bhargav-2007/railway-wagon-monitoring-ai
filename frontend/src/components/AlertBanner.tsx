import React from 'react';
import { AlertTriangle, X } from 'lucide-react';
import '../styles/AlertBanner.css';

const AlertBanner: React.FC = () => {
  const [visible, setVisible] = React.useState(true);
  if (!visible) return null;

  return (
    <div className="alert-banner alert-warning">
      <div className="alert-content">
        <AlertTriangle size={20} />
        <p>3 wagons with high blur detection - Review recommended</p>
      </div>
      <button className="alert-close" onClick={() => setVisible(false)}><X size={18} /></button>
    </div>
  );
};
export default AlertBanner;
