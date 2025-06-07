# backend/src/services/parsing/DependencyResolver.py
import os
from typing import List, Dict, Any
from .ParserFactory import ParserFactory

class DependencyResolver:
    """Resolves file dependencies across the codebase"""
    
    def __init__(self):
        self.parser_factory = ParserFactory()
    
    def resolve_file_dependencies(self, file_path: str) -> List[Dict[str, Any]]:
        """Resolve dependencies for a specific file"""
        try:
            # Detect language and get parser
            from utils.FileUtils import FileUtils
            language = FileUtils.detect_language(file_path)
            
            if not language:
                return []
            
            parser = self.parser_factory.create_parser(language)
            if not parser:
                return []
            
            # Parse file and extract dependencies
            file_info = parser.parse_file(file_path)
            return file_info.get('dependencies', [])
            
        except Exception as e:
            print(f"Error resolving dependencies for {file_path}: {e}")
            return []
    
    def find_reverse_dependencies(self, target_file: str, repo_path: str) -> List[Dict[str, Any]]:
        """Find files that depend on the target file"""
        dependents = []
        
        try:
            # Walk through all files in repository
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in ['node_modules', '__pycache__', 'venv']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Skip the target file itself
                    if file_path == target_file:
                        continue
                    
                    # Get dependencies of this file
                    deps = self.resolve_file_dependencies(file_path)
                    
                    # Check if target file is in dependencies
                    for dep in deps:
                        if self._is_dependency_match(dep, target_file, file_path, repo_path):
                            dependents.append({
                                'path': os.path.relpath(file_path, repo_path),
                                'name': os.path.basename(file_path),
                                'line': dep.get('line', 0),
                                'type': dep.get('type', 'unknown')
                            })
                            break
            
            return dependents
            
        except Exception as e:
            print(f"Error finding reverse dependencies: {e}")
            return []
    
    def _is_dependency_match(self, dependency: Dict[str, Any], target_file: str, 
                           source_file: str, repo_path: str) -> bool:
        """Check if a dependency matches the target file"""
        dep_name = dependency.get('name', '')
        
        # Simple name matching (could be enhanced)
        target_name = os.path.basename(target_file)
        target_name_no_ext = os.path.splitext(target_name)[0]
        
        return (dep_name == target_name or 
                dep_name == target_name_no_ext or
                dep_name.endswith(target_name))