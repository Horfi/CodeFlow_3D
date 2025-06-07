// frontend/src/algorithms/personalized/PersonalizedSearch.js
import { SearchInterface } from '../factory/AlgorithmInterface';

export class PersonalizedSearch extends SearchInterface {
  constructor(userModel, config) {
    super(userModel, config);
    this.searchHistory = [];
    this.searchIndex = new Map();
  }

  async performSearch(query) {
    this.addToSearchHistory(query);
    
    if (!this.config.searchRanking.useML) {
      return this.simpleSearch(query);
    }

    const results = await this.intelligentSearch(query);
    return this.rankResults(results, query);
  }

  simpleSearch(query) {
    const results = [];
    const lowerQuery = query.toLowerCase();
    
    // Get all available files from user model or cache
    const allFiles = this.getAllAvailableFiles();
    
    allFiles.forEach(file => {
      if (file.name.toLowerCase().includes(lowerQuery) ||
          file.path.toLowerCase().includes(lowerQuery)) {
        results.push({
          ...file,
          relevanceScore: this.calculateSimpleRelevance(file, query)
        });
      }
    });

    return results.sort((a, b) => b.relevanceScore - a.relevanceScore);
  }

  async intelligentSearch(query) {
    const results = [];
    const allFiles = this.getAllAvailableFiles();
    
    for (const file of allFiles) {
      const score = await this.calculateIntelligentScore(file, query);
      if (score > 0.1) {
        results.push({
          ...file,
          relevanceScore: score,
          preview: await this.generatePreview(file, query)
        });
      }
    }

    return results;
  }

  calculateSimpleRelevance(file, query) {
    const lowerQuery = query.toLowerCase();
    const fileName = file.name.toLowerCase();
    const filePath = file.path.toLowerCase();
    
    let score = 0;
    
    // Exact name match
    if (fileName === lowerQuery) score += 1.0;
    // Name starts with query
    else if (fileName.startsWith(lowerQuery)) score += 0.8;
    // Name contains query
    else if (fileName.includes(lowerQuery)) score += 0.6;
    // Path contains query
    else if (filePath.includes(lowerQuery)) score += 0.4;
    
    return score;
  }

  async calculateIntelligentScore(file, query) {
    let score = this.calculateSimpleRelevance(file, query);
    
    if (!this.userModel) return score;

    // User interaction boost
    const interactionScore = this.userModel.getFileInteractionCount(file.path) || 0;
    const maxInteractions = this.userModel.getMaxInteractionCount() || 1;
    const normalizedInteractions = interactionScore / maxInteractions;
    
    // Recent access boost
    const lastAccess = this.userModel.getLastAccessTime(file.path) || 0;
    const hoursSinceAccess = (Date.now() - lastAccess) / (1000 * 60 * 60);
    const recencyBoost = Math.max(0, 1 - (hoursSinceAccess / 48)); // Decay over 48 hours
    
    // Language preference
    const langPreference = this.userModel.getLanguagePreference(file.language) || 0.5;
    
    // Context similarity (if we have current file context)
    const contextBoost = this.calculateContextualRelevance(file, query);
    
    // Weighted combination
    const personalizedScore = (
      score * 0.4 +
      normalizedInteractions * 0.25 +
      recencyBoost * 0.15 +
      langPreference * 0.1 +
      contextBoost * 0.1
    );

    return Math.min(1, personalizedScore);
  }

  calculateContextualRelevance(file, query) {
    // Check if query relates to current working context
    const currentFiles = this.userModel?.getCurrentSessionFiles() || [];
    
    if (currentFiles.some(cf => cf.path === file.path)) {
      return 0.3; // Boost for files in current session
    }
    
    // Check for dependency relationships with current files
    for (const currentFile of currentFiles) {
      if (this.areFilesRelated(file, currentFile)) {
        return 0.2;
      }
    }
    
    return 0;
  }

  areFilesRelated(file1, file2) {
    // Simple heuristic - same directory or similar names
    const dir1 = file1.path.split('/').slice(0, -1).join('/');
    const dir2 = file2.path.split('/').slice(0, -1).join('/');
    
    return dir1 === dir2 || 
           file1.dependencies?.some(dep => dep.path === file2.path) ||
           file2.dependencies?.some(dep => dep.path === file1.path);
  }

  async generatePreview(file, query) {
    // Generate a relevant preview snippet
    const content = await this.getFileContent(file.path);
    if (!content) return '';
    
    const lines = content.split('\n');
    const queryLower = query.toLowerCase();
    
    // Find lines containing the query
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].toLowerCase().includes(queryLower)) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 2);
        return lines.slice(start, end).join('\n').substring(0, 150) + '...';
      }
    }
    
    // Return first few lines if no match
    return lines.slice(0, 3).join('\n').substring(0, 150) + '...';
  }

  async getFileContent(filePath) {
    try {
      const response = await fetch(`/api/files/${encodeURIComponent(filePath)}`);
      return response.ok ? await response.text() : '';
    } catch {
      return '';
    }
  }

  rankResults(results, query) {
    if (!this.config.searchRanking.personalizeResults) {
      return results.sort((a, b) => b.relevanceScore - a.relevanceScore);
    }

    // Apply personalized ranking
    return results.sort((a, b) => {
      const scoreA = this.getPersonalizedRankingScore(a, query);
      const scoreB = this.getPersonalizedRankingScore(b, query);
      return scoreB - scoreA;
    });
  }

  getPersonalizedRankingScore(result, query) {
    let score = result.relevanceScore;
    
    if (this.userModel) {
      // Boost frequently accessed files
      const frequency = this.userModel.getFileAccessFrequency(result.path) || 0;
      score += frequency * 0.1;
      
      // Boost recently accessed files
      const recency = this.userModel.getFileRecencyScore(result.path) || 0;
      score += recency * 0.1;
      
      // Boost files in preferred languages
      const langPreference = this.userModel.getLanguagePreference(result.language) || 0.5;
      score += (langPreference - 0.5) * 0.1;
    }
    
    return score;
  }

  addToSearchHistory(query) {
    this.searchHistory = [query, ...this.searchHistory.filter(q => q !== query)];
    this.searchHistory = this.searchHistory.slice(0, 20); // Keep last 20 searches
  }

  getSearchHistory() {
    return this.searchHistory;
  }

  getAllAvailableFiles() {
    // This would typically come from a global store or cache
    return window.projectFiles || [];
  }
}