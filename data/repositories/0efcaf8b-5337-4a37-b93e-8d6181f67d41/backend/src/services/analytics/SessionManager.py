# backend/src/services/analytics/SessionManager.py
from typing import Dict, Any, Optional
from datetime import datetime

class SessionManager:
    """Manages user sessions"""
    
    def __init__(self):
        self.active_sessions = {}
    
    def create_session(self, user_id: str, session_id: str, project_id: str = None) -> Dict[str, Any]:
        """Create a new session"""
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'project_id': project_id,
            'started_at': datetime.now(),
            'last_activity': datetime.now(),
            'interaction_count': 0
        }
        
        self.active_sessions[session_id] = session_data
        return session_data
    
    def update_session(self, session_id: str, interaction_data: Dict[str, Any]):
        """Update session with new interaction"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session['last_activity'] = datetime.now()
            session['interaction_count'] += 1
    
    def end_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """End a session and return session data"""
        if session_id in self.active_sessions:
            session = self.active_sessions.pop(session_id)
            session['ended_at'] = datetime.now()
            session['duration'] = (session['ended_at'] - session['started_at']).total_seconds()
            return session
        return None