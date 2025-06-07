// frontend/src/components/editor/FileMetadata.jsx
import React from 'react';

const FileMetadata = ({ file, algorithms }) => {
  if (!file) {
    return (
      <div className="file-metadata">
        <h4>📊 File Information</h4>
        <p>Select a file to view its metadata</p>
      </div>
    );
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getComplexityColor = (complexity) => {
    switch (complexity?.toLowerCase()) {
      case 'low': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'high': return '#f44336';
      default: return '#757575';
    }
  };

  const getLanguageInfo = (language) => {
    const info = {
      'javascript': { icon: '🟨', name: 'JavaScript' },
      'typescript': { icon: '🔷', name: 'TypeScript' },
      'python': { icon: '🐍', name: 'Python' },
      'java': { icon: '☕', name: 'Java' },
      'cpp': { icon: '⚡', name: 'C++' },
      'html': { icon: '🌐', name: 'HTML' },
      'css': { icon: '🎨', name: 'CSS' }
    };
    return info[language] || { icon: '📄', name: language || 'Unknown' };
  };

  const langInfo = getLanguageInfo(file.language);
  const importance = algorithms?.layout?.getImportanceScore?.(file);

  return (
    <div className="file-metadata">
      <h4>📊 File Metadata:</h4>
      
      <div className="metadata-grid">
        <div className="metadata-item">
          <label>Language:</label>
          <span>
            {langInfo.icon} {langInfo.name}
          </span>
        </div>
        
        <div className="metadata-item">
          <label>Size:</label>
          <span>{file.lines || 0} lines</span>
        </div>
        
        <div className="metadata-item">
          <label>File Size:</label>
          <span>{formatFileSize(file.size || 0)}</span>
        </div>
        
        <div className="metadata-item">
          <label>Modified:</label>
          <span>{formatDate(file.lastModified || Date.now())}</span>
        </div>
        
        {file.complexity && (
          <div className="metadata-item">
            <label>Complexity:</label>
            <span style={{ color: getComplexityColor(file.complexity) }}>
              {file.complexity}
            </span>
          </div>
        )}
        
        {importance && (
          <div className="metadata-item">
            <label>Importance Rank:</label>
            <span>#{importance.rank}</span>
          </div>
        )}
        
        {file.testCoverage !== undefined && (
          <div className="metadata-item">
            <label>Test Coverage:</label>
            <span>{file.testCoverage}%</span>
          </div>
        )}
        
        <div className="metadata-item">
          <label>Dependencies:</label>
          <span>{file.dependencies?.length || 0}</span>
        </div>
        
        <div className="metadata-item">
          <label>Dependents:</label>
          <span>{file.dependents?.length || 0}</span>
        </div>
      </div>
      
      {file.git && (
        <div className="git-info">
          <h5>📝 Git Information:</h5>
          <div className="metadata-item">
            <label>Last Author:</label>
            <span>{file.git.lastAuthor}</span>
          </div>
          <div className="metadata-item">
            <label>Last Commit:</label>
            <span>{file.git.lastCommit?.substring(0, 8)}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileMetadata;