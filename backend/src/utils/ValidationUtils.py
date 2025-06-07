# backend/src/utils/ValidationUtils.py
import re
import uuid
import os
from urllib.parse import urlparse
from typing import List, Any, Dict

class ValidationUtils:
    """Input validation utilities"""
    
    @staticmethod
    def is_valid_git_url(url: str) -> bool:
        """Validate Git repository URL"""
        if not url or not isinstance(url, str):
            return False
        
        # GitHub/GitLab patterns
        github_pattern = r'^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$'
        gitlab_pattern = r'^https://gitlab\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$'
        git_pattern = r'^https://.*\.git$'
        ssh_pattern = r'^git@.*:.*\.git$'
        
        return (
            re.match(github_pattern, url) or
            re.match(gitlab_pattern, url) or
            re.match(git_pattern, url) or
            re.match(ssh_pattern, url)
        )
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """Validate UUID format"""
        try:
            uuid.UUID(uuid_string)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_safe_path(path: str) -> bool:
        """Check if path is safe (no directory traversal)"""
        if not path or not isinstance(path, str):
            return False
        
        # Normalize path
        normalized = os.path.normpath(path)
        
        # Check for directory traversal attempts
        if '..' in normalized or normalized.startswith('/'):
            return False
        
        # Check for suspicious characters
        dangerous_chars = ['<', '>', '|', '*', '?', '"']
        if any(char in path for char in dangerous_chars):
            return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system operations"""
        if not filename:
            return 'untitled'
        
        # Remove or replace dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip(' .')
        
        # Ensure filename is not empty
        if not sanitized:
            return 'untitled'
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        return sanitized
    
    @staticmethod
    def validate_json_data(data: Any, required_fields: List[str] = None) -> bool:
        """Validate JSON data structure"""
        if not isinstance(data, dict):
            return False
        
        if required_fields:
            for field in required_fields:
                if field not in data:
                    return False
        
        return True
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def validate_interaction_data(data: Dict[str, Any]) -> bool:
        """Validate user interaction data"""
        required_fields = ['type', 'timestamp']
        
        if not ValidationUtils.validate_json_data(data, required_fields):
            return False
        
        # Validate interaction type - EXPANDED LIST
        valid_types = [
            'file_opened', 'file_selected', 'node_click', 'code_edited',
            'search', 'bookmark_added', 'version_switch', 'graph_interaction',
            'page_view', 'session_start', 'session_end',  # Added these
            'navigation', 'scroll', 'click', 'hover'       # Added these
        ]
        
        if data['type'] not in valid_types:
            return False
        
        # Validate timestamp
        try:
            timestamp = data['timestamp']
            if not isinstance(timestamp, (int, float)) or timestamp <= 0:
                return False
        except (KeyError, TypeError, ValueError):
            return False
        
        return True