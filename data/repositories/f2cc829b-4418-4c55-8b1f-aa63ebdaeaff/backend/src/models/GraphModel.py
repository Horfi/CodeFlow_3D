# backend/src/models/GraphModel.py
from typing import Dict, Any, List

class GraphModel:
    """Graph model for storing graph structure"""
    
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.metadata = {}
    
    def add_node(self, node: Dict[str, Any]):
        """Add a node to the graph"""
        self.nodes.append(node)
    
    def add_edge(self, edge: Dict[str, Any]):
        """Add an edge to the graph"""
        self.edges.append(edge)
    
    def get_node_by_id(self, node_id: str) -> Dict[str, Any]:
        """Get node by ID"""
        for node in self.nodes:
            if node.get('id') == node_id:
                return node
        return None
    
    def get_edges_for_node(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all edges connected to a node"""
        connected_edges = []
        for edge in self.edges:
            if edge.get('source') == node_id or edge.get('target') == node_id:
                connected_edges.append(edge)
        return connected_edges
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphModel':
        """Create from dictionary"""
        graph = cls()
        graph.nodes = data.get('nodes', [])
        graph.edges = data.get('edges', [])
        graph.metadata = data.get('metadata', {})
        return graph