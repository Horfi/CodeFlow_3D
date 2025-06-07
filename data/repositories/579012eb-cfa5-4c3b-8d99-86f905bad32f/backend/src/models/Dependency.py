# backend/src/models/Dependency.py
from typing import Dict, Any, Optional

class Dependency:
    """Represents a dependency relationship between files"""
    
    def __init__(self, source: str, target: str, **kwargs):
        self.source = source
        self.target = target
        self.type = kwargs.get('type', 'unknown')  # 'import', 'require', 'include', etc.
        self.line = kwargs.get('line', 0)
        self.strength = kwargs.get('strength', 1.0)
        self.syntax = kwargs.get('syntax', 'unknown')  # 'es6', 'commonjs', etc.
        self.imported_name = kwargs.get('imported_name')
        self.alias = kwargs.get('alias')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'source': self.source,
            'target': self.target,
            'type': self.type,
            'line': self.line,
            'strength': self.strength,
            'syntax': self.syntax,
            'importedName': self.imported_name,
            'alias': self.alias
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dependency':
        """Create Dependency from dictionary"""
        return cls(
            source=data['source'],
            target=data['target'],
            type=data.get('type', 'unknown'),
            line=data.get('line', 0),
            strength=data.get('strength', 1.0),
            syntax=data.get('syntax', 'unknown'),
            imported_name=data.get('importedName'),
            alias=data.get('alias')
        )