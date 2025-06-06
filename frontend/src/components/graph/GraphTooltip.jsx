// frontend/src/components/graph/GraphTooltip.jsx
import React from 'react';

const GraphTooltip = ({ data, version, algorithms }) => {
  if (!data?.node) return null;

  const { node } = data;
  const importance = algorithms?.layout?.getImportanceScore?.(node) || {};

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString();
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    return `${mins}m ${seconds % 60}s`;
  };

  const formatTemperature = (temp) => {
    const percentage = Math.round(temp * 100);
    const heat = temp > 0.7 ? '🔥' : temp > 0.4 ? '🌡️' : '❄️';
    return `${heat} ${percentage}%`;
  };

  const getFileIcon = (filePath) => {
    const ext = filePath.split('.').pop()?.toLowerCase();
    const icons = {
      'js': '🟨', 'jsx': '⚛️', 'ts': '🔷', 'tsx': '⚛️',
      'py': '🐍', 'java': '☕', 'cpp': '⚡', 'c': '⚡',
      'html': '🌐', 'css': '🎨', 'scss': '🎨'
    };
    return icons[ext] || '📄';
  };

  return (
    <div className="graph-tooltip">
      <div className="tooltip-header">
        <span className="file-icon">{getFileIcon(node.path)}</span>
        <span className="file-name">{node.name}</span>
      </div>
      
      <div className="tooltip-path">{node.path}</div>
      
      <div className="tooltip-stats">
        <div>📏 Size: {node.size || 0} lines</div>
        <div>🔤 Language: {node.language || 'Unknown'}</div>
        <div>⭐ Importance Rank: #{importance.rank || 'N/A'}</div>
        <div>🔗 Dependencies: {node.dependencies?.length || 0}</div>
        <div>📅 Last Modified: {formatDate(node.lastModified || Date.now())}</div>
      </div>
      
      {version === 'personalized' && node.userStats && (
        <div className="tooltip-personalization">
          <h5>📊 Your Interaction Data:</h5>
          <div>👆 Clicks: {node.userStats.clickCount || 0}</div>
          <div>⏱️ Time Spent: {formatTime(node.userStats.timeSpent || 0)}</div>
          <div>🌡️ Temperature: {formatTemperature(node.userStats.temperature || 0.5)}</div>
          <div>📈 Usage Score: {Math.round((node.userStats.usageScore || 0) * 100)}%</div>
        </div>
      )}
      
      {node.metrics && (
        <div className="tooltip-metrics">
          <h5>📈 Code Metrics:</h5>
          <div>🔄 Complexity: {node.metrics.complexity || 'Low'}</div>
          <div>🎯 Test Coverage: {node.metrics.testCoverage || 0}%</div>
          <div>🐛 Issues: {node.metrics.issues || 0}</div>
        </div>
      )}
    </div>
  );
};

export default GraphTooltip;