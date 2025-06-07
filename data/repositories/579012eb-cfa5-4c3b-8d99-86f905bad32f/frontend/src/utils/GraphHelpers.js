// frontend/src/utils/GraphHelpers.js
import * as THREE from 'three';

export class GraphHelpers {
  static calculateDistance(pos1, pos2) {
    const dx = pos1.x - pos2.x;
    const dy = pos1.y - pos2.y;
    const dz = pos1.z - pos2.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  static normalizeVector(vector) {
    const length = Math.sqrt(vector.x * vector.x + vector.y * vector.y + vector.z * vector.z);
    if (length === 0) return { x: 0, y: 0, z: 0 };
    return {
      x: vector.x / length,
      y: vector.y / length,
      z: vector.z / length
    };
  }

  static interpolatePosition(start, end, factor) {
    return {
      x: start.x + (end.x - start.x) * factor,
      y: start.y + (end.y - start.y) * factor,
      z: start.z + (end.z - start.z) * factor
    };
  }

  static createSpherePositions(count, radius = 200) {
    const positions = [];
    const goldenAngle = Math.PI * (3 - Math.sqrt(5));
    
    for (let i = 0; i < count; i++) {
      const y = 1 - (i / (count - 1)) * 2;
      const radiusAtY = Math.sqrt(1 - y * y);
      const theta = goldenAngle * i;
      
      positions.push({
        x: Math.cos(theta) * radiusAtY * radius,
        y: y * radius,
        z: Math.sin(theta) * radiusAtY * radius
      });
    }
    
    return positions;
  }

  static calculateBoundingBox(nodes) {
    if (!nodes || nodes.length === 0) {
      return { min: { x: 0, y: 0, z: 0 }, max: { x: 0, y: 0, z: 0 } };
    }

    const min = { x: Infinity, y: Infinity, z: Infinity };
    const max = { x: -Infinity, y: -Infinity, z: -Infinity };

    nodes.forEach(node => {
      if (node.x < min.x) min.x = node.x;
      if (node.y < min.y) min.y = node.y;
      if (node.z < min.z) min.z = node.z;
      if (node.x > max.x) max.x = node.x;
      if (node.y > max.y) max.y = node.y;
      if (node.z > max.z) max.z = node.z;
    });

    return { min, max };
  }

  static fitCameraToNodes(camera, nodes, padding = 1.5) {
    const bbox = this.calculateBoundingBox(nodes);
    const center = {
      x: (bbox.min.x + bbox.max.x) / 2,
      y: (bbox.min.y + bbox.max.y) / 2,
      z: (bbox.min.z + bbox.max.z) / 2
    };

    const size = Math.max(
      bbox.max.x - bbox.min.x,
      bbox.max.y - bbox.min.y,
      bbox.max.z - bbox.min.z
    );

    const distance = size * padding;
    camera.position.set(center.x, center.y, center.z + distance);
    camera.lookAt(center.x, center.y, center.z);
  }

  static createTextTexture(text, options = {}) {
    const {
      fontSize = 24,
      fontFamily = 'Arial',
      color = '#ffffff',
      backgroundColor = 'transparent',
      padding = 10
    } = options;

    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    context.font = `${fontSize}px ${fontFamily}`;
    const textMetrics = context.measureText(text);
    
    canvas.width = textMetrics.width + padding * 2;
    canvas.height = fontSize + padding * 2;
    
    if (backgroundColor !== 'transparent') {
      context.fillStyle = backgroundColor;
      context.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    context.font = `${fontSize}px ${fontFamily}`;
    context.fillStyle = color;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);
    
    return new THREE.CanvasTexture(canvas);
  }

  static animateValue(from, to, duration, callback, easing = 'easeInOut') {
    const startTime = Date.now();
    
    const easingFunctions = {
      linear: t => t,
      easeIn: t => t * t,
      easeOut: t => t * (2 - t),
      easeInOut: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t
    };
    
    const easingFn = easingFunctions[easing] || easingFunctions.easeInOut;
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easingFn(progress);
      
      const currentValue = from + (to - from) * easedProgress;
      callback(currentValue);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    animate();
  }
}