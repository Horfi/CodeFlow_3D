# backend/src/services/parsing/TypeScriptParser.py
import re
import os
from typing import Dict, Any, List

from .JavaScriptParser import JavaScriptParser

class TypeScriptParser(JavaScriptParser):
    """Parser for TypeScript files (extends JavaScript parser)"""
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a TypeScript file and extract metadata"""
        try:
            from utils.FileUtils import FileUtils
            content = FileUtils.read_file_content(file_path)
            
            # Get base JavaScript info
            info = super().parse_file(file_path)
            
            # Override language
            info['language'] = 'typescript'
            
            # Add TypeScript-specific features
            info['interfaces'] = self._extract_interfaces(content)
            info['types'] = self._extract_types(content)
            info['enums'] = self._extract_enums(content)
            info['decorators'] = self._extract_decorators(content)
            
            return info
            
        except Exception as e:
            return {
                'path': file_path,
                'language': 'typescript',
                'error': str(e)
            }
    
    def _extract_interfaces(self, content: str) -> List[Dict[str, Any]]:
        """Extract interface definitions"""
        interfaces = []
        
        interface_pattern = r'interface\s+(\w+)(?:\s+extends\s+([\w,\s]+))?\s*{'
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            match = re.search(interface_pattern, line)
            if match:
                name = match.group(1)
                extends = match.group(2)
                
                interfaces.append({
                    'name': name,
                    'line': i,
                    'extends': [ext.strip() for ext in extends.split(',')] if extends else []
                })
        
        return interfaces
    
    def _extract_types(self, content: str) -> List[Dict[str, Any]]:
        """Extract type definitions"""
        types = []
        
        type_pattern = r'type\s+(\w+)\s*=\s*(.+);'
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            match = re.search(type_pattern, line)
            if match:
                name = match.group(1)
                definition = match.group(2)
                
                types.append({
                    'name': name,
                    'line': i,
                    'definition': definition.strip()
                })
        
        return types
    
    def _extract_enums(self, content: str) -> List[Dict[str, Any]]:
        """Extract enum definitions"""
        enums = []
        
        enum_pattern = r'enum\s+(\w+)\s*{'
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            match = re.search(enum_pattern, line)
            if match:
                name = match.group(1)
                
                enums.append({
                    'name': name,
                    'line': i
                })
        
        return enums
    
    def _extract_decorators(self, content: str) -> List[Dict[str, Any]]:
        """Extract decorator usage"""
        decorators = []
        
        decorator_pattern = r'@(\w+)(?:\([^)]*\))?'
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            matches = re.finditer(decorator_pattern, line)
            for match in matches:
                decorators.append({
                    'name': match.group(1),
                    'line': i,
                    'full': match.group(0)
                })
        
        return decorators