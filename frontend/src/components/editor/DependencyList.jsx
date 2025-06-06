// frontend/src/components/editor/DependencyList.jsx
import React from 'react';

const DependencyList = ({ dependencies, selectedFile, onDependencyClick }) => {
  if (!selectedFile) {
    return (
      <div className="dependency-list">
        <h4>🔗 Dependencies</h4>
        <p>Select a file to view its dependencies</p>
      </div>
    );
  }

  const getImportType = (dep) => {
    if (dep.type === 'external') return '📦';
    if (dep.type === 'internal') return '📁';
    if (dep.type === 'relative') return '🔗';
    return '❓';
  };

  const getDependencyColor = (dep) => {
    switch (dep.type) {
      case 'external': return '#ff9800';
      case 'internal': return '#4caf50';
      case 'relative': return '#2196f3';
      default: return '#757575';
    }
  };

  return (
    <div className="dependency-list">
      <h4>🔗 Dependencies Found:</h4>
      
      {dependencies.length === 0 ? (
        <p>No dependencies detected</p>
      ) : (
        <div className="dependency-items">
          {dependencies.map((dep, index) => (
            <div
              key={index}
              className="dependency-item"
              onClick={() => onDependencyClick(dep)}
              style={{ borderLeftColor: getDependencyColor(dep) }}
            >
              <div className="dependency-header">
                <span className="dependency-icon">{getImportType(dep)}</span>
                <span className="dependency-name">{dep.name}</span>
              </div>
              <div className="dependency-path">{dep.path}</div>
              {dep.line && (
                <div className="dependency-line">Line {dep.line}</div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="dependency-legend">
        <h5>Legend:</h5>
        <div className="legend-item">
          <span>📦</span> External packages
        </div>
        <div className="legend-item">
          <span>📁</span> Internal modules
        </div>
        <div className="legend-item">
          <span>🔗</span> Relative imports
        </div>
      </div>
    </div>
  );
};

export default DependencyList;