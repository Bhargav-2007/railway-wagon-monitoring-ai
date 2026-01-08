import React from 'react';
import '../styles/BlurDetectionTable.css';

const BlurDetectionTable: React.FC = () => {
  const data = [
    { wagon: 'WG-2847-001', timestamp: '2026-01-09 00:15:23', severity: 'High', score: 92, status: 'Flagged' },
    { wagon: 'WG-2846-045', timestamp: '2026-01-09 00:12:45', severity: 'Medium', score: 67, status: 'Reviewed' },
    { wagon: 'WG-2845-128', timestamp: '2026-01-09 00:10:12', severity: 'Low', score: 34, status: 'Cleared' },
  ];
  
  return (
    <div className="blur-table-container">
      <div className="table-header">
        <h3>Recent Blur Detection</h3>
        <a href="#" className="view-all">View All →</a>
      </div>
      <div className="table-wrapper">
        <table className="blur-table">
          <thead>
            <tr>
              <th>Wagon ID</th>
              <th>Timestamp</th>
              <th>Severity</th>
              <th>Score</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map((record, idx) => (
              <tr key={idx}>
                <td className="wagon-id">{record.wagon}</td>
                <td className="timestamp">{record.timestamp}</td>
                <td><span className={`severity-badge ${record.severity.toLowerCase()}`}>{record.severity}</span></td>
                <td><div className="score-bar"><div className="score-fill" style={{width: `${record.score}%`}}></div><span className="score-value">{record.score}%</span></div></td>
                <td><span className="status-badge">{record.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
export default BlurDetectionTable;
