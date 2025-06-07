# backend/src/services/parsing/PythonParser.py
import ast
import os
import re
from typing import Dict, Any, List

from .base_parser import BaseParser

class PythonParser(BaseParser):
    """Parser for Python files"""
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a Python file and extract metadata"""
        try:
            from utils.FileUtils import FileUtils
            content = FileUtils.read_file_content(file_path)
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract information
            info = {
                'path': file_path,
                'language': 'python',
                'size': len(content),
                'lines': len(content.splitlines()),
                'dependencies': self.extract_dependencies(content),
                'functions': self._extract_functions(tree),
                'classes': self._extract_classes(tree),
                'complexity': self._calculate_complexity(tree),
                'lastModified': os.path.getmtime(file_path)
            }
            
            return info
            
        except SyntaxError:
            # Return basic info for files with syntax errors
            content = ''
            try:
                from utils.FileUtils import FileUtils
                content = FileUtils.read_file_content(file_path)
            except:
                pass
                
            return {
                'path': file_path,
                'language': 'python',
                'size': len(content),
                'dependencies': [],
                'error': 'syntax_error'
            }
        except Exception as e:
            return {
                'path': file_path,
                'language': 'python',
                'error': str(e)
            }
    
    def extract_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract import statements from Python code"""
        dependencies = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append({
                            'name': alias.name,
                            'type': self._classify_import(alias.name),
                            'line': node.lineno,
                            'alias': alias.asname
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    level = node.level
                    
                    for alias in node.names:
                        dependencies.append({
                            'name': f"{module}.{alias.name}" if module else alias.name,
                            'module': module,
                            'type': self._classify_import(module, level),
                            'line': node.lineno,
                            'alias': alias.asname,
                            'level': level
                        })
            
        except SyntaxError:
            # Fall back to regex parsing for syntax errors
            dependencies = self._extract_dependencies_regex(content)
        
        return dependencies
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list]
                })
        
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'bases': [self._get_name(base) for base in node.bases],
                    'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list],
                    'methods': self._extract_class_methods(node)
                })
        
        return classes
    
    def _extract_class_methods(self, class_node: ast.ClassDef) -> List[str]:
        """Extract method names from a class"""
        methods = []
        
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(node.name)
        
        return methods
    
    def _calculate_complexity(self, tree: ast.AST) -> str:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        if complexity <= 5:
            return 'low'
        elif complexity <= 10:
            return 'medium'
        else:
            return 'high'
    
    def _classify_import(self, module_name: str, level: int = 0) -> str:
        """Classify import as external, internal, or relative"""
        if level > 0:  # Relative import
            return 'relative'
        elif module_name and ('.' in module_name or module_name in ['os', 'sys', 'json', 'datetime']):
            return 'external'
        else:
            return 'internal'
    
    def _extract_dependencies_regex(self, content: str) -> List[Dict[str, Any]]:
        """Fallback regex-based dependency extraction"""
        dependencies = []
        
        # Match import statements
        import_pattern = r'^import\s+([\w.]+)(?:\s+as\s+(\w+))?'
        from_pattern = r'^from\s+([\w.]*)\s+import\s+([\w,\s*]+)'
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Regular import
            match = re.match(import_pattern, line)
            if match:
                dependencies.append({
                    'name': match.group(1),
                    'type': self._classify_import(match.group(1)),
                    'line': i,
                    'alias': match.group(2)
                })
                continue
            
            # From import
            match = re.match(from_pattern, line)
            if match:
                module = match.group(1)
                imports = match.group(2).split(',')
                
                for imp in imports:
                    imp = imp.strip()
                    if ' as ' in imp:
                        name, alias = imp.split(' as ')
                        name = name.strip()
                        alias = alias.strip()
                    else:
                        name = imp
                        alias = None
                    
                    dependencies.append({
                        'name': f"{module}.{name}" if module else name,
                        'module': module,
                        'type': self._classify_import(module),
                        'line': i,
                        'alias': alias
                    })
        
        return dependencies
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Get decorator name as string"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_name(decorator.value)}.{decorator.attr}"
        else:
            return str(decorator)
    
    def _get_name(self, node: ast.expr) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return str(node)
