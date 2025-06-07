# backend/src/services/graph/EdgeManager.py
from typing import Dict, Any, List, Tuple

class EdgeManager:
    """Manages graph edges"""
    
    def __init__(self):
        self.edges = []
        self.adjacency = {}
    
    def add_edge(self, source: str, target: str, edge_data: Dict[str, Any] = None):
        """Add an edge to the graph"""
        edge = {
            'source': source,
            'target': target,
            **(edge_data or {})
        }
        self.edges.append(edge)
        
        # Update adjacency list
        if source not in self.adjacency:
            self.adjacency[source] = []
        self.adjacency[source].append(target)
    
    def get_edges(self) -> List[Dict[str, Any]]:
        """Get all edges"""
        return self.edges
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighbors of a node"""
        return self.adjacency.get(node_id, [])
    
    def remove_edge(self, source: str, target: str):
        """Remove an edge"""
        self.edges = [e for e in self.edges if not (e['source'] == source and e['target'] == target)]
        
        if source in self.adjacency:
            self.adjacency[source] = [t for t in self.adjacency[source] if t != target]
