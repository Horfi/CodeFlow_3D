# backend/src/services/personalization/PreferenceManager.py
from typing import Dict, Any, List

class PreferenceManager:
    """Manages user preferences"""
    
    def get_language_preferences(self, user_model: Dict[str, Any]) -> Dict[str, float]:
        """Get user's language preferences as scores"""
        language_prefs = user_model.get('language_preferences', {})
        
        # Normalize scores to 0-1 range
        max_score = max([data.get('usage_score', 0) for data in language_prefs.values()] + [1])
        
        normalized_prefs = {}
        for lang, data in language_prefs.items():
            normalized_prefs[lang] = data.get('usage_score', 0) / max_score
        
        return normalized_prefs
    
    def get_default_filters(self, user_model: Dict[str, Any]) -> List[str]:
        """Get default language filters based on user preferences"""
        language_prefs = self.get_language_preferences(user_model)
        
        # Return languages with score > 0.3
        default_languages = [
            lang for lang, score in language_prefs.items()
            if score > 0.3
        ]
        
        # If no preferences, return common languages
        if not default_languages:
            default_languages = ['python', 'javascript', 'typescript']
        
        return default_languages
    
    def update_preferences(self, user_model: Dict[str, Any], preference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        if 'language_preferences' in preference_data:
            user_model.setdefault('language_preferences', {}).update(
                preference_data['language_preferences']
            )
        
        if 'behavior_patterns' in preference_data:
            user_model.setdefault('behavior_patterns', {}).update(
                preference_data['behavior_patterns']
            )
        
        return user_model