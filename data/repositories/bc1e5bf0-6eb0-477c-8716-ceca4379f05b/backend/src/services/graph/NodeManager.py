# backend/src/services/graph/NodeManager.py
from typing import Dict, Any, List

class NodeManager:
    """Manages graph nodes"""
    
    def __init__(self):
        self.nodes = {}
    
    def add_node(self, node_id: str, node_data: Dict[str, Any]):
        """Add a node to the graph"""
        self.nodes[node_id] = node_data
    
    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Get a node by ID"""
        return self.nodes.get(node_id, {})
    
    def update_node(self, node_id: str, updates: Dict[str, Any]):
        """Update node data"""
        if node_id in self.nodes:
            self.nodes[node_id].update(updates)
    
    def remove_node(self, node_id: str):
        """Remove a node"""
        if node_id in self.nodes:
            del self.nodes[node_id]
    
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes"""
        return list(self.nodes.values())