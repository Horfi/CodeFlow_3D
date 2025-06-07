# backend/src/services/graph/CentralityCalculator.py
import networkx as nx
from typing import Dict, Any, List, Optional
import logging

class CentralityCalculator:
    """Calculates various centrality measures for graph nodes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_all_centralities(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all centrality measures for the graph"""
        try:
            # Build NetworkX graph from data
            G = self._build_networkx_graph(graph_data)
            
            if G.number_of_nodes() == 0:
                return {}
            
            centralities = {}
            
            # Calculate different centrality measures
            centralities['pagerank'] = self._calculate_pagerank(G)
            centralities['betweenness'] = self._calculate_betweenness_centrality(G)
            centralities['degree'] = self._calculate_degree_centrality(G)
            centralities['eigenvector'] = self._calculate_eigenvector_centrality(G)
            centralities['closeness'] = self._calculate_closeness_centrality(G)
            
            # Combine scores into a composite importance score
            centralities['importance'] = self._calculate_composite_importance(centralities)
            
            return centralities
            
        except Exception as e:
            self.logger.error(f"Failed to calculate centralities: {e}")
            return {}
    
    def _build_networkx_graph(self, graph_data: Dict[str, Any]) -> nx.DiGraph:
        """Convert graph data to NetworkX directed graph"""
        G = nx.DiGraph()
        
        # Add nodes
        nodes = graph_data.get('nodes', [])
        for node in nodes:
            node_id = node.get('id')
            if node_id:
                G.add_node(node_id, **node)
        
        # Add edges
        edges = graph_data.get('edges', [])
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            
            # Handle cases where source/target might be objects with id
            if isinstance(source, dict):
                source = source.get('id')
            if isinstance(target, dict):
                target = target.get('id')
            
            if source and target and source in G and target in G:
                G.add_edge(source, target, **edge)
        
        return G
    
    def _calculate_pagerank(self, G: nx.DiGraph) -> Dict[str, float]:
        """Calculate PageRank centrality"""
        try:
            return nx.pagerank(G, alpha=0.85, max_iter=100, tol=1e-06)
        except Exception as e:
            self.logger.warning(f"PageRank calculation failed: {e}")
            return {node: 0.0 for node in G.nodes()}
    
    def _calculate_betweenness_centrality(self, G: nx.DiGraph) -> Dict[str, float]:
        """Calculate betweenness centrality"""
        try:
            # For large graphs, use sampling to speed up calculation
            if G.number_of_nodes() > 1000:
                return nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))
            else:
                return nx.betweenness_centrality(G)
        except Exception as e:
            self.logger.warning(f"Betweenness centrality calculation failed: {e}")
            return {node: 0.0 for node in G.nodes()}
    
    def _calculate_degree_centrality(self, G: nx.DiGraph) -> Dict[str, float]:
        """Calculate degree centrality"""
        try:
            # Use in-degree + out-degree for directed graphs
            in_degree = dict(G.in_degree())
            out_degree = dict(G.out_degree())
            
            centrality = {}
            max_degree = max(max(in_degree.values(), default=0), max(out_degree.values(), default=0))
            
            if max_degree > 0:
                for node in G.nodes():
                    total_degree = in_degree.get(node, 0) + out_degree.get(node, 0)
                    centrality[node] = total_degree / (max_degree * 2)  # Normalize
            else:
                centrality = {node: 0.0 for node in G.nodes()}
            
            return centrality
        except Exception as e:
            self.logger.warning(f"Degree centrality calculation failed: {e}")
            return {node: 0.0 for node in G.nodes()}
    
    def _calculate_eigenvector_centrality(self, G: nx.DiGraph) -> Dict[str, float]:
        """Calculate eigenvector centrality"""
        try:
            # Convert to undirected for eigenvector centrality
            G_undirected = G.to_undirected()
            return nx.eigenvector_centrality(G_undirected, max_iter=1000, tol=1e-06)
        except Exception as e:
            self.logger.warning(f"Eigenvector centrality calculation failed: {e}")
            return {node: 0.0 for node in G.nodes()}
    
    def _calculate_closeness_centrality(self, G: nx.DiGraph) -> Dict[str, float]:
        """Calculate closeness centrality"""
        try:
            return nx.closeness_centrality(G)
        except Exception as e:
            self.logger.warning(f"Closeness centrality calculation failed: {e}")
            return {node: 0.0 for node in G.nodes()}
    
    def _calculate_composite_importance(self, centralities: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate composite importance score from all centrality measures"""
        importance = {}
        
        # Get all node IDs
        all_nodes = set()
        for centrality_dict in centralities.values():
            all_nodes.update(centrality_dict.keys())
        
        # Weighted combination of centrality measures
        weights = {
            'pagerank': 0.35,
            'betweenness': 0.25,
            'degree': 0.20,
            'eigenvector': 0.15,
            'closeness': 0.05
        }
        
        for node in all_nodes:
            score = 0.0
            for measure, weight in weights.items():
                if measure in centralities:
                    score += centralities[measure].get(node, 0.0) * weight
            importance[node] = score
        
        return importance
    
    def get_top_nodes(self, centralities: Dict[str, Any], measure: str = 'importance', limit: int = 10) -> List[Dict[str, Any]]:
        """Get top nodes by centrality measure"""
        if measure not in centralities:
            return []
        
        measure_data = centralities[measure]
        sorted_nodes = sorted(measure_data.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'node_id': node_id,
                'score': score,
                'rank': rank + 1
            }
            for rank, (node_id, score) in enumerate(sorted_nodes[:limit])
        ]
    
    def normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores to 0-1 range"""
        if not scores:
            return scores
        
        min_score = min(scores.values())
        max_score = max(scores.values())
        
        if min_score == max_score:
            return {node: 0.5 for node in scores}
        
        normalized = {}
        for node, score in scores.items():
            normalized[node] = (score - min_score) / (max_score - min_score)
        
        return normalized