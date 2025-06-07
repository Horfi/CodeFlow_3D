// frontend/src/components/graph/GraphControls.jsx
import React from 'react';
import Button from '../shared/Button';

const GraphControls = ({ 
  onResetLayout, 
  onResetColors, 
  onTogglePhysics,
  settings,
  onSettingsChange 
}) => {
  const handleSettingChange = (key, value) => {
    onSettingsChange(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="graph-controls">
      <div className="control-group">
        <h4>🎛️ Graph Controls</h4>
        
        <div className="control-buttons">
          <Button onClick={onResetLayout} size="small">
            📐 Reset Layout
          </Button>
          <Button onClick={onResetColors} size="small">
            🎨 Reset Colors
          </Button>
          <Button onClick={onTogglePhysics} size="small">
            {settings.enablePhysics ? '⏸️' : '▶️'} Physics
          </Button>
        </div>
      </div>

      <div className="control-group">
        <h4>⚙️ Settings</h4>
        
        <div className="control-sliders">
          <label>
            Link Distance: {settings.linkDistance}
            <input
              type="range"
              min="50"
              max="200"
              value={settings.linkDistance}
              onChange={(e) => handleSettingChange('linkDistance', Number(e.target.value))}
            />
          </label>
          
          <label>
            Node Size: {settings.nodeSize}
            <input
              type="range"
              min="4"
              max="20"
              value={settings.nodeSize}
              onChange={(e) => handleSettingChange('nodeSize', Number(e.target.value))}
            />
          </label>
          
          <label>
            <input
              type="checkbox"
              checked={settings.showLabels}
              onChange={(e) => handleSettingChange('showLabels', e.target.checked)}
            />
            Show Labels
          </label>
        </div>
      </div>
    </div>
  );
};

export default GraphControls;