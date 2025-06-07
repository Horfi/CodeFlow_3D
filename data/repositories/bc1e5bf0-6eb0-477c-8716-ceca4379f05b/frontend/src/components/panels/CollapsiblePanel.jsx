// frontend/src/components/panels/CollapsiblePanel.jsx
import React, { useState } from 'react';

const CollapsiblePanel = ({ 
  title, 
  icon, 
  defaultCollapsed = false, 
  children,
  className = '',
  onToggle
}) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  const handleToggle = () => {
    setIsCollapsed(!isCollapsed);
    if (onToggle) onToggle(!isCollapsed);
  };

  return (
    <div className={`collapsible-panel ${isCollapsed ? 'collapsed' : 'expanded'} ${className}`}>
      <div 
        className="panel-header"
        onClick={handleToggle}
      >
        <span className="panel-icon">{icon}</span>
        <span className="panel-title">{title}</span>
        <span className="collapse-indicator">
          {isCollapsed ? '[+]' : '[−]'}
        </span>
      </div>
      <div className={`panel-content ${isCollapsed ? 'hidden' : 'visible'}`}>
        {!isCollapsed && children}
      </div>
    </div>
  );
};

export default CollapsiblePanel;