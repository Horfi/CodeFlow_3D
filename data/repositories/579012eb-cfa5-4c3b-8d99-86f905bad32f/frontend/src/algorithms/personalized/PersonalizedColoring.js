// frontend/src/algorithms/personalized/PersonalizedColoring.js
import { ColoringInterface } from '../factory/AlgorithmInterface';
import * as d3 from 'd3';

export class PersonalizedColoring extends ColoringInterface {
  constructor(userModel, config) {
    super(userModel, config);
    this.colorSchemes = this.initializeColorSchemes();
  }

  initializeColorSchemes() {
    return {
      temperature: d3.scaleSequential(d3.interpolateYlOrRd).domain([0, 1]),
      importance: d3.scaleSequential(d3.interpolateViridis).domain([0, 1]),
      language: d3.scaleOrdinal(d3.schemeCategory10),
      usage: d3.scaleSequential(d3.interpolateCool).domain([0, 1])
    };
  }

  calculateNodeColor(node) {
    if (!this.config.colorScheme.temperature) {
      return this.getRandomColor();
    }

    const temperature = this.calculateNodeTemperature(node);
    const importance = node.importance?.total_score || 0;
    const usage = this.getUserUsageScore(node);

    if (this.config.colorScheme.usage && usage > 0) {
      return this.blendColors(
        this.colorSchemes.temperature(temperature),
        this.colorSchemes.usage(usage),
        0.7
      );
    }

    if (this.config.colorScheme.importance) {
      return this.blendColors(
        this.colorSchemes.temperature(temperature),
        this.colorSchemes.importance(importance),
        0.6
      );
    }

    return this.colorSchemes.temperature(temperature);
  }

  calculateNodeTemperature(node) {
    if (!this.userModel) return 0.5;

    const interactions = this.userModel.getFileInteractionCount(node.path) || 0;
    const lastAccess = this.userModel.getLastAccessTime(node.path) || 0;
    const totalTime = this.userModel.getTotalTimeSpent(node.path) || 0;

    // Base interaction score
    const maxInteractions = this.userModel.getMaxInteractionCount() || 1;
    const interactionScore = Math.min(1, interactions / Math.max(1, maxInteractions * 0.1));

    // Recency boost
    const hoursSinceAccess = (Date.now() - lastAccess) / (1000 * 60 * 60);
    const recencyScore = Math.exp(-hoursSinceAccess / 12); // Exponential decay over 12 hours

    // Time investment
    const maxTime = this.userModel.getMaxTimeSpent() || 1;
    const timeScore = Math.min(1, totalTime / Math.max(1, maxTime * 0.1));

    // Language preference boost
    const languagePreference = this.userModel.getLanguagePreference(node.language) || 0.5;

    // Weighted combination
    const temperature = (
      interactionScore * 0.35 +
      recencyScore * 0.25 +
      timeScore * 0.25 +
      languagePreference * 0.15
    );

    return Math.min(1, Math.max(0, temperature));
  }

  getUserUsageScore(node) {
    if (!this.userModel) return 0;
    
    const editCount = this.userModel.getFileEditCount(node.path) || 0;
    const maxEdits = this.userModel.getMaxEditCount() || 1;
    
    return Math.min(1, editCount / maxEdits);
  }

  calculateEdgeColor(edge) {
    if (!this.config.colorScheme.temperature) {
      return '#ffffff40';
    }

    const sourceTemp = this.userModel?.getFileTemperature(edge.source.path) || 0.5;
    const targetTemp = this.userModel?.getFileTemperature(edge.target.path) || 0.5;
    const avgTemp = (sourceTemp + targetTemp) / 2;

    // Edge strength based on user co-access patterns
    const coAccessScore = this.userModel?.getFileRelatedness(
      edge.source.path, 
      edge.target.path
    ) || 0;

    const baseColor = this.colorSchemes.temperature(avgTemp);
    const opacity = 0.4 + (coAccessScore * 0.4);

    return this.hexToRgba(baseColor, opacity);
  }

  blendColors(color1, color2, ratio) {
    const rgb1 = d3.rgb(color1);
    const rgb2 = d3.rgb(color2);
    
    return d3.rgb(
      rgb1.r * ratio + rgb2.r * (1 - ratio),
      rgb1.g * ratio + rgb2.g * (1 - ratio),
      rgb1.b * ratio + rgb2.b * (1 - ratio)
    ).toString();
  }

  hexToRgba(hex, alpha) {
    const rgb = d3.rgb(hex);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
  }

  getRandomColor() {
    const colors = ['#69b3ff', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b'];
    return colors[Math.floor(Math.random() * colors.length)];
  }

  getColorScheme() {
    return {
      temperature: this.colorSchemes.temperature,
      importance: this.colorSchemes.importance,
      language: this.colorSchemes.language,
      usage: this.colorSchemes.usage
    };
  }
}
