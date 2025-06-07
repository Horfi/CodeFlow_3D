// frontend/src/hooks/useGraph3D.js
import { useState, useEffect, useRef } from 'react';
import GraphService from '../services/GraphService';

export const useGraph3D = () => {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const unsubscribeRef = useRef(null);

  useEffect(() => {
    // Subscribe to graph updates
    unsubscribeRef.current = GraphService.subscribe((update) => {
      switch (update.type) {
        case 'graph_loaded':
          setGraphData(update.data);
          setLoading(false);
          setError(null);
          break;
        case 'graph_updated':
          setGraphData(update.data);
          break;
        case 'graph_error':
          setError(update.error);
          setLoading(false);
          break;
      }
    });

    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
    };
  }, []);

  const loadGraph = async (projectId) => {
    setLoading(true);
    setError(null);
    try {
      await GraphService.loadGraphData(projectId);
    } catch (err) {
      setError(err);
      setLoading(false);
    }
  };

  const updateGraph = (updates) => {
    GraphService.updateGraph(updates);
  };

  const selectNode = (node) => {
    setSelectedNode(node);
  };

  const hoverNode = (node) => {
    setHoveredNode(node);
  };

  const getConnectedNodes = (nodeId) => {
    return GraphService.getConnectedNodes(nodeId);
  };

  const filterNodes = (filterFn) => {
    return GraphService.filterNodes(filterFn);
  };

  return {
    graphData,
    loading,
    error,
    selectedNode,
    hoveredNode,
    loadGraph,
    updateGraph,
    selectNode,
    hoverNode,
    getConnectedNodes,
    filterNodes
  };
};