# backend/src/services/graph/GraphBuilder.py
import networkx as nx
from typing import Dict, Any, List, Set
import os

from services.parsing.ParserFactory import ParserFactory
from utils.FileUtils import FileUtils
from config import Config

class GraphBuilder:
    """Builds dependency graphs from parsed code"""
    
    def __init__(self):
        self.parser_factory = ParserFactory()
    
    def build_graph(self, repo_path: str) -> Dict[str, Any]:
        """Build a complete dependency graph from repository"""
        try:
            # Discover all source files
            source_files = self._discover_source_files(repo_path)
            
            # Parse all files
            parsed_files = self._parse_files(source_files)
            
            # Build graph structure
            graph = self._build_graph_structure(parsed_files, repo_path)
            
            # Calculate graph metrics
            metrics = self._calculate_graph_metrics(graph)
            
            return {
                'nodes': graph['nodes'],
                'edges': graph['edges'],
                'metrics': metrics,
                'metadata': {
                    'total_files': len(source_files),
                    'parsed_files': len(parsed_files),
                    'repository_path': repo_path
                }
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to build graph: {str(e)}")
    
    def _discover_source_files(self, repo_path: str) -> List[str]:
        """Discover all source code files in repository"""
        source_files = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['node_modules', '__pycache__', 'venv', 'env', 'dist', 'build']]
            
            for file in files:
                if FileUtils.is_allowed_file(file):
                    file_path = os.path.join(root, file)
                    # Make path relative to repository root
                    rel_path = os.path.relpath(file_path, repo_path)
                    source_files.append(rel_path)
        
        return source_files
    
    def _parse_files(self, source_files: List[str]) -> Dict[str, Dict[str, Any]]:
        """Parse all source files and extract metadata"""
        parsed_files = {}
        
        for file_path in source_files:
            try:
                # Detect language
                language = FileUtils.detect_language(file_path)
                if not language:
                    continue
                
                # Get appropriate parser
                parser = self.parser_factory.create_parser(language)
                if not parser:
                    continue
                
                # Parse file
                file_info = parser.parse_file(file_path)
                if file_info and 'error' not in file_info:
                    parsed_files[file_path] = file_info
                
            except Exception as e:
                # Log parsing error but continue
                print(f"Warning: Failed to parse {file_path}: {str(e)}")
                continue
        
        return parsed_files
    
    def _build_graph_structure(self, parsed_files: Dict[str, Dict[str, Any]], repo_path: str) -> Dict[str, Any]:
        """Build graph nodes and edges from parsed files"""
        nodes = []
        edges = []
        file_map = {}  # Map file paths to node IDs
        
        # Create nodes
        for file_path, file_info in parsed_files.items():
            node_id = self._generate_node_id(file_path)
            file_map[file_path] = node_id
            
            node = {
                'id': node_id,
                'name': os.path.basename(file_path),
                'path': file_path,
                'language': file_info.get('language', 'unknown'),
                'size': file_info.get('size', 0),
                'lines': file_info.get('lines', 0),
                'complexity': file_info.get('complexity', 'unknown'),
                'functions': file_info.get('functions', []),
                'classes': file_info.get('classes', []),
                'lastModified': file_info.get('lastModified', 0)
            }
            
            nodes.append(node)
        
        # Create edges from dependencies
        for file_path, file_info in parsed_files.items():
            source_id = file_map[file_path]
            dependencies = file_info.get('dependencies', [])
            
            for dep in dependencies:
                target_path = self._resolve_dependency_path(dep, file_path, repo_path, file_map.keys())
                
                if target_path and target_path in file_map:
                    target_id = file_map[target_path]
                    
                    # Avoid self-references
                    if source_id != target_id:
                        edge = {
                            'source': source_id,
                            'target': target_id,
                            'type': dep.get('type', 'unknown'),
                            'line': dep.get('line', 0),
                            'strength': 1.0
                        }
                        
                        edges.append(edge)
        
        return {'nodes': nodes, 'edges': edges}
    
    def _resolve_dependency_path(self, dependency: Dict[str, Any], source_file: str, repo_path: str, available_files: Set[str]) -> str:
        """Resolve dependency to actual file path"""
        dep_name = dependency.get('name', '')
        dep_type = dependency.get('type', 'unknown')
        
        if dep_type == 'external':
            # External dependencies are not resolved to files
            return None
        
        # For relative and internal dependencies, try to find the actual file
        base_dir = os.path.dirname(source_file)
        
        # Common patterns to try
        candidates = []
        
        if dep_type == 'relative':
            # Relative imports like './utils' or '../config'
            if dep_name.startswith('./') or dep_name.startswith('../'):
                # Remove leading ./
                clean_path = dep_name[2:] if dep_name.startswith('./') else dep_name
                candidates.append(os.path.join(base_dir, clean_path))
        else:
            # Internal imports - search in common locations
            candidates.extend([
                dep_name,  # Direct path
                f"src/{dep_name}",  # Common src directory
                f"lib/{dep_name}",  # Common lib directory
                os.path.join(base_dir, dep_name)  # Same directory
            ])
        
        # Add common file extensions
        for candidate in candidates[:]:
            for ext in ['.py', '.js', '.jsx', '.ts', '.tsx']:
                candidates.append(f"{candidate}{ext}")
            
            # Try index files
            for ext in ['.py', '.js', '.jsx', '.ts', '.tsx']:
                candidates.append(f"{candidate}/index{ext}")
                candidates.append(f"{candidate}/__init__{ext}")
        
        # Find the first matching file
        for candidate in candidates:
            # Normalize path
            normalized = os.path.normpath(candidate)
            if normalized in available_files:
                return normalized
        
        return None
    
    def _generate_node_id(self, file_path: str) -> str:
        """Generate a unique node ID from file path"""
        # Use file path as ID, replacing path separators
        return file_path.replace('\\', '/').replace('/', '_').replace('.', '_')
    
    def _calculate_graph_metrics(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic graph metrics"""
        nodes = graph['nodes']
        edges = graph['edges']
        
        # Create NetworkX graph for calculations
        G = nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            G.add_node(node['id'])
        
        # Add edges
        for edge in edges:
            G.add_edge(edge['source'], edge['target'])
        
        # Calculate metrics
        metrics = {
            'node_count': len(nodes),
            'edge_count': len(edges),
            'density': nx.density(G) if len(nodes) > 1 else 0,
            'is_connected': nx.is_weakly_connected(G) if len(nodes) > 0 else False,
            'average_degree': sum(dict(G.degree()).values()) / len(nodes) if len(nodes) > 0 else 0
        }
        
        # Calculate centrality measures for top nodes
        if len(nodes) > 0:
            try:
                pagerank = nx.pagerank(G)
                betweenness = nx.betweenness_centrality(G)
                
                # Get top 10 nodes by PageRank
                top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
                top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
                
                metrics['top_pagerank'] = top_pagerank
                metrics['top_betweenness'] = top_betweenness
                
            except Exception:
                # Handle cases where centrality calculation fails
                metrics['top_pagerank'] = []
                metrics['top_betweenness'] = []
        
        return metrics
