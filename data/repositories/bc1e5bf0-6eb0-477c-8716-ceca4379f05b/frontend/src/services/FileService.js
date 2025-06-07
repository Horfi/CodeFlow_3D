// frontend/src/services/FileService.js
import APIService from './APIService';

class FileService {
  constructor() {
    this.fileCache = new Map();
    this.contentCache = new Map();
  }

  async getFileContent(filePath) {
    // Check cache first
    if (this.contentCache.has(filePath)) {
      return this.contentCache.get(filePath);
    }

    try {
      const content = await APIService.getFileContent(filePath);
      this.contentCache.set(filePath, content);
      return content;
    } catch (error) {
      console.error(`Failed to load file content: ${filePath}`, error);
      throw error;
    }
  }

  async saveFileContent(filePath, content) {
    try {
      await APIService.saveFileContent(filePath, content);
      // Update cache
      this.contentCache.set(filePath, content);
      return true;
    } catch (error) {
      console.error(`Failed to save file: ${filePath}`, error);
      throw error;
    }
  }

  async getFileDependencies(filePath) {
    try {
      return await APIService.getFileDependencies(filePath);
    } catch (error) {
      console.error(`Failed to get dependencies for: ${filePath}`, error);
      return [];
    }
  }

  async getFileDependents(filePath) {
    try {
      return await APIService.getFileDependents(filePath);
    } catch (error) {
      console.error(`Failed to get dependents for: ${filePath}`, error);
      return [];
    }
  }

  detectLanguage(filePath) {
    const ext = filePath.split('.').pop()?.toLowerCase();
    const languageMap = {
      'js': 'JavaScript',
      'jsx': 'JavaScript',
      'ts': 'TypeScript',
      'tsx': 'TypeScript',
      'py': 'Python',
      'java': 'Java',
      'cpp': 'C++',
      'c': 'C',
      'html': 'HTML',
      'css': 'CSS',
      'scss': 'SCSS',
      'json': 'JSON',
      'xml': 'XML',
      'yml': 'YAML',
      'yaml': 'YAML',
      'md': 'Markdown',
      'txt': 'Text'
    };
    return languageMap[ext] || 'Unknown';
  }

  getFileIcon(filePath) {
    const language = this.detectLanguage(filePath);
    const icons = {
      'JavaScript': '🟨',
      'TypeScript': '🔷',
      'Python': '🐍',
      'Java': '☕',
      'C++': '⚡',
      'C': '⚡',
      'HTML': '🌐',
      'CSS': '🎨',
      'SCSS': '🎨',
      'JSON': '📋',
      'XML': '📋',
      'YAML': '⚙️',
      'Markdown': '📝',
      'Text': '📄'
    };
    return icons[language] || '📄';
  }

  clearCache() {
    this.fileCache.clear();
    this.contentCache.clear();
  }

  getCacheSize() {
    return {
      files: this.fileCache.size,
      content: this.contentCache.size
    };
  }
}

export default new FileService();