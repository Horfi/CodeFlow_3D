// frontend/src/components/editor/CodeEditorPanel.jsx
import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import EditorControls from './EditorControls';
import DependencyList from './DependencyList';
import FileMetadata from './FileMetadata';

const CodeEditorPanel = ({ algorithms, selectedFile, onInteraction }) => {
  const [fileContent, setFileContent] = useState('// Select a file to start editing...');
  const [language, setLanguage] = useState('javascript');
  const [loading, setLoading] = useState(false);
  const [isModified, setIsModified] = useState(false);
  const [dependencies, setDependencies] = useState([]);
  const editorRef = useRef(null);

  useEffect(() => {
    if (selectedFile) {
      loadFileContent(selectedFile);
    }
  }, [selectedFile]);

  const loadFileContent = async (file) => {
    if (!file?.path) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/files/${encodeURIComponent(file.path)}`);
      if (response.ok) {
        const content = await response.text();
        setFileContent(content);
        setLanguage(detectLanguage(file.path));
        setIsModified(false);
        
        // Load dependencies
        loadFileDependencies(file.path);
        
        // Track interaction
        onInteraction({
          type: 'file_opened',
          filePath: file.path,
          timestamp: Date.now()
        });
      }
    } catch (error) {
      console.error('Failed to load file:', error);
      setFileContent('// Error loading file');
    }
    setLoading(false);
  };

  const loadFileDependencies = async (filePath) => {
    try {
      const response = await fetch(`/api/files/${encodeURIComponent(filePath)}/dependencies`);
      if (response.ok) {
        const deps = await response.json();
        setDependencies(deps);
      }
    } catch (error) {
      console.error('Failed to load dependencies:', error);
    }
  };

  const detectLanguage = (filePath) => {
    const ext = filePath.split('.').pop()?.toLowerCase();
    const languageMap = {
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'py': 'python',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'html': 'html',
      'css': 'css',
      'scss': 'scss',
      'json': 'json',
      'xml': 'xml',
      'yml': 'yaml',
      'yaml': 'yaml',
      'md': 'markdown'
    };
    return languageMap[ext] || 'plaintext';
  };

  const handleEditorChange = (value) => {
    setFileContent(value);
    setIsModified(true);
    
    // Debounced dependency analysis
    clearTimeout(window.dependencyAnalysisTimeout);
    window.dependencyAnalysisTimeout = setTimeout(() => {
      analyzeDependencyChanges(value);
    }, 1000);

    // Track editing activity
    onInteraction({
      type: 'code_edited',
      filePath: selectedFile?.path,
      timestamp: Date.now(),
      contentLength: value?.length || 0
    });
  };

  const analyzeDependencyChanges = async (content) => {
    if (!selectedFile?.path || !algorithms?.parsing) return;

    try {
      const newDependencies = await algorithms.parsing.parseDependencies(content, language);
      
      // Compare with old dependencies
      const hasChanges = JSON.stringify(dependencies) !== JSON.stringify(newDependencies);
      
      if (hasChanges) {
        setDependencies(newDependencies);
        
        // Notify about dependency changes
        onInteraction({
          type: 'dependencies_changed',
          filePath: selectedFile.path,
          oldDeps: dependencies,
          newDeps: newDependencies,
          timestamp: Date.now()
        });
      }
    } catch (error) {
      console.error('Dependency analysis failed:', error);
    }
  };

  const handleEditorMount = (editor, monaco) => {
    editorRef.current = editor;
    
    // Setup intelligent autocomplete if personalized version
    if (algorithms?.suggestions) {
      setupIntelligentAutocomplete(monaco);
    }
    
    // Setup custom key bindings
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      handleSave();
    });
  };

  const setupIntelligentAutocomplete = (monaco) => {
    monaco.languages.registerCompletionItemProvider(language, {
      provideCompletionItems: async (model, position) => {
        if (!algorithms?.suggestions) return { suggestions: [] };
        
        const suggestions = await algorithms.suggestions.getCodeCompletions(
          model.getValue(),
          position,
          selectedFile?.path
        );
        
        return { suggestions };
      }
    });
  };

  const handleSave = async () => {
    if (!selectedFile?.path || !isModified) return;

    try {
      const response = await fetch(`/api/files/${encodeURIComponent(selectedFile.path)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: fileContent })
      });

      if (response.ok) {
        setIsModified(false);
        onInteraction({
          type: 'file_saved',
          filePath: selectedFile.path,
          timestamp: Date.now()
        });
      }
    } catch (error) {
      console.error('Failed to save file:', error);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(fileContent);
      onInteraction({
        type: 'code_copied',
        filePath: selectedFile?.path,
        timestamp: Date.now(),
        contentLength: fileContent.length
      });
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const handleClose = () => {
    if (isModified) {
      const confirmClose = window.confirm('You have unsaved changes. Are you sure you want to close?');
      if (!confirmClose) return;
    }
    
    setFileContent('// Select a file to start editing...');
    setLanguage('javascript');
    setIsModified(false);
    setDependencies([]);
  };

  return (
    <div className="code-editor-panel">
      <div className="editor-header">
        <div className="editor-title">
          {selectedFile ? (
            <>
              <span className="file-icon">📄</span>
              <span className="file-name">{selectedFile.name}</span>
              {isModified && <span className="modified-indicator">●</span>}
            </>
          ) : (
            <span>Code Editor</span>
          )}
        </div>
        
        <EditorControls
          onSave={handleSave}
          onCopy={handleCopy}
          onClose={handleClose}
          canSave={isModified && selectedFile}
          canCopy={!!fileContent && fileContent !== '// Select a file to start editing...'}
        />
      </div>

      <div className="editor-content">
        <div className="editor-wrapper">
          {loading ? (
            <div className="editor-loading">Loading file...</div>
          ) : (
            <Editor
              height="60%"
              language={language}
              value={fileContent}
              onChange={handleEditorChange}
              onMount={handleEditorMount}
              theme="vs-dark"
              options={{
                fontSize: 14,
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                automaticLayout: true,
                minimap: { enabled: true },
                folding: true,
                wordWrap: 'on',
                readOnly: !selectedFile
              }}
            />
          )}
        </div>

        <div className="editor-sidebar">
          <DependencyList
            dependencies={dependencies}
            selectedFile={selectedFile}
            onDependencyClick={(dep) => onInteraction({
              type: 'dependency_clicked',
              targetFile: dep.path,
              sourceFile: selectedFile?.path,
              timestamp: Date.now()
            })}
          />
          
          <FileMetadata
            file={selectedFile}
            algorithms={algorithms}
          />
        </div>
      </div>
    </div>
  );
};

export default CodeEditorPanel;