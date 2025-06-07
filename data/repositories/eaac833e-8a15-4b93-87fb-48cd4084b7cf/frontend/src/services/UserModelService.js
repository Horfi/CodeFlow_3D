// frontend/src/services/UserModelService.js
import APIService from './APIService';

class UserModelService {
  constructor() {
    this.userModel = {
      fileInteractions: new Map(),
      languagePreferences: new Map(),
      behaviorPatterns: {},
      sessionData: {
        startTime: Date.now(),
        currentFiles: [],
        interactions: []
      }
    };
    
    this.loadUserModel();
  }

  async loadUserModel() {
    try {
      const savedModel = await APIService.getUserModel();
      if (savedModel) {
        this.userModel = {
          ...this.userModel,
          ...savedModel,
          fileInteractions: new Map(Object.entries(savedModel.fileInteractions || {})),
          languagePreferences: new Map(Object.entries(savedModel.languagePreferences || {}))
        };
      }
    } catch (error) {
      console.warn('Failed to load user model:', error);
    }
  }

  async saveUserModel() {
    try {
      const modelToSave = {
        ...this.userModel,
        fileInteractions: Object.fromEntries(this.userModel.fileInteractions),
        languagePreferences: Object.fromEntries(this.userModel.languagePreferences)
      };
      
      await APIService.updateUserModel(modelToSave);
    } catch (error) {
      console.warn('Failed to save user model:', error);
    }
  }

  updateFromInteraction(interaction) {
    const { type, filePath, timestamp } = interaction;
    
    if (!filePath) return;

    // Update file interactions
    const fileData = this.userModel.fileInteractions.get(filePath) || {
      clickCount: 0,
      editCount: 0,
      totalTime: 0,
      lastAccess: 0,
      language: null
    };

    switch (type) {
      case 'file_opened':
      case 'file_selected':
      case 'node_click':
        fileData.clickCount++;
        fileData.lastAccess = timestamp;
        break;
      case 'code_edited':
        fileData.editCount++;
        break;
      case 'time_spent':
        fileData.totalTime += interaction.duration || 0;
        break;
    }

    this.userModel.fileInteractions.set(filePath, fileData);

    // Update language preferences
    if (interaction.language) {
      const langData = this.userModel.languagePreferences.get(interaction.language) || {
        usageScore: 0,
        fileCount: 0,
        totalTime: 0
      };
      
      langData.usageScore += 0.1;
      this.userModel.languagePreferences.set(interaction.language, langData);
    }

    // Add to session data
    this.userModel.sessionData.interactions.push(interaction);
    
    // Auto-save periodically
    if (this.userModel.sessionData.interactions.length % 10 === 0) {
      this.saveUserModel();
    }
  }

  getFileInteractionCount(filePath) {
    return this.userModel.fileInteractions.get(filePath)?.clickCount || 0;
  }

  getFileEditCount(filePath) {
    return this.userModel.fileInteractions.get(filePath)?.editCount || 0;
  }

  getTotalTimeSpent(filePath) {
    return this.userModel.fileInteractions.get(filePath)?.totalTime || 0;
  }

  getLastAccessTime(filePath) {
    return this.userModel.fileInteractions.get(filePath)?.lastAccess || 0;
  }

  getFileTemperature(filePath) {
    const interactions = this.getFileInteractionCount(filePath);
    const lastAccess = this.getLastAccessTime(filePath);
    const totalTime = this.getTotalTimeSpent(filePath);

    if (interactions === 0) return 0.5;

    // Calculate temperature based on recency and frequency
    const hoursSinceAccess = (Date.now() - lastAccess) / (1000 * 60 * 60);
    const recencyScore = Math.max(0, 1 - (hoursSinceAccess / 24));
    const frequencyScore = Math.min(1, interactions / 10);
    const timeScore = Math.min(1, totalTime / 300); // 5 minutes

    return (recencyScore * 0.4) + (frequencyScore * 0.4) + (timeScore * 0.2);
  }

  getFileImportance(filePath) {
    const interactions = this.getFileInteractionCount(filePath);
    const edits = this.getFileEditCount(filePath);
    const time = this.getTotalTimeSpent(filePath);

    // Normalize scores
    const maxInteractions = this.getMaxInteractionCount();
    const maxEdits = this.getMaxEditCount();
    const maxTime = this.getMaxTimeSpent();

    const interactionScore = maxInteractions > 0 ? interactions / maxInteractions : 0;
    const editScore = maxEdits > 0 ? edits / maxEdits : 0;
    const timeScore = maxTime > 0 ? time / maxTime : 0;

    return (interactionScore * 0.5) + (editScore * 0.3) + (timeScore * 0.2);
  }

  getMaxInteractionCount() {
    return Math.max(...Array.from(this.userModel.fileInteractions.values()).map(f => f.clickCount), 1);
  }

  getMaxEditCount() {
    return Math.max(...Array.from(this.userModel.fileInteractions.values()).map(f => f.editCount), 1);
  }

  getMaxTimeSpent() {
    return Math.max(...Array.from(this.userModel.fileInteractions.values()).map(f => f.totalTime), 1);
  }

  getLanguagePreferences() {
    const prefs = {};
    this.userModel.languagePreferences.forEach((data, lang) => {
      prefs[lang] = data;
    });
    return prefs;
  }

  getLanguagePreference(language) {
    return this.userModel.languagePreferences.get(language)?.usageScore || 0.5;
  }

  getRecentFiles(limit = 5) {
    return Array.from(this.userModel.fileInteractions.entries())
      .sort(([,a], [,b]) => b.lastAccess - a.lastAccess)
      .slice(0, limit)
      .map(([path, data]) => ({ path, ...data }));
  }

  getFrequentFiles(limit = 5) {
    return Array.from(this.userModel.fileInteractions.entries())
      .sort(([,a], [,b]) => b.clickCount - a.clickCount)
      .slice(0, limit)
      .map(([path, data]) => ({ path, ...data }));
  }

  getCoAccessedFiles(filePath) {
    // Find files that were accessed in the same session as the given file
    const coAccessed = {};
    const fileAccessTimes = [];
    
    // Get access times for the target file
    this.userModel.sessionData.interactions.forEach(interaction => {
      if (interaction.filePath === filePath && 
          (interaction.type === 'file_opened' || interaction.type === 'file_selected')) {
        fileAccessTimes.push(interaction.timestamp);
      }
    });

    // Find other files accessed within time windows
    fileAccessTimes.forEach(targetTime => {
      this.userModel.sessionData.interactions.forEach(interaction => {
        if (interaction.filePath && 
            interaction.filePath !== filePath &&
            Math.abs(interaction.timestamp - targetTime) < 300000) { // 5 minutes
          
          coAccessed[interaction.filePath] = (coAccessed[interaction.filePath] || 0) + 0.1;
        }
      });
    });

    return coAccessed;
  }

  getFileRelatedness(file1Path, file2Path) {
    const coAccessed = this.getCoAccessedFiles(file1Path);
    return coAccessed[file2Path] || 0;
  }

  getCurrentContext() {
    return {
      currentFiles: this.userModel.sessionData.currentFiles,
      recentInteractions: this.userModel.sessionData.interactions.slice(-10),
      sessionDuration: Date.now() - this.userModel.sessionData.startTime
    };
  }

  getLastUpdate() {
    return Math.max(...this.userModel.sessionData.interactions.map(i => i.timestamp), 0);
  }
}

export default new UserModelService();