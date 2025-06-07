
// frontend/src/components/layout/HomePage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../shared/Button';
import LoadingSpinner from '../shared/LoadingSpinner';

const HomePage = () => {
  const [gitUrl, setGitUrl] = useState('');
  const [version, setVersion] = useState('personalized');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!gitUrl.trim()) return;
    
    setLoading(true);
    setProgress(0);
    setStatus('Cloning repository...');
    
    try {
      const response = await fetch('/api/repository/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gitUrl, version })
      });
      
      if (response.ok) {
        const { projectId } = await response.json();
        navigate(`/project/${projectId}?version=${version}`);
      }
    } catch (error) {
      console.error('Analysis failed:', error);
    }
    
    setLoading(false);
  };

  return (
    <div className="home-page">
      <header className="home-header">
        <h1>🌟 CodeFlow 3D 🌟</h1>
        <p>AI-Augmented Code Dependency Explorer</p>
      </header>

      <div className="import-section">
        <h2>📂 Import Repository</h2>
        
        <div className="url-input">
          <label>Git Repository URL:</label>
          <input
            type="url"
            value={gitUrl}
            onChange={(e) => setGitUrl(e.target.value)}
            placeholder="https://github.com/username/repo.git"
            disabled={loading}
          />
          <Button onClick={() => document.getElementById('file-input').click()}>
            Browse
          </Button>
          <input
            id="file-input"
            type="file"
            style={{ display: 'none' }}
            webkitdirectory=""
            onChange={(e) => console.log('Local folder selected')}
          />
        </div>

        <div className="advanced-options">
          <details>
            <summary>Advanced Options</summary>
            <div className="options-grid">
              <label><input type="checkbox" /> Include test files</label>
              <label><input type="checkbox" /> Parse documentation</label>
              <label><input type="checkbox" /> Deep analysis mode</label>
              <label><input type="checkbox" /> Track external dependencies</label>
              <label><input type="checkbox" /> Enable real-time sync</label>
              <label><input type="checkbox" /> Cache for offline use</label>
            </div>
          </details>
        </div>

        <div className="version-selector">
          <label>Version Mode:</label>
          <label>
            <input
              type="radio"
              value="personalized"
              checked={version === 'personalized'}
              onChange={(e) => setVersion(e.target.value)}
            />
            Personalized
          </label>
          <label>
            <input
              type="radio"
              value="random"
              checked={version === 'random'}
              onChange={(e) => setVersion(e.target.value)}
            />
            Random (Research Mode)
          </label>
        </div>

        <Button 
          onClick={handleAnalyze} 
          disabled={loading || !gitUrl.trim()}
          className="analyze-btn"
        >
          🚀 Analyze Repository
        </Button>

        {loading && (
          <div className="progress-section">
            <p>Processing Status: ⏳ {status} ({progress}%)</p>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress}%` }}
              />
            </div>
            <LoadingSpinner />
          </div>
        )}
      </div>

      <div className="recent-projects">
        <h3>📁 Recent Projects:</h3>
        <div className="project-list">
          <div className="project-item">
            • react-dashboard (⭐ 245 files, analyzed 2 hours ago)
          </div>
          <div className="project-item">
            • python-ml-toolkit (⭐ 156 files, analyzed yesterday)
          </div>
          <div className="project-item">
            • node-api-server (⭐ 89 files, analyzed 3 days ago)
          </div>
        </div>
      </div>

      <div className="stats-section">
        <p>📊 Quick Stats: 1,247 files analyzed | 15 sessions | 42 hours saved</p>
      </div>
    </div>
  );
};

export default HomePage;