// frontend/src/services/GraphService.js
import APIService from './APIService';

class GraphService {
  constructor() {
    this.currentGraph = null;
    this.subscribers = [];
  }

  subscribe(callback) {
    this.subscribers.push(callback);
    return () => {
      this.subscribers = this.subscribers.filter(cb => cb !== callback);
    };
  }

  notify(data) {
    this.subscribers.forEach(callback => callback(data));
  }

  async loadGraphData(projectId) {
    try {
      const graphData = await APIService.getGraphData(projectId);
      this.currentGraph = graphData;
      this.notify({ type: 'graph_loaded', data: graphData });
      return graphData;
    } catch (error) {
      console.error('Failed to load graph data:', error);
      throw error;
    }
  }

  async updateGraph(updates) {
    if (!this.currentGraph) return;

    this.currentGraph = { ...this.currentGraph, ...updates };
    this.notify({ type: 'graph_updated', data: this.currentGraph });
  }

  getCurrentGraph() {
    return this.currentGraph;
  }

  getNodeById(nodeId) {
    return this.currentGraph?.nodes?.find(node => node.id === nodeId);
  }

  getNodesByLanguage(language) {
    return this.currentGraph?.nodes?.filter(node => node.language === language) || [];
  }

  getConnectedNodes(nodeId) {
    if (!this.currentGraph) return [];

    const connectedNodes = [];
    const edges = this.currentGraph.edges || [];

    edges.forEach(edge => {
      if (edge.source === nodeId || edge.source.id === nodeId) {
        const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
        const targetNode = this.getNodeById(targetId);
        if (targetNode) connectedNodes.push(targetNode);
      }
      if (edge.target === nodeId || edge.target.id === nodeId) {
        const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
        const sourceNode = this.getNodeById(sourceId);
        if (sourceNode) connectedNodes.push(sourceNode);
      }
    });

    return connectedNodes;
  }

  filterNodes(filterFn) {
    if (!this.currentGraph) return [];
    return this.currentGraph.nodes.filter(filterFn);
  }

  searchNodes(query) {
    if (!this.currentGraph || !query) return [];
    
    const lowerQuery = query.toLowerCase();
    return this.currentGraph.nodes.filter(node =>
      node.name.toLowerCase().includes(lowerQuery) ||
      node.path.toLowerCase().includes(lowerQuery)
    );
  }
}

export default new GraphService();
