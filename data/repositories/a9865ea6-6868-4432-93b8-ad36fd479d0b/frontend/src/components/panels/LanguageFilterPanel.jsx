// frontend/src/components/panels/LanguageFilterPanel.jsx
import React, { useState, useEffect } from 'react';
import CollapsiblePanel from './CollapsiblePanel';
import Button from '../shared/Button';

const LanguageFilterPanel = ({ algorithms, projectData, onFilterChange }) => {
  const [activeFilters, setActiveFilters] = useState(new Set());
  const [languageStats, setLanguageStats] = useState({});

  useEffect(() => {
    if (projectData) {
      calculateLanguageStats();
    }
  }, [projectData]);

  useEffect(() => {
    if (algorithms?.filtering) {
      const defaultLanguages = algorithms.filtering.getDefaultLanguages();
      setActiveFilters(new Set(defaultLanguages));
    }
  }, [algorithms]);

  const calculateLanguageStats = () => {
    const stats = {};
    if (projectData?.nodes) {
      projectData.nodes.forEach(node => {
        const lang = node.language || 'Unknown';
        if (!stats[lang]) {
          stats[lang] = { fileCount: 0, usagePercentage: 0 };
        }
        stats[lang].fileCount++;
      });

      const total = projectData.nodes.length;
      Object.keys(stats).forEach(lang => {
        stats[lang].usagePercentage = (stats[lang].fileCount / total) * 100;
      });
    }
    setLanguageStats(stats);
  };

  const toggleLanguageFilter = (lang) => {
    const newFilters = new Set(activeFilters);
    if (newFilters.has(lang)) {
      newFilters.delete(lang);
    } else {
      newFilters.add(lang);
    }
    setActiveFilters(newFilters);
    if (onFilterChange) onFilterChange(Array.from(newFilters));
  };

  const selectAllLanguages = () => {
    setActiveFilters(new Set(Object.keys(languageStats)));
  };

  const clearAllLanguages = () => {
    setActiveFilters(new Set());
  };

  const resetToDefaults = () => {
    if (algorithms?.filtering) {
      const defaultLanguages = algorithms.filtering.getDefaultLanguages();
      setActiveFilters(new Set(defaultLanguages));
    }
  };

  const getLanguageIcon = (lang) => {
    const icons = {
      'JavaScript': '🟨',
      'TypeScript': '🔷',
      'Python': '🐍',
      'Java': '☕',
      'C++': '⚡',
      'C#': '🔵',
      'Go': '🐹',
      'Rust': '🦀',
      'PHP': '🐘',
      'Ruby': '💎'
    };
    return icons[lang] || '📄';
  };

  return (
    <CollapsiblePanel title="Language Filters" icon="🎨" defaultCollapsed={false}>
      <div className="filter-controls">
        <Button onClick={selectAllLanguages} size="small">Select All</Button>
        <Button onClick={clearAllLanguages} size="small">Clear All</Button>
        <Button onClick={resetToDefaults} size="small">Reset to Defaults</Button>
      </div>
      
      <div className="language-filters">
        {Object.entries(languageStats).map(([lang, stats]) => (
          <div key={lang} className="filter-item">
            <label className="filter-checkbox">
              <input
                type="checkbox"
                checked={activeFilters.has(lang)}
                onChange={() => toggleLanguageFilter(lang)}
              />
              <span className="language-icon">{getLanguageIcon(lang)}</span>
              <span className="language-name">{lang}</span>
              <span className="file-count">({stats.fileCount})</span>
            </label>
            <div className="language-stats">
              <div 
                className="usage-bar" 
                style={{ width: `${stats.usagePercentage}%` }}
              />
              <span className="usage-text">{stats.usagePercentage.toFixed(1)}%</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="total-stats">
        📊 Total: {Object.values(languageStats).reduce((sum, stat) => sum + stat.fileCount, 0)} files
      </div>
    </CollapsiblePanel>
  );
};

export default LanguageFilterPanel;