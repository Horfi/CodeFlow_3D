// frontend/src/components/layout/SplitLayout.jsx
import React, { useState } from 'react';
import Graph3DCanvas from '../graph/Graph3DCanvas';
import CodeEditorPanel from '../editor/CodeEditorPanel';
import BookmarkPanel from '../panels/BookmarkPanel';
import LanguageFilterPanel from '../panels/LanguageFilterPanel';
import SearchPanel from '../panels/SearchPanel';

const SplitLayout = ({ algorithms, projectData, version, onInteraction }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [panelStates, setPanelStates] = useState({
    bookmarks: false,
    languages: false,
    search: false
  });

  const togglePanel = (panelName) => {
    setPanelStates(prev => ({
      ...prev,
      [panelName]: !prev[panelName]
    }));
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    onInteraction({
      type: 'file_selected',
      filePath: file.path,
      timestamp: Date.now()
    });
  };

  return (
    <div className="split-layout">
      <div className="left-panels">
        <div className="panel-tabs">
          <button 
            onClick={() => togglePanel('bookmarks')}
            className={panelStates.bookmarks ? 'active' : ''}
          >
            📑 Bookmarks
          </button>
          <button 
            onClick={() => togglePanel('languages')}
            className={panelStates.languages ? 'active' : ''}
          >
            🎨 Languages
          </button>
          <button 
            onClick={() => togglePanel('search')}
            className={panelStates.search ? 'active' : ''}
          >
            🔍 Search
          </button>
        </div>

        <div className="panel-content">
          {panelStates.bookmarks && (
            <BookmarkPanel 
              algorithms={algorithms}
              onFileSelect={handleFileSelect}
            />
          )}
          {panelStates.languages && (
            <LanguageFilterPanel 
              algorithms={algorithms}
              projectData={projectData}
            />
          )}
          {panelStates.search && (
            <SearchPanel 
              algorithms={algorithms}
              projectData={projectData}
              onFileSelect={handleFileSelect}
            />
          )}
        </div>
      </div>

      <div className="center-canvas">
        <Graph3DCanvas
          algorithms={algorithms}
          projectData={projectData}
          version={version}
          onFileSelect={handleFileSelect}
          selectedFile={selectedFile}
        />
      </div>

      <div className="right-panel">
        <CodeEditorPanel
          algorithms={algorithms}
          selectedFile={selectedFile}
          onInteraction={onInteraction}
        />
      </div>
    </div>
  );
};

export default SplitLayout;