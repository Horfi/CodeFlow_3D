// frontend/src/components/graph/EdgeRenderer.jsx
import React from 'react';
import * as THREE from 'three';

export class EdgeRenderer {
  constructor(algorithms, version) {
    this.algorithms = algorithms;
    this.version = version;
  }

  createEdgeMaterial(edge) {
    if (this.version === 'personalized' && this.algorithms?.coloring) {
      const color = this.algorithms.coloring.calculateEdgeColor(edge);
      return new THREE.LineBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.6
      });
    }
    
    // Random version - uniform gray
    return new THREE.LineBasicMaterial({
      color: '#ffffff40',
      transparent: true,
      opacity: 0.4
    });
  }

  calculateEdgeWidth(edge) {
    if (this.version === 'personalized' && edge.strength) {
      return Math.max(1, edge.strength * 5);
    }
    return 2; // Default width for random version
  }

  createCurvedEdge(sourcePos, targetPos) {
    const curve = new THREE.QuadraticBezierCurve3(
      new THREE.Vector3(sourcePos.x, sourcePos.y, sourcePos.z),
      new THREE.Vector3(
        (sourcePos.x + targetPos.x) / 2,
        (sourcePos.y + targetPos.y) / 2 + 30,
        (sourcePos.z + targetPos.z) / 2
      ),
      new THREE.Vector3(targetPos.x, targetPos.y, targetPos.z)
    );

    const points = curve.getPoints(20);
    return new THREE.BufferGeometry().setFromPoints(points);
  }

  highlightEdge(edgeObject, highlight = true) {
    if (edgeObject?.material) {
      edgeObject.material.opacity = highlight ? 1.0 : 0.6;
      edgeObject.material.color.setHex(highlight ? 0xffd700 : 0xffffff);
    }
  }
}
