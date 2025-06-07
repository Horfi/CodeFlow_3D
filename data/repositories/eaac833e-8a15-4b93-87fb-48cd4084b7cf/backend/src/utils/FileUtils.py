# backend/src/utils/FileUtils.py
import os
import mimetypes
import magic
from typing import List, Optional
from config import Config

class FileUtils:
    """File system utilities"""
    
    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """Check if file extension is allowed"""
        _, ext = os.path.splitext(filename.lower())
        return ext in Config.ALLOWED_FILE_EXTENSIONS
    
    @staticmethod
    def detect_language(filename: str) -> Optional[str]:
        """Detect programming language from file extension"""
        _, ext = os.path.splitext(filename.lower())
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.xml': 'xml',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text'
        }
        
        return language_map.get(ext)
    
    @staticmethod
    def read_file_content(file_path: str) -> str:
        """Read file content with encoding detection"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            # If all fail, read as binary and decode with error handling
            with open(file_path, 'rb') as f:
                content = f.read()
                return content.decode('utf-8', errors='replace')
    
    @staticmethod
    def write_file_content(file_path: str, content: str):
        """Write content to file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    continue
        return total_size
    
    @staticmethod
    def is_safe_file(file_path: str, base_path: str) -> bool:
        """Check if file path is safe (within base directory)"""
        try:
            # Resolve absolute paths
            abs_file_path = os.path.abspath(file_path)
            abs_base_path = os.path.abspath(base_path)
            
            # Check if file is within base directory
            return abs_file_path.startswith(abs_base_path) and os.path.exists(abs_file_path)
        except Exception:
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """Get file information"""
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path),
                'extension': os.path.splitext(file_path)[1].lower(),
                'language': FileUtils.detect_language(file_path)
            }
        except OSError:
            return {}
