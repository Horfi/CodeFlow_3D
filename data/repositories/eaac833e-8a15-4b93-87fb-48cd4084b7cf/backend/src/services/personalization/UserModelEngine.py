# backend/src/services/personalization/UserModelEngine.py
from typing import Dict, Any
from datetime import datetime

class UserModelEngine:
    """Core user model engine for personalization"""
    
    def create_new_user_model(self) -> Dict[str, Any]:
        """Create a new user model with default values"""
        return {
            'file_interactions': {},
            'language_preferences': {},
            'behavior_patterns': {
                'exploration_style': {
                    'depth_first': 0.5,
                    'systematic': 0.5,
                    'dependency_follower': 0.5
                },
                'session_characteristics': {
                    'average_duration': 0,
                    'files_per_session': 0,
                    'focus_span': 0.5
                }
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'version': '1.0'
        }
    
    def update_from_interaction(self, user_model: Dict[str, Any], interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Update user model from interaction data"""
        interaction_type = interaction.get('type')
        file_path = interaction.get('file_path')
        
        if not file_path:
            return user_model
        
        # Update file interactions
        file_interactions = user_model.setdefault('file_interactions', {})
        file_data = file_interactions.setdefault(file_path, {
            'click_count': 0,
            'edit_count': 0,
            'total_time': 0,
            'last_access': 0
        })
        
        if interaction_type in ['file_opened', 'file_selected', 'node_click']:
            file_data['click_count'] += 1
            file_data['last_access'] = interaction.get('timestamp', 0)
        elif interaction_type == 'code_edited':
            file_data['edit_count'] += 1
        
        # Update language preferences if available
        language = interaction.get('language')
        if language:
            lang_prefs = user_model.setdefault('language_preferences', {})
            lang_data = lang_prefs.setdefault(language, {
                'usage_score': 0,
                'file_count': 0
            })
            lang_data['usage_score'] += 0.1
        
        user_model['last_updated'] = datetime.now().isoformat()
        return user_model