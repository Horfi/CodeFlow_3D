# backend/src/services/parsing/base_parser.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseParser(ABC):
    """Abstract base class for language parsers"""
    
    @abstractmethod
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a file and extract information"""
        pass
    
    @abstractmethod
    def extract_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract dependencies from file content"""
        pass