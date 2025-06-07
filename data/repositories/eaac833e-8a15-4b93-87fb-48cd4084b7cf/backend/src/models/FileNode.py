# backend/src/models/FileNode.py
from typing import Dict, Any, List, Optional
from datetime import datetime

class FileNode:
    """Represents a file node in the dependency graph"""
    
    def __init__(self, file_path: str, **kwargs):
        self.id = self._generate_id(file_path)
        self.path = file_path
        self.name = file_path.split('/')[-1]
        self.language = kwargs.get('language', 'unknown')
        self.size = kwargs.get('size', 0)
        self.lines = kwargs.get('lines', 0)
        self.complexity = kwargs.get('complexity', 'unknown')
        self.dependencies = kwargs.get('dependencies', [])
        self.functions = kwargs.get('functions', [])
        self.classes = kwargs.get('classes', [])
        self.last_modified = kwargs.get('last_modified', datetime.now().timestamp())
        
        # User interaction data
        self.user_interactions = 0
        self.temperature = 0.5
        self.importance_score = 0.0
    
    def _generate_id(self, file_path: str) -> str:
        """Generate unique ID from file path"""
        return file_path.replace('/', '_').replace('.', '_')
    
    def add_dependency(self, dependency: Dict[str, Any]):
        """Add a dependency to this file"""
        self.dependencies.append(dependency)
    
    def update_user_stats(self, interaction_type: str, **kwargs):
        """Update user interaction statistics"""
        self.user_interactions += 1
        
        # Update temperature based on interaction
        if interaction_type in ['click', 'edit', 'view']:
            self.temperature = min(1.0, self.temperature + 0.1)
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate various metrics for this file"""
        return {
            'dependency_count': len(self.dependencies),
            'complexity_score': self._complexity_to_score(),
            'size_category': self._categorize_size(),
            'user_engagement': self.user_interactions,
            'temperature': self.temperature
        }
    
    def _complexity_to_score(self) -> float:
        """Convert complexity string to numeric score"""
        complexity_map = {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.8,
            'unknown': 0.3
        }
        return complexity_map.get(self.complexity, 0.3)
    
    def _categorize_size(self) -> str:
        """Categorize file size"""
        if self.lines < 50:
            return 'small'
        elif self.lines < 200:
            return 'medium'
        elif self.lines < 500:
            return 'large'
        else:
            return 'very_large'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'path': self.path,
            'name': self.name,
            'language': self.language,
            'size': self.size,
            'lines': self.lines,
            'complexity': self.complexity,
            'dependencies': self.dependencies,
            'functions': self.functions,
            'classes': self.classes,
            'lastModified': self.last_modified,
            'userInteractions': self.user_interactions,
            'temperature': self.temperature,
            'importanceScore': self.importance_score,
            'metrics': self.calculate_metrics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileNode':
        """Create FileNode from dictionary"""
        node = cls(
            file_path=data['path'],
            language=data.get('language', 'unknown'),
            size=data.get('size', 0),
            lines=data.get('lines', 0),
            complexity=data.get('complexity', 'unknown'),
            dependencies=data.get('dependencies', []),
            functions=data.get('functions', []),
            classes=data.get('classes', []),
            last_modified=data.get('lastModified', datetime.now().timestamp())
        )
        
        # Set additional properties
        node.user_interactions = data.get('userInteractions', 0)
        node.temperature = data.get('temperature', 0.5)
        node.importance_score = data.get('importanceScore', 0.0)
        
        return node