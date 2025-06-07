// frontend/src/algorithms/personalized/PersonalizedFiltering.js
import { FilteringInterface } from '../factory/AlgorithmInterface';

export class PersonalizedFiltering extends FilteringInterface {
  constructor(userModel, config) {
    super(userModel, config);
  }

  getDefaultLanguages() {
    if (!this.userModel) {
      return this.getAllLanguages();
    }

    // Get user's preferred languages based on usage
    const languagePreferences = this.userModel.getLanguagePreferences();
    const topLanguages = Object.entries(languagePreferences)
      .sort(([,a], [,b]) => b.usageScore - a.usageScore)
      .slice(0, 5)
      .map(([lang]) => lang);

    // Include at least the top 3 most used languages
    const allLanguages = this.getAllLanguages();
    const defaultSet = new Set(topLanguages);
    
    // Add languages with high interaction scores
    allLanguages.forEach(lang => {
      const preference = languagePreferences[lang];
      if (preference && preference.usageScore > 0.3) {
        defaultSet.add(lang);
      }
    });

    return Array.from(defaultSet);
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
    if (!this.userModel) return {};

    return {
      languages: this.userModel.getLanguagePreferences(),
      folders: this.userModel.getFolderPreferences(),
      fileTypes: this.userModel.getFileTypePreferences()
    };
  }

  getAllLanguages() {
    const allFiles = this.getAllAvailableFiles();
    const languages = new Set();
    
    allFiles.forEach(file => {
      if (file.language) {
        languages.add(file.language);
      }
    });
    
    return Array.from(languages);
  }

  getAllAvailableFiles() {
    return window.projectFiles || [];
  }
}