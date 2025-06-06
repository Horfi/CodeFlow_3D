// frontend/src/algorithms/random/RandomSearch.js
import { SearchInterface } from '../factory/AlgorithmInterface';

export class RandomSearch extends SearchInterface {
  constructor(config) {
    super(null, config);
    this.searchHistory = [];
  }

  async performSearch(query) {
    this.addToSearchHistory(query);
    
    const results = this.alphabeticalSearch(query);
    return this.randomizeResults(results);
  }

  alphabeticalSearch(query) {
    const results = [];
    const lowerQuery = query.toLowerCase();
    const allFiles = this.getAllAvailableFiles();
    
    allFiles.forEach(file => {
      if (file.name.toLowerCase().includes(lowerQuery) ||
          file.path.toLowerCase().includes(lowerQuery)) {
        results.push({
          ...file,
          relevanceScore: this.calculateAlphabeticalScore(file, query)
        });
      }
    });

    return results.sort((a, b) => a.name.localeCompare(b.name));
  }

  calculateAlphabeticalScore(file, query) {
    // Simple alphabetical-based scoring
    const position = file.name.toLowerCase().indexOf(query.toLowerCase());
    if (position === 0) return 1.0; // Starts with query
    if (position > 0) return 0.7; // Contains query
    return 0.5; // Default score
  }

  randomizeResults(results) {
    // Shuffle results to remove any accidental personalization
    const shuffled = [...results];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  rankResults(results, query) {
    // No intelligent ranking - just alphabetical
    return results.sort((a, b) => a.name.localeCompare(b.name));
  }

  addToSearchHistory(query) {
    this.searchHistory = [query, ...this.searchHistory.filter(q => q !== query)];
    this.searchHistory = this.searchHistory.slice(0, 10);
  }

  getSearchHistory() {
    return this.searchHistory;
  }

  getAllAvailableFiles() {
    return window.projectFiles || [];
  }
}