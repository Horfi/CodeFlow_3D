// frontend/src/algorithms/random/RandomColoring.js
import { ColoringInterface } from '../factory/AlgorithmInterface';

export class RandomColoring extends ColoringInterface {
  constructor(config) {
    super(null, config);
    this.colorPalette = [
      '#69b3ff', '#ff6b6b', '#4ecdc4', '#45b7d1', 
      '#f9ca24', '#f0932b', '#eb4d4b', '#6c5ce7',
      '#a29bfe', '#fd79a8', '#e17055', '#00b894'
    ];
  }

  calculateNodeColor(node) {
    // Consistent random color per node
    const colorIndex = this.getConsistentIndex(node.id, this.colorPalette.length);
    return this.colorPalette[colorIndex];
  }

  calculateEdgeColor(edge) {
    // Fixed edge color for random version
    return '#ffffff40';
  }

  getConsistentIndex(seed, arrayLength) {
    let hash = 0;
    for (let i = 0; i < seed.length; i++) {
      const char = seed.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash) % arrayLength;
  }

  getColorScheme() {
    return {
      random: this.colorPalette,
      default: '#69b3ff'
    };
  }
}

