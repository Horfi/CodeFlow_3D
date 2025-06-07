// frontend/src/components/graph/Graph3DCanvas.jsx
import React, { useRef, useEffect, useState } from 'react';
import ForceGraph3D from '3d-force-graph';
import * as THREE from 'three';
import GraphControls from './GraphControls';
import GraphTooltip from './GraphTooltip';

const Graph3DCanvas = ({ 
  algorithms, 
  projectData, 
  version, 
  onFileSelect, 
  selectedFile 
}) => {
  const containerRef = useRef(null);
  const graphRef = useRef(null);
  const [tooltipData, setTooltipData] = useState(null);
  const [graphSettings, setGraphSettings] = useState({
    linkDistance: 100,
    nodeSize: 8,
    showLabels: true,
    enablePhysics: true
  });

  useEffect(() => {
    if (containerRef.current && projectData) {
      initializeGraph();
    }
    return () => {
      if (graphRef.current) {
        graphRef.current._destructor?.();
      }
    };
  }, []);

  useEffect(() => {
    if (graphRef.current && projectData) {
      updateGraphData();
    }
  }, [projectData, algorithms, version]);

  const initializeGraph = () => {
    const graph = ForceGraph3D()(containerRef.current)
      .backgroundColor('#0a0a0a')
      .showNavInfo(false)
      .enableNodeDrag(true)
      .enablePointerInteraction(true);

    // Node appearance
    graph
      .nodeLabel('')
      .nodeVal(node => algorithms?.layout?.calculateNodeSize(node) || 8)
      .nodeColor(node => algorithms?.coloring?.calculateNodeColor(node) || '#69b3ff')
      .nodeThreeObject(node => createNodeObject(node))
      .nodeThreeObjectExtend(true);

    // Link appearance  
    graph
      .linkColor(link => algorithms?.coloring?.calculateEdgeColor(link) || '#ffffff40')
      .linkWidth(2)
      .linkOpacity(0.6)
      .linkDirectionalArrowLength(6)
      .linkDirectionalArrowRelPos(0.8);

    // Interaction handlers
    graph
      .onNodeClick(handleNodeClick)
      .onNodeHover(handleNodeHover)
      .onNodeDragEnd(handleNodeDragEnd)
      .onBackgroundClick(() => setTooltipData(null));

    // Physics settings
    graph
      .d3Force('link').distance(graphSettings.linkDistance)
      .d3Force('charge').strength(-300)
      .d3Force('center').strength(0.1);

    graphRef.current = graph;
  };

  const createNodeObject = (node) => {
    const group = new THREE.Group();
    
    // Main sphere
    const sphereGeometry = new THREE.SphereGeometry(
      algorithms?.layout?.calculateNodeSize(node) || 8, 
      16, 
      16
    );
    
    const sphereMaterial = new THREE.MeshLambertMaterial({
      color: algorithms?.coloring?.calculateNodeColor(node) || '#69b3ff',
      transparent: true,
      opacity: 0.8
    });
    
    const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    group.add(sphere);

    // File name label
    if (graphSettings.showLabels) {
      const label = createTextSprite(node.name, '#ffffff');
      label.position.set(0, 15, 0);
      label.scale.set(0.5, 0.5, 0.5);
      group.add(label);
    }

    // Folder badge
    const folderBadge = createFolderBadge(node);
    if (folderBadge) {
      folderBadge.position.set(8, 8, 0);
      group.add(folderBadge);
    }

    // Importance indicator
    const importance = algorithms?.layout?.getImportanceScore?.(node);
    if (importance && importance > 0.8) {
      const ring = createImportanceRing();
      ring.position.copy(sphere.position);
      group.add(ring);
    }

    group.userData = { 
      nodeData: node,
      originalColor: sphereMaterial.color.clone(),
      sphere: sphere
    };

    return group;
  };

  const createTextSprite = (text, color = '#ffffff') => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    
    context.fillStyle = color;
    context.font = 'bold 20px Arial';
    context.textAlign = 'center';
    context.fillText(text, 128, 40);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
    return new THREE.Sprite(spriteMaterial);
  };

  const createFolderBadge = (node) => {
    const folderPath = node.path.split('/').slice(0, -1).join('/');
    const badge = getFolderBadgeEmoji(folderPath);
    
    if (badge) {
      return createTextSprite(badge, '#ffff00');
    }
    return null;
  };

  const createImportanceRing = () => {
    const ringGeometry = new THREE.RingGeometry(12, 15, 16);
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: '#ffd700',
      transparent: true,
      opacity: 0.7,
      side: THREE.DoubleSide
    });
    return new THREE.Mesh(ringGeometry, ringMaterial);
  };

  const getFolderBadgeEmoji = (folderPath) => {
    const folderIcons = {
      'src': '🟢',
      'test': '🔵', 
      'tests': '🔵',
      'docs': '📚',
      'config': '⚙️',
      'utils': '🛠️',
      'models': '🏗️',
      'api': '🌐',
      'components': '🧩',
      'services': '🔧',
      'lib': '📚',
      'assets': '🎨'
    };
    
    const folder = folderPath.split('/')[0];
    return folderIcons[folder] || null;
  };

  const updateGraphData = () => {
    if (!graphRef.current || !projectData) return;

    const graphData = algorithms?.layout?.processGraphData?.(projectData) || {
      nodes: projectData.nodes || [],
      links: projectData.edges || []
    };

    graphRef.current.graphData(graphData);
    
    // Apply layout algorithm
    if (algorithms?.layout?.applyLayout) {
      setTimeout(() => {
        algorithms.layout.applyLayout(graphRef.current);
      }, 1000);
    }
  };

  const handleNodeClick = (node, event) => {
    if (node && onFileSelect) {
      onFileSelect(node);
      
      // Visual feedback
      highlightNode(node);
      
      // Track interaction
      if (algorithms?.interactionHandler) {
        algorithms.interactionHandler.recordInteraction({
          type: 'node_click',
          filePath: node.path,
          timestamp: Date.now()
        });
      }
    }
  };

  const handleNodeHover = (node) => {
    if (node) {
      setTooltipData({
        node,
        position: { x: 0, y: 0 } // Will be updated by tooltip component
      });
    } else {
      setTooltipData(null);
    }
  };

  const handleNodeDragEnd = (node) => {
    if (node && algorithms?.interactionHandler) {
      algorithms.interactionHandler.recordInteraction({
        type: 'node_drag',
        filePath: node.path,
        timestamp: Date.now()
      });
    }
  };

  const highlightNode = (targetNode) => {
    // Reset all nodes
    if (graphRef.current) {
      graphRef.current.nodeThreeObject().children.forEach(group => {
        if (group.userData?.sphere) {
          group.userData.sphere.material.emissive.setHex(0x000000);
          group.userData.sphere.material.opacity = 0.8;
        }
      });

      // Highlight selected node
      const nodeObj = graphRef.current.nodeThreeObject(targetNode);
      if (nodeObj?.userData?.sphere) {
        nodeObj.userData.sphere.material.emissive.setHex(0x444444);
        nodeObj.userData.sphere.material.opacity = 1.0;
      }
    }
  };

  const handleResetLayout = () => {
    if (graphRef.current) {
      graphRef.current.d3ReheatSimulation();
    }
  };

  const handleResetColors = () => {
    updateGraphData();
  };

  const handleTogglePhysics = () => {
    setGraphSettings(prev => ({
      ...prev,
      enablePhysics: !prev.enablePhysics
    }));
    
    if (graphRef.current) {
      if (graphSettings.enablePhysics) {
        graphRef.current.d3Force('link', null);
        graphRef.current.d3Force('charge', null);
      } else {
        graphRef.current
          .d3Force('link').distance(graphSettings.linkDistance)
          .d3Force('charge').strength(-300);
      }
    }
  };

  return (
    <div className="graph-canvas-container">
      <div ref={containerRef} className="graph-canvas" />
      
      <GraphControls
        onResetLayout={handleResetLayout}
        onResetColors={handleResetColors}
        onTogglePhysics={handleTogglePhysics}
        settings={graphSettings}
        onSettingsChange={setGraphSettings}
      />
      
      {tooltipData && (
        <GraphTooltip
          data={tooltipData}
          version={version}
          algorithms={algorithms}
        />
      )}
      
      <div className="graph-info">
        <div className="node-count">
          📊 Nodes: {projectData?.nodes?.length || 0}
        </div>
        <div className="edge-count">
          🔗 Edges: {projectData?.edges?.length || 0}
        </div>
        <div className="version-indicator">
          🎯 Mode: {version === 'personalized' ? 'Personalized' : 'Random'}
        </div>
      </div>
    </div>
  );
};

export default Graph3DCanvas;