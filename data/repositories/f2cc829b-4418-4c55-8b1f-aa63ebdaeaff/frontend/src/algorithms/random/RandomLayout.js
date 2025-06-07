// frontend/src/algorithms/random/RandomLayout.js
import { LayoutInterface } from '../factory/AlgorithmInterface';

export class RandomLayout extends LayoutInterface {
  constructor(config) {
    super(null, config);
    this.randomSeed = Math.random();
  }

  calculateNodePosition(node, importanceScores) {
    // Pure random positioning - no personalization
    const seededRandom = this.getSeededRandom(node.id);
    
    return {
      x: (seededRandom() - 0.5) * 800,
      y: (seededRandom() - 0.5) * 600,
      z: (seededRandom() - 0.5) * 800
    };
  }

  calculateNodeSize(node) {
    // Random size between 6-16, consistent per node
    const seededRandom = this.getSeededRandom(node.id);
    return 6 + seededRandom() * 10;
  }

  getSeededRandom(seed) {
    // Simple seeded random to ensure consistency
    let hash = 0;
    for (let i = 0; i < seed.length; i++) {
      const char = seed.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    
    return () => {
      hash = (hash * 9301 + 49297) % 233280;
      return hash / 233280;
    };
  }

  applyLayout(forceGraph) {
    if (!forceGraph) return;

    // Apply standard force layout without personalization
    const simulation = forceGraph.d3Force('simulation');
    if (simulation) {
      simulation
        .force('link', forceGraph.d3Force('link').distance(this.config.layoutPhysics.linkDistance || 100))
        .force('charge', forceGraph.d3Force('charge').strength(this.config.layoutPhysics.chargeStrength || -300))
        .force('center', forceGraph.d3Force('center').strength(this.config.layoutPhysics.gravityStrength || 0.05));
    }
  }

  processGraphData(data) {
    if (!data || !data.nodes) return data;

    // Add random importance scores
    const enhancedNodes = data.nodes.map(node => {
      const seededRandom = this.getSeededRandom(node.id);
      return {
        ...node,
        importance: {
          total_score: seededRandom(),
          rank: Math.floor(seededRandom() * data.nodes.length) + 1
        },
        temperature: seededRandom(),
        personalizedScore: seededRandom()
      };
    });

    return {
      ...data,
      nodes: enhancedNodes
    };
  }

  getImportanceScore(node) {
    const seededRandom = this.getSeededRandom(node.id);
    return {
      total_score: seededRandom(),
      rank: Math.floor(seededRandom() * 1000) + 1
    };
  }

  calculateTemperature(node) {
    // Random temperature
    const seededRandom = this.getSeededRandom(node.id);
    return seededRandom();
  }
}
