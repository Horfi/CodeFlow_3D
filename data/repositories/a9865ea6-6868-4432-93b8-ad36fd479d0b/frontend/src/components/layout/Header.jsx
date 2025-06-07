// frontend/src/components/layout/Header.jsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Button from '../shared/Button';

const Header = ({ onVersionSwitch, currentVersion }) => {
  const location = useLocation();
  const isProjectView = location.pathname.startsWith('/project/');

  return (
    <header className="app-header">
      <div className="header-left">
        <Link to="/" className="logo">
          🎯 CodeFlow 3D
        </Link>
        {isProjectView && (
          <span className="project-name">
            📁 {new URLSearchParams(location.search).get('name') || 'my-awesome-project'}
          </span>
        )}
      </div>

      <nav className="header-nav">
        <Link to="/">🏠 Home</Link>
        <Button onClick={() => console.log('Settings')}>⚙️ Settings</Button>
        <Button onClick={() => console.log('Help')}>❓ Help</Button>
        
        {isProjectView && onVersionSwitch && (
          <div className="version-switch">
            <label>
              Mode:
              <select 
                value={currentVersion} 
                onChange={(e) => onVersionSwitch(e.target.value)}
              >
                <option value="personalized">Personalized</option>
                <option value="random">Random</option>
              </select>
            </label>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;