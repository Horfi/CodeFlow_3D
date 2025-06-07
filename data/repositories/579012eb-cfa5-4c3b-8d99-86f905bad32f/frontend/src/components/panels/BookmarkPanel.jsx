// frontend/src/components/panels/BookmarkPanel.jsx
import React, { useState, useEffect } from 'react';
import CollapsiblePanel from './CollapsiblePanel';
import Button from '../shared/Button';

const BookmarkPanel = ({ algorithms, onFileSelect }) => {
  const [bookmarks, setBookmarks] = useState([]);
  const [sortBy, setSortBy] = useState('usage');

  useEffect(() => {
    loadBookmarks();
  }, []);

  const loadBookmarks = async () => {
    try {
      const response = await fetch('/api/bookmarks');
      const data = await response.json();
      setBookmarks(data);
    } catch (error) {
      console.error('Failed to load bookmarks:', error);
    }
  };

  const sortedBookmarks = algorithms?.ranking?.sortBookmarks(bookmarks, sortBy) || bookmarks;

  const addCurrentFileToBookmarks = async () => {
    try {
      const response = await fetch('/api/bookmarks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filePath: 'current-file-path' })
      });
      if (response.ok) {
        loadBookmarks();
      }
    } catch (error) {
      console.error('Failed to add bookmark:', error);
    }
  };

  const removeBookmark = async (path) => {
    try {
      const response = await fetch(`/api/bookmarks/${encodeURIComponent(path)}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        loadBookmarks();
      }
    } catch (error) {
      console.error('Failed to remove bookmark:', error);
    }
  };

  const clearAllBookmarks = async () => {
    try {
      const response = await fetch('/api/bookmarks', { method: 'DELETE' });
      if (response.ok) {
        setBookmarks([]);
      }
    } catch (error) {
      console.error('Failed to clear bookmarks:', error);
    }
  };

  return (
    <CollapsiblePanel title="My Bookmarks" icon="📑" defaultCollapsed={false}>
      <div className="bookmark-controls">
        <select 
          value={sortBy} 
          onChange={(e) => setSortBy(e.target.value)}
          className="sort-dropdown"
        >
          <option value="usage">By Usage</option>
          <option value="date">By Date</option>
          <option value="name">By Name</option>
          <option value="importance">By Importance</option>
        </select>
        <Button onClick={clearAllBookmarks} className="clear-btn" size="small">
          🗑️ Clear All
        </Button>
      </div>
      
      <div className="bookmark-list">
        {sortedBookmarks.map(bookmark => (
          <div key={bookmark.path} className="bookmark-item">
            <span className="bookmark-icon">📌</span>
            <span 
              className="bookmark-name"
              onClick={() => onFileSelect(bookmark)}
            >
              {bookmark.name}
            </span>
            <span className="bookmark-stats">
              {algorithms?.ranking?.getBookmarkStats?.(bookmark) || ''}
            </span>
            <Button 
              onClick={() => removeBookmark(bookmark.path)}
              className="remove-btn"
              size="small"
            >
              ×
            </Button>
          </div>
        ))}
      </div>
      
      <Button 
        onClick={addCurrentFileToBookmarks}
        className="add-current-btn"
      >
        + Add Current File
      </Button>
    </CollapsiblePanel>
  );
};

export default BookmarkPanel;