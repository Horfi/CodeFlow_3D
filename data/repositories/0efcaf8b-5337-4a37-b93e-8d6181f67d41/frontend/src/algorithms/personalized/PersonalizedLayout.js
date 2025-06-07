// frontend/src/algorithms/personalized/PersonalizedLayout.js
import { LayoutInterface } from '../factory/AlgorithmInterface';
import * as d3 from 'd3';

export class PersonalizedLayout extends LayoutInterface {
  constructor(userModel, config) {
    super(userModel, config);
    this.importanceCache = new Map();
    this.positionCache = new Map();
  }

  calculateNodePosition(node, importanceScores) {
    const cacheKey = `${node.id}_${this.userModel?.getLastUpdate() || 0}`;
    if (this.positionCache.has(cacheKey)) {
      return this.positionCache.get(cacheKey);
    }

    const importance = this.getPersonalizedImportance(node, importanceScores);
    const userPreference = this.userModel?.getFilePreference(node.path) || 0.5;
    
    // Central positioning for high importance files
    const radius = this.calculateDistanceFromCenter(importance, userPreference);
    const angle = this.calculateOptimalAngle(node, importanceScores);
    const height = this.calculateVerticalPosition(node, importance);

    const position = {
      x: radius * Math.cos(angle),
      y: height,
      z: radius * Math.sin(angle)
    };

    this.positionCache.set(cacheKey, position);
    return position;
  }

  calculateDistanceFromCenter(importance, userPreference) {
    // Combine graph importance with user preference
    const combinedScore = (importance * 0.6) + (userPreference * 0.4);
    
    // Most important files closer to center
    const minRadius = 50;
    const maxRadius = 400;
    return maxRadius - (combinedScore * (maxRadius - minRadius));
  }

  calculateOptimalAngle(node, importanceScores) {
    // Use golden angle for even distribution
    const goldenAngle = Math.PI * (3 - Math.sqrt(5));
    const rank = importanceScores[node.id]?.rank || 0;
    return rank * goldenAngle;
  }

  calculateVerticalPosition(node, importance) {
    // Spread nodes vertically based on folder structure
    const folderLevel = (node.path.match(/\//g) || []).length;
    const baseHeight = folderLevel * 30;
    
    // Add some randomness but keep important files more centered
    const randomOffset = (Math.random() - 0.5) * 100 * (1 - importance);
    
    return baseHeight + randomOffset;
  }

  calculateNodeSize(node) {
    const baseSize = 6;
    const maxSize = 20;
    
    // Size based on user interaction frequency
    const userInteractions = this.userModel?.getFileInteractionCount(node.path) || 0;
    const maxInteractions = this.userModel?.getMaxInteractionCount() || 1;
    const interactionScore = userInteractions / maxInteractions;
    
    // Size based on graph centrality
    const importance = this.getImportanceScore(node);
    
    // Combine factors
    const sizeFactor = (interactionScore * 0.7) + (importance.total_score * 0.3);
    
    return baseSize + (sizeFactor * (maxSize - baseSize));
  }

  getPersonalizedImportance(node, importanceScores) {
    const graphImportance = importanceScores[node.id]?.total_score || 0;
    const userImportance = this.userModel?.getFileImportance(node.path) || 0;
    
    // Weighted combination favoring user behavior over graph structure
    return (graphImportance * 0.4) + (userImportance * 0.6);
  }

  applyLayout(forceGraph) {
    if (!forceGraph || !this.config.enableSmartLayout) return;

    const simulation = forceGraph.d3Force('simulation');
    if (!simulation) return;

    // Enhance forces based on user preferences
    simulation
      .force('link', d3.forceLink()
        .distance(link => this.calculateLinkDistance(link))
        .strength(link => this.calculateLinkStrength(link))
      )
      .force('charge', d3.forceManyBody()
        .strength(node => this.calculateNodeCharge(node))
      )
      .force('center', d3.forceCenter(0, 0)
        .strength(this.config.layoutPhysics.gravityStrength)
      )
      .force('collision', d3.forceCollide()
        .radius(node => this.calculateNodeSize(node) + 5)
      );

    // Add custom forces for user preferences
    simulation.force('userPreference', this.createUserPreferenceForce());
  }

  calculateLinkDistance(link) {
    const baseDistance = 100;
    
    // Shorter distances for frequently accessed pairs
    const sourceInteractions = this.userModel?.getFileInteractionCount(link.source.path) || 0;
    const targetInteractions = this.userModel?.getFileInteractionCount(link.target.path) || 0;
    
    if (sourceInteractions > 0 && targetInteractions > 0) {
      return baseDistance * 0.7; // Bring related files closer
    }
    
    return baseDistance;
  }

  calculateLinkStrength(link) {
    const baseStrength = 0.5;
    
    // Stronger connections for user-related files
    const userRelatedness = this.userModel?.getFileRelatedness(
      link.source.path, 
      link.target.path
    ) || 0;
    
    return baseStrength + (userRelatedness * 0.3);
  }

  calculateNodeCharge(node) {
    const baseCharge = -300;
    
    // Important nodes repel more strongly
    const importance = this.getImportanceScore(node);
    const chargeFactor = 1 + (importance.total_score * 0.5);
    
    return baseCharge * chargeFactor;
  }

  createUserPreferenceForce() {
    return (alpha) => {
      if (!this.userModel) return;
      
      // Pull frequently used files toward user's preferred area
      const preferredFiles = this.userModel.getTopFiles(10);
      
      preferredFiles.forEach(file => {
        const node = this.findNodeById(file.path);
        if (node) {
          // Pull toward a preferred region (e.g., lower right quadrant)
          const targetX = 100;
          const targetY = -50;
          
          node.vx += (targetX - node.x) * alpha * 0.1;
          node.vy += (targetY - node.y) * alpha * 0.1;
        }
      });
    };
  }

  processGraphData(data) {
    if (!data || !data.nodes) return data;

    // Calculate importance scores using PageRank-style algorithm
    const importanceScores = this.calculateImportanceScores(data);
    
    // Enhance nodes with personalized data
    const enhancedNodes = data.nodes.map(node => ({
      ...node,
      importance: importanceScores[node.id] || { total_score: 0, rank: 999 },
      userStats: this.userModel?.getFileStats(node.path) || {},
      temperature: this.calculateTemperature(node),
      personalizedScore: this.getPersonalizedImportance(node, importanceScores)
    }));

    return {
      ...data,
      nodes: enhancedNodes,
      importanceScores
    };
  }

  calculateImportanceScores(data) {
    const nodes = data.nodes || [];
    const links = data.edges || data.links || [];
    
    // Build adjacency matrix for PageRank
    const nodeMap = new Map();
    nodes.forEach((node, index) => {
      nodeMap.set(node.id, index);
    });

    const matrix = Array(nodes.length).fill().map(() => Array(nodes.length).fill(0));
    
    links.forEach(link => {
      const sourceIndex = nodeMap.get(link.source.id || link.source);
      const targetIndex = nodeMap.get(link.target.id || link.target);
      
      if (sourceIndex !== undefined && targetIndex !== undefined) {
        matrix[sourceIndex][targetIndex] = 1;
      }
    });

    // Calculate PageRank scores
    const pageRankScores = this.calculatePageRank(matrix);
    
    // Calculate other centrality measures
    const betweennessScores = this.calculateBetweennessCentrality(data);
    const degreeScores = this.calculateDegreeCentrality(data);

    const scores = {};
    nodes.forEach((node, index) => {
      const totalScore = (
        pageRankScores[index] * 0.5 +
        betweennessScores[index] * 0.3 +
        degreeScores[index] * 0.2
      );
      
      scores[node.id] = {
        total_score: totalScore,
        pagerank: pageRankScores[index],
        betweenness: betweennessScores[index],
        degree: degreeScores[index],
        rank: 0 // Will be assigned after sorting
      };
    });

    // Assign ranks
    const sortedNodes = Object.entries(scores)
      .sort(([,a], [,b]) => b.total_score - a.total_score);
    
    sortedNodes.forEach(([nodeId, scoreData], index) => {
      scores[nodeId].rank = index + 1;
    });

    return scores;
  }

  calculatePageRank(matrix, damping = 0.85, iterations = 100) {
    const n = matrix.length;
    if (n === 0) return [];

    let ranks = new Array(n).fill(1 / n);
    
    for (let iter = 0; iter < iterations; iter++) {
      const newRanks = new Array(n).fill((1 - damping) / n);
      
      for (let i = 0; i < n; i++) {
        let linkSum = 0;
        for (let j = 0; j < n; j++) {
          if (matrix[j][i] > 0) {
            const outLinks = matrix[j].reduce((sum, val) => sum + val, 0);
            if (outLinks > 0) {
              linkSum += ranks[j] / outLinks;
            }
          }
        }
        newRanks[i] += damping * linkSum;
      }
      
      ranks = newRanks;
    }
    
    return ranks;
  }

  calculateBetweennessCentrality(data) {
    // Simplified betweenness centrality calculation
    const nodes = data.nodes || [];
    return nodes.map(() => Math.random() * 0.1); // Placeholder
  }

  calculateDegreeCentrality(data) {
    const nodes = data.nodes || [];
    const links = data.edges || data.links || [];
    
    const degrees = new Map();
    nodes.forEach(node => degrees.set(node.id, 0));
    
    links.forEach(link => {
      const sourceId = link.source.id || link.source;
      const targetId = link.target.id || link.target;
      
      degrees.set(sourceId, (degrees.get(sourceId) || 0) + 1);
      degrees.set(targetId, (degrees.get(targetId) || 0) + 1);
    });
    
    const maxDegree = Math.max(...degrees.values()) || 1;
    
    return nodes.map(node => (degrees.get(node.id) || 0) / maxDegree);
  }

  calculateTemperature(node) {
    if (!this.userModel) return 0.5;
    
    const interactions = this.userModel.getFileInteractionCount(node.path) || 0;
    const lastAccess = this.userModel.getLastAccessTime(node.path) || 0;
    const totalTime = this.userModel.getTotalTimeSpent(node.path) || 0;
    
    // Recency factor (0-1)
    const hoursSinceAccess = (Date.now() - lastAccess) / (1000 * 60 * 60);
    const recencyScore = Math.max(0, 1 - (hoursSinceAccess / 24)); // Decay over 24 hours
    
    // Interaction frequency factor (0-1)
    const maxInteractions = this.userModel.getMaxInteractionCount() || 1;
    const frequencyScore = Math.min(1, interactions / maxInteractions);
    
    // Time investment factor (0-1)
    const maxTime = this.userModel.getMaxTimeSpent() || 1;
    const timeScore = Math.min(1, totalTime / maxTime);
    
    // Combined temperature (weighted average)
    return (recencyScore * 0.4) + (frequencyScore * 0.4) + (timeScore * 0.2);
  }

  getImportanceScore(node) {
    return this.importanceCache.get(node.id) || { total_score: 0, rank: 999 };
  }

  findNodeById(id) {
    // This would be implemented to find node in the current graph
    return null; // Placeholder
  }
}
