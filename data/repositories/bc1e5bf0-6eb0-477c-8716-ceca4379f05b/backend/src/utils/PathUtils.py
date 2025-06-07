# backend/src/utils/PathUtils.py
import os
from typing import Optional

class PathUtils:
    """Path manipulation utilities"""
    
    @staticmethod
    def safe_join(base_path: str, *paths: str) -> Optional[str]:
        """Safely join paths, preventing directory traversal"""
        try:
            # Join paths
            full_path = os.path.join(base_path, *paths)
            
            # Resolve to absolute path
            full_path = os.path.abspath(full_path)
            base_path = os.path.abspath(base_path)
            
            # Check if the result is within base_path
            if full_path.startswith(base_path):
                return full_path
            else:
                return None
                
        except Exception:
            return None
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize a file path"""
        return os.path.normpath(path).replace('\\', '/')
    
    @staticmethod
    def get_relative_path(file_path: str, base_path: str) -> str:
        """Get relative path from base path"""
        try:
            return os.path.relpath(file_path, base_path).replace('\\', '/')
        except Exception:
            return file_path