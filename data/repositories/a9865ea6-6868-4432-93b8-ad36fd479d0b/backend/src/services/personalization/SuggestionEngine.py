# backend/src/services/personalization/SuggestionEngine.py
from typing import Dict, Any, List

class SuggestionEngine:
    """Generates personalized suggestions"""
    
    def generate_suggestions(self, current_file: str, user_model: Dict[str, Any], 
                           graph_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized file suggestions"""
        suggestions = []
        
        # Get user's frequently accessed files
        file_interactions = user_model.get('file_interactions', {})
        frequent_files = sorted(
            file_interactions.items(),
            key=lambda x: x[1].get('click_count', 0),
            reverse=True
        )[:5]
        
        for file_path, interaction_data in frequent_files:
            if file_path != current_file:
                suggestions.append({
                    'file': file_path,
                    'name': file_path.split('/')[-1],
                    'confidence': min(0.9, interaction_data.get('click_count', 0) / 10),
                    'reason': f"Frequently accessed ({interaction_data.get('click_count', 0)} times)",
                    'type': 'frequent'
                })
        
        # Get files from the same directory
        if current_file:
            current_dir = '/'.join(current_file.split('/')[:-1])
            for node in graph_data.get('nodes', []):
                node_dir = '/'.join(node.get('path', '').split('/')[:-1])
                if node_dir == current_dir and node.get('path') != current_file:
                    suggestions.append({
                        'file': node.get('path'),
                        'name': node.get('name'),
                        'confidence': 0.6,
                        'reason': f"Same directory ({current_dir})",
                        'type': 'directory'
                    })
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        return suggestions[:8]