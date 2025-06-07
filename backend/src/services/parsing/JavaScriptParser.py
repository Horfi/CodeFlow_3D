# backend/src/services/parsing/JavaScriptParser.py
import re
import os
from typing import Dict, Any, List

from .base_parser import BaseParser

class JavaScriptParser(BaseParser):
    """Parser for JavaScript files"""
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a JavaScript file and extract metadata"""
        try:
            from utils.FileUtils import FileUtils
            content = FileUtils.read_file_content(file_path)
            
            info = {
                'path': file_path,
                'language': 'javascript',
                'size': len(content),
                'lines': len(content.splitlines()),
                'dependencies': self.extract_dependencies(content),
                'functions': self._extract_functions(content),
                'classes': self._extract_classes(content),
                'exports': self._extract_exports(content),
                'complexity': self._calculate_complexity(content),
                'lastModified': os.path.getmtime(file_path)
            }
            
            return info
            
        except Exception as e:
            return {
                'path': file_path,
                'language': 'javascript',
                'error': str(e)
            }
    
    def extract_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract import/require statements from JavaScript code"""
        dependencies = []
        
        # ES6 imports
        import_patterns = [
            r'import\s+(.+?)\s+from\s+[\'"](.+?)[\'"]',
            r'import\s+[\'"](.+?)[\'"]',
            r'import\s*\(\s*[\'"](.+?)[\'"]\s*\)',  # Dynamic imports
        ]
        
        # CommonJS requires
        require_patterns = [
            r'(?:const|let|var)\s+(.+?)\s*=\s*require\s*\(\s*[\'"](.+?)[\'"]\s*\)',
            r'require\s*\(\s*[\'"](.+?)[\'"]\s*\)',
        ]
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('//') or line.startswith('*'):
                continue
            
            # ES6 imports
            for pattern in import_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    if len(match.groups()) == 2:
                        # import ... from '...'
                        imported = match.group(1).strip()
                        module = match.group(2)
                    else:
                        # import '...' or import('...')
                        module = match.group(1)
                        imported = None
                    
                    dependencies.append({
                        'name': module,
                        'imported': imported,
                        'type': self._classify_import(module),
                        'line': i,
                        'syntax': 'es6'
                    })
            
            # CommonJS requires
            for pattern in require_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    if len(match.groups()) == 2:
                        # const ... = require('...')
                        variable = match.group(1).strip()
                        module = match.group(2)
                    else:
                        # require('...')
                        module = match.group(1)
                        variable = None
                    
                    dependencies.append({
                        'name': module,
                        'variable': variable,
                        'type': self._classify_import(module),
                        'line': i,
                        'syntax': 'commonjs'
                    })
        
        return dependencies
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        # Function patterns
        patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)',  # Regular functions
            r'(\w+)\s*:\s*function\s*\(([^)]*)\)',  # Object methods
            r'(\w+)\s*=\s*function\s*\(([^)]*)\)',  # Function expressions
            r'(\w+)\s*=>\s*',  # Arrow functions (simple)
            r'(\w+)\s*=\s*\(([^)]*)\)\s*=>',  # Arrow functions with params
        ]
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    name = match.group(1)
                    params = match.group(2) if len(match.groups()) > 1 else ''
                    
                    functions.append({
                        'name': name,
                        'line': i,
                        'params': [p.strip() for p in params.split(',') if p.strip()],
                        'is_arrow': '=>' in line
                    })
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{'
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            match = re.search(class_pattern, line)
            if match:
                name = match.group(1)
                extends = match.group(2)
                
                classes.append({
                    'name': name,
                    'line': i,
                    'extends': extends,
                    'methods': self._extract_class_methods(content, i)
                })
        
        return classes
    
    def _extract_exports(self, content: str) -> List[Dict[str, Any]]:
        """Extract export statements"""
        exports = []
        
        export_patterns = [
            r'export\s+default\s+(\w+)',
            r'export\s+{\s*([^}]+)\s*}',
            r'export\s+(?:const|let|var|function|class)\s+(\w+)',
            r'module\.exports\s*=\s*(\w+)',
            r'exports\.(\w+)\s*=',
        ]
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            for pattern in export_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    exports.append({
                        'name': match.group(1),
                        'line': i,
                        'type': 'default' if 'default' in pattern else 'named',
                        'syntax': 'es6' if line.startswith('export') else 'commonjs'
                    })
        
        return exports
    
    def _extract_class_methods(self, content: str, class_line: int) -> List[str]:
        """Extract method names from a class"""
        methods = []
        lines = content.splitlines()
        
        # Find class end (simplified)
        brace_count = 0
        in_class = False
        
        for i in range(class_line - 1, len(lines)):
            line = lines[i].strip()
            
            if '{' in line:
                brace_count += line.count('{')
                in_class = True
            
            if '}' in line:
                brace_count -= line.count('}')
                if brace_count <= 0 and in_class:
                    break
            
            if in_class and brace_count > 0:
                # Look for method definitions
                method_pattern = r'(\w+)\s*\([^)]*\)\s*{'
                match = re.search(method_pattern, line)
                if match:
                    methods.append(match.group(1))
        
        return methods
    
    def _calculate_complexity(self, content: str) -> str:
        """Calculate approximate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        # Count control flow statements
        control_patterns = [
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
            r'\bswitch\b', r'\bcatch\b', r'\b\?\b', r'\b&&\b', r'\b\|\|\b'
        ]
        
        for pattern in control_patterns:
            complexity += len(re.findall(pattern, content))
        
        # Normalize by lines of code
        lines = len([line for line in content.splitlines() if line.strip()])
        if lines > 0:
            normalized_complexity = complexity / lines * 100
        else:
            normalized_complexity = 0
        
        if normalized_complexity <= 5:
            return 'low'
        elif normalized_complexity <= 15:
            return 'medium'
        else:
            return 'high'
    
    def _classify_import(self, module_name: str) -> str:
        """Classify import as external, internal, or relative"""
        if module_name.startswith('./') or module_name.startswith('../'):
            return 'relative'
        elif module_name.startswith('/') or 'src/' in module_name:
            return 'internal'
        else:
            return 'external'
