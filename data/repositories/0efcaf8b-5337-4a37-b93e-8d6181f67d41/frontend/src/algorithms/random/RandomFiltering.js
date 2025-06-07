// frontend/src/algorithms/random/RandomFiltering.js
import { FilteringInterface } from '../factory/AlgorithmInterface';

export class RandomFiltering extends FilteringInterface {
  constructor(config) {
    super(null, config);
  }

  getDefaultLanguages() {
    // Return all languages - no preferences
    const allFiles = this.getAllAvailableFiles();
    const languages = new Set();
    
    allFiles.forEach(file => {
      if (file.language) {
        languages.add(file.language);
      }
    });
    
    return Array.from(languages);
  }

  applyLanguageFilter(nodes, activeLanguages) {
    if (!activeLanguages || activeLanguages.length === 0) {
      return nodes;
    }
    
    return nodes.filter(node => 
      !node.language || activeLanguages.includes(node.language)
    );
  }

  getFilterPreferences() {
    // No preferences in random version
    return {};
  }

  getAllAvailableFiles() {
    return window.projectFiles || [];
  }
}
