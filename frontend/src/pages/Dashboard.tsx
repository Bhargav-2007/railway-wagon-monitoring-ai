import React, { useState } from 'react';
import { MetricCard } from '../components/MetricCard';
import CameraSection from '../components/CameraSection';
import BlurDetectionTable from '../components/BlurDetectionTable';
import AlertBanner from '../components/AlertBanner';
import ChartSection from '../components/ChartSection';
import '../styles/Dashboard.css';

const Dashboard: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState(0);

  const stats = [
    { label: 'Total Wagons', value: '2,847',  title: 'Total Wagons',change: '+12.5%', icon: '🚂' },
    { label: 'Blur Detected', value: '34', title: 'Blur Detected', change: '-5.2%', icon: '⚠️' },
    { label: 'Avg Score', value: '94.2%', title: 'Avg Score', change: '+2.1%', icon: '✓' },
    { label: 'Active Routes', value: '156', title: 'Active Routes', change: '+8.3%', icon: '🚆' },  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Railway Wagon Monitoring Dashboard</h1>
        <p className="subtitle">Real-time motion blur detection and analysis</p>
      </div>

      <section className="stats-section">
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <MetricCard key={index} {...stat} />
          ))}
        </div>
      </section>

      <AlertBanner />

      <div className="content-grid">
        <CameraSection selectedImage={selectedImage} setSelectedImage={setSelectedImage} />
        <BlurDetectionTable />
      </div>

      <ChartSection />
    </div>
  );
};

export default Dashboard;