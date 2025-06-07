// frontend/src/components/panels/SearchPanel.jsx
import React, { useState, useEffect } from 'react';
import CollapsiblePanel from './CollapsiblePanel';
import Button from '../shared/Button';
import { useDebounce } from '../../hooks/useDebounce';

const SearchPanel = ({ algorithms, projectData, onFileSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const debouncedQuery = useDebounce(searchQuery, 300);

  useEffect(() => {
    if (debouncedQuery.length > 2) {
      performSearch(debouncedQuery);
    } else {
      setSearchResults([]);
    }
  }, [debouncedQuery, algorithms]);

  useEffect(() => {
    loadAISuggestions();
  }, [algorithms]);

  const performSearch = async (query) => {
    setIsSearching(true);
    try {
      if (algorithms?.search) {
        const results = await algorithms.search.performSearch(query);
        setSearchResults(results);
      } else {
        // Fallback search
        const results = projectData?.nodes?.filter(node => 
          node.name.toLowerCase().includes(query.toLowerCase()) ||
          node.path.toLowerCase().includes(query.toLowerCase())
        ) || [];
        setSearchResults(results.slice(0, 10));
      }
    } catch (error) {
      console.error('Search failed:', error);
    }
    setIsSearching(false);
  };

  const loadAISuggestions = async () => {
    try {
      if (algorithms?.suggestions) {
        const suggestions = await algorithms.suggestions.getContextualSuggestions();
        setAiSuggestions(suggestions);
      }
    } catch (error) {
      console.error('Failed to load AI suggestions:', error);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
  };

  const addToHistory = (query) => {
    setSearchHistory(prev => {
      const newHistory = [query, ...prev.filter(q => q !== query)];
      return newHistory.slice(0, 5);
    });
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      addToHistory(searchQuery.trim());
      performSearch(searchQuery.trim());
    }
  };

  const getFileIcon = (filePath) => {
    const ext = filePath.split('.').pop()?.toLowerCase();
    const icons = {
      'js': '🟨', 'jsx': '⚛️', 'ts': '🔷', 'tsx': '⚛️',
      'py': '🐍', 'java': '☕', 'cpp': '⚡', 'c': '⚡',
      'html': '🌐', 'css': '🎨', 'scss': '🎨',
      'json': '📋', 'xml': '📋', 'yml': '⚙️', 'yaml': '⚙️',
      'md': '📝', 'txt': '📄'
    };
    return icons[ext] || '📄';
  };

  return (
    <CollapsiblePanel title="Search & Suggestions" icon="🔍" defaultCollapsed={false}>
      <div className="search-container">
        <form onSubmit={handleSearchSubmit} className="search-input-wrapper">
          <input
            type="text"
            placeholder="Search files, functions, classes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <Button 
            onClick={clearSearch} 
            className="clear-search"
            size="small"
            type="button"
          >
            ×
          </Button>
        </form>
        
        {isSearching && <div className="search-loading">Searching...</div>}
        
        {searchQuery && searchResults.length > 0 && (
          <div className="search-results">
            <h4>🎯 Exact Matches:</h4>
            {searchResults.map(result => (
              <div 
                key={result.path} 
                className="search-result-item"
                onClick={() => onFileSelect(result)}
              >
                <div className="result-header">
                  <span className="result-icon">{getFileIcon(result.path)}</span>
                  <span className="result-name">{result.name}</span>
                  <span className="result-score">
                    {'⭐'.repeat(Math.ceil((result.relevanceScore || 0.5) * 5))}
                  </span>
                </div>
                {result.preview && (
                  <div className="result-preview">{result.preview}</div>
                )}
                <div className="result-path">{result.path}</div>
              </div>
            ))}
          </div>
        )}
        
        <div className="ai-suggestions">
          <h4>🧠 AI Suggestions:</h4>
          {aiSuggestions.map(suggestion => (
            <div 
              key={suggestion.path} 
              className="suggestion-item"
              onClick={() => onFileSelect(suggestion)}
            >
              <div className="suggestion-header">
                <span className="suggestion-icon">{getFileIcon(suggestion.path)}</span>
                <span className="suggestion-name">{suggestion.name}</span>
                <span className="suggestion-confidence">
                  {'⭐'.repeat(Math.ceil((suggestion.confidence || 0.5) * 4))}
                </span>
              </div>
              <div className="suggestion-reason">
                💡 {suggestion.reason}
              </div>
            </div>
          ))}
        </div>
        
        {searchHistory.length > 0 && (
          <div className="search-history">
            <h4>📚 Recent Searches:</h4>
            {searchHistory.map(query => (
              <div 
                key={query} 
                className="history-item"
                onClick={() => setSearchQuery(query)}
              >
                🔍 {query}
              </div>
            ))}
          </div>
        )}
      </div>
    </CollapsiblePanel>
  );
};

export default SearchPanel;