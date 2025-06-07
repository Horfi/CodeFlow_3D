# backend/src/services/personalization/PersonalizationFactory.py
from typing import Any, Dict, Optional

class PersonalizationFactory:
    """Factory for creating personalization processors"""
    
    def create_graph_processor(self, version: str):
        """Create a graph processor for the specified version"""
        if version == 'personalized':
            return PersonalizedGraphProcessor()
        elif version == 'random':
            return RandomGraphProcessor()
        else:
            raise ValueError(f"Unknown version: {version}")

class PersonalizedGraphProcessor:
    """Processes graphs with personalization features"""
    
    def process_graph(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply personalized processing to graph data"""
        # Add personalization metadata to nodes
        nodes = graph_data.get('nodes', [])
        
        for node in nodes:
            # Add temperature and importance placeholders
            node['temperature'] = 0.5  # Will be updated by user interactions
            node['importance_score'] = 0.0
            node['user_interactions'] = 0
            node['personalized'] = True
        
        return graph_data

class RandomGraphProcessor:
    """Processes graphs with random/control features"""
    
    def process_graph(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply random processing to graph data"""
        import random
        
        nodes = graph_data.get('nodes', [])
        
        for node in nodes:
            # Add random values for control group
            node['temperature'] = random.random()
            node['importance_score'] = random.random()
            node['user_interactions'] = 0
            node['personalized'] = False
        
        return graph_data