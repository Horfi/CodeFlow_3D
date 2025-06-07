# backend/src/models/Session.py
from typing import Dict, Any, List, Optional
from datetime import datetime

class Session:
    """Represents a user session"""
    
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.started_at = datetime.now()
        self.ended_at = None
        self.interactions = []
        self.project_id = None
        self.version = None
    
    def add_interaction(self, interaction: Dict[str, Any]):
        """Add an interaction to this session"""
        interaction['timestamp'] = datetime.now().isoformat()
        interaction['session_id'] = self.session_id
        self.interactions.append(interaction)
    
    def end_session(self):
        """End the session"""
        self.ended_at = datetime.now()
    
    def get_duration(self) -> Optional[float]:
        """Get session duration in seconds"""
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None
    
    def get_interaction_count(self) -> int:
        """Get total number of interactions"""
        return len(self.interactions)
    
    def get_files_accessed(self) -> List[str]:
        """Get list of files accessed in this session"""
        files = set()
        for interaction in self.interactions:
            file_path = interaction.get('file_path')
            if file_path:
                files.add(file_path)
        return list(files)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'sessionId': self.session_id,
            'userId': self.user_id,
            'startedAt': self.started_at.isoformat(),
            'endedAt': self.ended_at.isoformat() if self.ended_at else None,
            'duration': self.get_duration(),
            'interactionCount': self.get_interaction_count(),
            'filesAccessed': self.get_files_accessed(),
            'projectId': self.project_id,
            'version': self.version,
            'interactions': self.interactions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create Session from dictionary"""
        session = cls(data['sessionId'], data['userId'])
        session.started_at = datetime.fromisoformat(data['startedAt'])
        if data.get('endedAt'):
            session.ended_at = datetime.fromisoformat(data['endedAt'])
        session.interactions = data.get('interactions', [])
        session.project_id = data.get('projectId')
        session.version = data.get('version')
        return session
