// frontend/src/components/graph/NodeRenderer.jsx
import React from 'react';
import * as THREE from 'three';

export class NodeRenderer {
  constructor(algorithms, version) {
    this.algorithms = algorithms;
    this.version = version;
  }

  createNodeMaterial(node) {
    const color = this.algorithms?.coloring?.calculateNodeColor(node) || '#69b3ff';
    const temperature = this.algorithms?.layout?.getTemperature?.(node) || 0.5;
    
    return new THREE.MeshLambertMaterial({
      color: color,
      transparent: true,
      opacity: 0.7 + (temperature * 0.3),
      emissive: new THREE.Color(0x000000)
    });
  }

  calculateNodeSize(node) {
    if (this.version === 'personalized' && this.algorithms?.layout) {
      return this.algorithms.layout.calculateNodeSize(node);
    }
    // Random version - uniform size
    return 6 + Math.random() * 4;
  }

  getNodePosition(node, importanceScore) {
    if (this.version === 'personalized' && this.algorithms?.layout) {
      return this.algorithms.layout.calculateNodePosition(node, importanceScore);
    }
    // Random version - random positioning
    return {
      x: (Math.random() - 0.5) * 800,
      y: (Math.random() - 0.5) * 600,
      z: (Math.random() - 0.5) * 800
    };
  }

  updateNodeAppearance(nodeObject, node) {
    if (nodeObject?.userData?.sphere) {
      const sphere = nodeObject.userData.sphere;
      const material = this.createNodeMaterial(node);
      sphere.material = material;
    }
  }

  animateNodeSelection(nodeObject) {
    if (nodeObject?.userData?.sphere) {
      const sphere = nodeObject.userData.sphere;
      sphere.material.emissive.setHex(0x444444);
      
      // Pulsing animation
      const animate = () => {
        const time = Date.now() * 0.005;
        sphere.scale.setScalar(1 + Math.sin(time) * 0.1);
        requestAnimationFrame(animate);
      };
      animate();
    }
  }
}
