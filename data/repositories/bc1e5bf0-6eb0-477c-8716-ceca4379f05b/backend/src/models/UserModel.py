# backend/src/models/UserModel.py
from typing import Dict, Any, List
from datetime import datetime

class UserModel:
    """User model for storing user preferences and behavior"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.file_interactions = {}
        self.language_preferences = {}
        self.behavior_patterns = {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
    
    def update_file_interaction(self, file_path: str, interaction_type: str, **kwargs):
        """Update file interaction data"""
        if file_path not in self.file_interactions:
            self.file_interactions[file_path] = {
                'click_count': 0,
                'edit_count': 0,
                'view_time': 0,
                'last_access': None
            }
        
        interaction = self.file_interactions[file_path]
        
        if interaction_type == 'click':
            interaction['click_count'] += 1
        elif interaction_type == 'edit':
            interaction['edit_count'] += 1
        elif interaction_type == 'view':
            interaction['view_time'] += kwargs.get('duration', 0)
        
        interaction['last_access'] = datetime.now()
        self.last_updated = datetime.now()
    
    def update_language_preference(self, language: str, preference_delta: float = 0.1):
        """Update language preference"""
        if language not in self.language_preferences:
            self.language_preferences[language] = 0.5
        
        # Update preference (between 0 and 1)
        self.language_preferences[language] = max(0, min(1, 
            self.language_preferences[language] + preference_delta))
        
        self.last_updated = datetime.now()
    
    def get_file_temperature(self, file_path: str) -> float:
        """Calculate file temperature based on interactions"""
        if file_path not in self.file_interactions:
            return 0.5
        
        interaction = self.file_interactions[file_path]
        
        # Simple temperature calculation
        click_factor = min(1.0, interaction['click_count'] / 10)
        edit_factor = min(1.0, interaction['edit_count'] / 5)
        
        # Recency factor
        if interaction['last_access']:
            hours_since = (datetime.now() - interaction['last_access']).total_seconds() / 3600
            recency_factor = max(0, 1 - (hours_since / 24))  # Decay over 24 hours
        else:
            recency_factor = 0
        
        temperature = (click_factor * 0.4 + edit_factor * 0.3 + recency_factor * 0.3)
        return max(0.1, min(1.0, temperature))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'user_id': self.user_id,
            'file_interactions': self.file_interactions,
            'language_preferences': self.language_preferences,
            'behavior_patterns': self.behavior_patterns,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserModel':
        """Create from dictionary"""
        user_model = cls(data['user_id'])
        user_model.file_interactions = data.get('file_interactions', {})
        user_model.language_preferences = data.get('language_preferences', {})
        user_model.behavior_patterns = data.get('behavior_patterns', {})
        
        if 'created_at' in data:
            user_model.created_at = datetime.fromisoformat(data['created_at'])
        if 'last_updated' in data:
            user_model.last_updated = datetime.fromisoformat(data['last_updated'])
        
        return user_model