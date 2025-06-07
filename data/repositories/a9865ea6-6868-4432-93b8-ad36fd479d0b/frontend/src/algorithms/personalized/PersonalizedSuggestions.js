// frontend/src/algorithms/personalized/PersonalizedSuggestions.js
import { SuggestionInterface } from '../factory/AlgorithmInterface';

export class PersonalizedSuggestions extends SuggestionInterface {
  constructor(userModel, config) {
    super(userModel, config);
    this.suggestionCache = new Map();
    this.contextHistory = [];
  }

  async generatePersonalizedSuggestions(currentFile, context = {}) {
    if (!currentFile) return [];
    
    const cacheKey = `${currentFile.path}_${JSON.stringify(context)}`;
    if (this.suggestionCache.has(cacheKey)) {
      return this.suggestionCache.get(cacheKey);
    }

    const suggestions = [];
    const algorithms = this.config.suggestions.algorithms;

    // Run different suggestion algorithms
    if (algorithms.includes('dependency')) {
      suggestions.push(...await this.getDependencyBasedSuggestions(currentFile));
    }
    
    if (algorithms.includes('pattern')) {
      suggestions.push(...await this.getPatternBasedSuggestions(currentFile));
    }
    
    if (algorithms.includes('similarity')) {
      suggestions.push(...await this.getSimilarityBasedSuggestions(currentFile));
    }
    
    if (algorithms.includes('centrality')) {
      suggestions.push(...await this.getCentralityBasedSuggestions(currentFile));
    }

    // Remove duplicates and filter by confidence
    const uniqueSuggestions = this.deduplicateSuggestions(suggestions);
    const filteredSuggestions = uniqueSuggestions.filter(
      s => s.confidence >= this.config.suggestions.confidenceThreshold
    );

    // Sort by confidence and limit results
    const finalSuggestions = filteredSuggestions
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, this.config.suggestions.maxSuggestions);

    this.suggestionCache.set(cacheKey, finalSuggestions);
    return finalSuggestions;
  }

  async getDependencyBasedSuggestions(currentFile) {
    const suggestions = [];
    
    // Direct dependencies
    if (currentFile.dependencies) {
      for (const dep of currentFile.dependencies) {
        const confidence = 0.8 + (this.getUserAffinityScore(dep.path) * 0.2);
        suggestions.push({
          file: dep.path,
          name: dep.name,
          confidence,
          reason: `Direct dependency of ${currentFile.name}`,
          type: 'dependency'
        });
      }
    }

    // Reverse dependencies (files that depend on current file)
    const reverseDeps = await this.getReverseDependencies(currentFile.path);
    for (const dep of reverseDeps) {
      const confidence = 0.7 + (this.getUserAffinityScore(dep.path) * 0.3);
      suggestions.push({
        file: dep.path,
        name: dep.name,
        confidence,
        reason: `Depends on ${currentFile.name}`,
        type: 'reverse_dependency'
      });
    }

    return suggestions;
  }

  async getPatternBasedSuggestions(currentFile) {
    if (!this.userModel) return [];
    
    const suggestions = [];
    const coAccessedFiles = this.userModel.getCoAccessedFiles(currentFile.path);
    
    for (const [filePath, coAccessScore] of Object.entries(coAccessedFiles)) {
      const confidence = Math.min(0.9, coAccessScore * 1.2);
      if (confidence > 0.3) {
        suggestions.push({
          file: filePath,
          name: this.getFileName(filePath),
          confidence,
          reason: `Often accessed together with ${currentFile.name}`,
          type: 'pattern'
        });
      }
    }

    return suggestions;
  }

  async getSimilarityBasedSuggestions(currentFile) {
    const suggestions = [];
    const allFiles = this.getAllAvailableFiles();
    
    for (const file of allFiles) {
      if (file.path === currentFile.path) continue;
      
      const similarity = this.calculateFileSimilarity(currentFile, file);
      if (similarity > 0.4) {
        const langBoost = this.userModel?.getLanguagePreference(file.language) || 0.5;
        const confidence = (similarity * 0.7) + (langBoost * 0.3);
        
        suggestions.push({
          file: file.path,
          name: file.name,
          confidence,
          reason: `Similar to ${currentFile.name}`,
          type: 'similarity'
        });
      }
    }

    return suggestions;
  }

  async getCentralityBasedSuggestions(currentFile) {
    const suggestions = [];
    const importantFiles = await this.getHighCentralityFiles();
    
    for (const file of importantFiles.slice(0, 3)) {
      const userAffinity = this.getUserAffinityScore(file.path);
      const confidence = (file.importance * 0.6) + (userAffinity * 0.4);
      
      suggestions.push({
        file: file.path,
        name: file.name,
        confidence,
        reason: `Important file in codebase (rank #${file.rank})`,
        type: 'centrality'
      });
    }

    return suggestions;
  }

  calculateFileSimilarity(file1, file2) {
    let similarity = 0;
    
    // Same language
    if (file1.language === file2.language) similarity += 0.3;
    
    // Same directory
    const dir1 = file1.path.split('/').slice(0, -1).join('/');
    const dir2 = file2.path.split('/').slice(0, -1).join('/');
    if (dir1 === dir2) similarity += 0.4;
    
    // Similar file names
    const nameSimiliarity = this.calculateNameSimilarity(file1.name, file2.name);
    similarity += nameSimiliarity * 0.3;
    
    return Math.min(1, similarity);
  }

  calculateNameSimilarity(name1, name2) {
    const tokens1 = name1.toLowerCase().split(/[._-]/);
    const tokens2 = name2.toLowerCase().split(/[._-]/);
    
    const intersection = tokens1.filter(token => tokens2.includes(token));
    const union = new Set([...tokens1, ...tokens2]);
    
    return intersection.length / union.size;
  }

  getUserAffinityScore(filePath) {
    if (!this.userModel) return 0.5;
    
    const interactions = this.userModel.getFileInteractionCount(filePath) || 0;
    const maxInteractions = this.userModel.getMaxInteractionCount() || 1;
    
    return Math.min(1, interactions / maxInteractions);
  }

  deduplicateSuggestions(suggestions) {
    const seen = new Set();
    return suggestions.filter(suggestion => {
      if (seen.has(suggestion.file)) return false;
      seen.add(suggestion.file);
      return true;
    });
  }

  async getContextualSuggestions() {
    if (!this.userModel) return [];
    
    const currentContext = this.userModel.getCurrentContext();
    const suggestions = [];
    
    // Recent files
    const recentFiles = this.userModel.getRecentFiles(5);
    recentFiles.forEach((file, index) => {
      suggestions.push({
        file: file.path,
        name: file.name,
        confidence: 0.8 - (index * 0.1),
        reason: `Recently accessed`,
        type: 'recent'
      });
    });
    
    // Frequently used files
    const frequentFiles = this.userModel.getFrequentFiles(3);
    frequentFiles.forEach(file => {
      suggestions.push({
        file: file.path,
        name: file.name,
        confidence: 0.7,
        reason: `Frequently accessed`,
        type: 'frequent'
      });
    });
    
    return suggestions;
  }

  async getCodeCompletions(code, position, filePath) {
    if (!this.config.enableAISuggestions) return [];
    
    // This would integrate with an AI service for code completions
    // For now, return basic suggestions based on user patterns
    
    const completions = [];
    
    if (this.userModel) {
      const commonPatterns = this.userModel.getCommonCodePatterns(filePath);
      
      commonPatterns.forEach((pattern, index) => {
        completions.push({
          label: pattern.text,
          kind: 1, // Text
          detail: `Common pattern (used ${pattern.frequency} times)`,
          insertText: pattern.text
        });
      });
    }
    
    return completions;
  }

  async getReverseDependencies(filePath) {
    try {
      const response = await fetch(`/api/files/${encodeURIComponent(filePath)}/dependents`);
      return response.ok ? await response.json() : [];
    } catch {
      return [];
    }
  }

  async getHighCentralityFiles() {
    try {
      const response = await fetch('/api/graph/centrality');
      return response.ok ? await response.json() : [];
    } catch {
      return [];
    }
  }

  getFileName(filePath) {
    return filePath.split('/').pop() || filePath;
  }

  getAllAvailableFiles() {
    return window.projectFiles || [];
  }
}