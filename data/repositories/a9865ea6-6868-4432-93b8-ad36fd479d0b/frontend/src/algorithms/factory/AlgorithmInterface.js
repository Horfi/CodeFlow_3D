// frontend/src/algorithms/factory/AlgorithmInterface.js
export class BaseAlgorithm {
  constructor(userModel = null, config = {}) {
    this.userModel = userModel;
    this.config = config;
    this.version = config.version || 'unknown';
  }

  // Abstract methods to be implemented by subclasses
  initialize() {
    throw new Error('initialize() must be implemented by subclass');
  }

  process(data) {
    throw new Error('process() must be implemented by subclass');
  }

  updateConfiguration(newConfig) {
    this.config = { ...this.config, ...newConfig };
  }

  getMetrics() {
    return {
      version: this.version,
      config: this.config,
      lastUpdated: Date.now()
    };
  }
}

export class LayoutInterface extends BaseAlgorithm {
  calculateNodePosition(node, importance) {
    throw new Error('calculateNodePosition() must be implemented');
  }

  calculateNodeSize(node) {
    throw new Error('calculateNodeSize() must be implemented');
  }

  applyLayout(graph) {
    throw new Error('applyLayout() must be implemented');
  }

  processGraphData(data) {
    throw new Error('processGraphData() must be implemented');
  }
}

export class ColoringInterface extends BaseAlgorithm {
  calculateNodeColor(node) {
    throw new Error('calculateNodeColor() must be implemented');
  }

  calculateEdgeColor(edge) {
    throw new Error('calculateEdgeColor() must be implemented');
  }

  getColorScheme() {
    throw new Error('getColorScheme() must be implemented');
  }
}

export class SearchInterface extends BaseAlgorithm {
  performSearch(query) {
    throw new Error('performSearch() must be implemented');
  }

  rankResults(results, query) {
    throw new Error('rankResults() must be implemented');
  }

  getSearchHistory() {
    throw new Error('getSearchHistory() must be implemented');
  }
}

export class SuggestionInterface extends BaseAlgorithm {
  generatePersonalizedSuggestions(currentFile, context) {
    throw new Error('generatePersonalizedSuggestions() must be implemented');
  }

  getContextualSuggestions() {
    throw new Error('getContextualSuggestions() must be implemented');
  }

  getCodeCompletions(code, position, filePath) {
    throw new Error('getCodeCompletions() must be implemented');
  }
}

export class FilteringInterface extends BaseAlgorithm {
  getDefaultLanguages() {
    throw new Error('getDefaultLanguages() must be implemented');
  }

  applyLanguageFilter(nodes, activeLanguages) {
    throw new Error('applyLanguageFilter() must be implemented');
  }

  getFilterPreferences() {
    throw new Error('getFilterPreferences() must be implemented');
  }
}

export class RankingInterface extends BaseAlgorithm {
  sortBookmarks(bookmarks, criteria) {
    throw new Error('sortBookmarks() must be implemented');
  }

  getBookmarkStats(bookmark) {
    throw new Error('getBookmarkStats() must be implemented');
  }

  rankFilesByImportance(files) {
    throw new Error('rankFilesByImportance() must be implemented');
  }
}