// frontend/src/services/APIService.js
class APIService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
    this.timeout = 30000; // 30 seconds
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);
      
      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return await response.text();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Repository Management
  async analyzeRepository(gitUrl, version = 'personalized') {
    return this.request('/repository/analyze', {
      method: 'POST',
      body: JSON.stringify({ gitUrl, version })
    });
  }

  async getProjectData(projectId) {
    return this.request(`/project/${projectId}`);
  }

  async getRepositoryStatus(projectId) {
    return this.request(`/repository/${projectId}/status`);
  }

  // File Operations
  async getFileContent(filePath) {
    return this.request(`/files/${encodeURIComponent(filePath)}`);
  }

  async saveFileContent(filePath, content) {
    return this.request(`/files/${encodeURIComponent(filePath)}`, {
      method: 'PUT',
      body: JSON.stringify({ content })
    });
  }

  async getFileDependencies(filePath) {
    return this.request(`/files/${encodeURIComponent(filePath)}/dependencies`);
  }

  async getFileDependents(filePath) {
    return this.request(`/files/${encodeURIComponent(filePath)}/dependents`);
  }

  // Graph Operations
  async getGraphData(projectId) {
    return this.request(`/graph/${projectId}`);
  }

  async getCentralityData(projectId) {
    return this.request(`/graph/${projectId}/centrality`);
  }

  async updateGraphData(projectId, graphData) {
    return this.request(`/graph/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(graphData)
    });
  }

  // User Model and Analytics
  async getUserModel() {
    return this.request('/user/model');
  }

  async updateUserModel(modelData) {
    return this.request('/user/model', {
      method: 'PUT',
      body: JSON.stringify(modelData)
    });
  }

  async trackInteraction(interaction) {
    return this.request('/analytics/interaction', {
      method: 'POST',
      body: JSON.stringify(interaction)
    });
  }

  async getAnalytics(timeRange = '7d') {
    return this.request(`/analytics?range=${timeRange}`);
  }

  // Bookmarks
  async getBookmarks() {
    return this.request('/bookmarks');
  }

  async addBookmark(filePath) {
    return this.request('/bookmarks', {
      method: 'POST',
      body: JSON.stringify({ filePath })
    });
  }

  async removeBookmark(filePath) {
    return this.request(`/bookmarks/${encodeURIComponent(filePath)}`, {
      method: 'DELETE'
    });
  }

  async clearBookmarks() {
    return this.request('/bookmarks', {
      method: 'DELETE'
    });
  }

  // Search
  async search(query, projectId) {
    return this.request('/search', {
      method: 'POST',
      body: JSON.stringify({ query, projectId })
    });
  }

  // Suggestions
  async getSuggestions(currentFile, context = {}) {
    return this.request('/suggestions', {
      method: 'POST',
      body: JSON.stringify({ currentFile, context })
    });
  }
}

export default new APIService();