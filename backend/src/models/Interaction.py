# backend/src/models/Interaction.py
from typing import Dict, Any, Optional
from datetime import datetime

class Interaction:
    """Represents a user interaction event"""
    
    def __init__(self, interaction_type: str, **kwargs):
        self.type = interaction_type
        self.timestamp = kwargs.get('timestamp', datetime.now().isoformat())
        self.user_id = kwargs.get('user_id')
        self.session_id = kwargs.get('session_id')
        self.file_path = kwargs.get('file_path')
        self.project_id = kwargs.get('project_id')
        self.data = kwargs.get('data', {})
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'type': self.type,
            'timestamp': self.timestamp,
            'userId': self.user_id,
            'sessionId': self.session_id,
            'filePath': self.file_path,
            'projectId': self.project_id,
            'data': self.data,
            'ipAddress': self.ip_address,
            'userAgent': self.user_agent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interaction':
        """Create Interaction from dictionary"""
        return cls(
            interaction_type=data['type'],
            timestamp=data.get('timestamp'),
            user_id=data.get('userId'),
            session_id=data.get('sessionId'),
            file_path=data.get('filePath'),
            project_id=data.get('projectId'),
            data=data.get('data', {}),
            ip_address=data.get('ipAddress'),
            user_agent=data.get('userAgent')
        )
    
    def is_valid(self) -> bool:
        """Check if interaction has required fields"""
        return bool(self.type and self.timestamp)