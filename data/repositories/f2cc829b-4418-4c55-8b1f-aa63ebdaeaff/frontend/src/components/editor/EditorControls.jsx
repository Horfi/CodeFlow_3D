// frontend/src/components/editor/EditorControls.jsx
import React from 'react';
import Button from '../shared/Button';

const EditorControls = ({ onSave, onCopy, onClose, canSave, canCopy }) => {
  return (
    <div className="editor-controls">
      <Button
        onClick={onCopy}
        disabled={!canCopy}
        size="small"
        title="Copy to clipboard (Ctrl+C)"
      >
        📋 Copy
      </Button>
      
      <Button
        onClick={onSave}
        disabled={!canSave}
        size="small"
        variant="primary"
        title="Save file (Ctrl+S)"
      >
        💾 Save
      </Button>
      
      <Button
        onClick={onClose}
        size="small"
        variant="secondary"
        title="Close file"
      >
        ❌ Close
      </Button>
    </div>
  );
};

export default EditorControls;