// frontend/src/algorithms/random/RandomSuggestions.js
import { SuggestionInterface } from '../factory/AlgorithmInterface';

export class RandomSuggestions extends SuggestionInterface {
  constructor(config) {
    super(null, config);
  }

  async generatePersonalizedSuggestions(currentFile, context = {}) {
    if (!currentFile) return [];
    
    const allFiles = this.getAllAvailableFiles();
    const otherFiles = allFiles.filter(f => f.path !== currentFile.path);
    
    // Return random files
    const randomFiles = this.getRandomFiles(otherFiles, this.config.suggestions.maxSuggestions);
    
    return randomFiles.map((file, index) => ({
      file: file.path,
      name: file.name,
      confidence: Math.random() * 0.6 + 0.2, // Random confidence 0.2-0.8
      reason: this.getRandomReason(),
      type: 'random'
    }));
  }

  getRandomFiles(files, count) {
    const shuffled = [...files].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count);
  }

  getRandomReason() {
    const reasons = [
      'Randomly suggested',
      'Might be interesting',
      'Found in project',
      'Available file',
      'Consider checking'
    ];
    return reasons[Math.floor(Math.random() * reasons.length)];
  }

  async getContextualSuggestions() {
    const allFiles = this.getAllAvailableFiles();
    const randomFiles = this.getRandomFiles(allFiles, 5);
    
    return randomFiles.map(file => ({
      file: file.path,
      name: file.name,
      confidence: Math.random() * 0.5 + 0.3,
      reason: 'Random suggestion',
      type: 'random'
    }));
  }

  async getCodeCompletions(code, position, filePath) {
    // No intelligent code completions in random version
    return [];
  }

  getAllAvailableFiles() {
    return window.projectFiles || [];
  }
}
