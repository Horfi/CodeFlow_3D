# backend/src/services/personalization/PatternAnalyzer.py
from typing import Dict, Any, List
from collections import defaultdict

class PatternAnalyzer:
    """Analyzes user behavior patterns"""
    
    def analyze_access_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze file access patterns from interaction history"""
        patterns = {
            'co_accessed_files': defaultdict(int),
            'session_patterns': [],
            'time_patterns': defaultdict(int)
        }
        
        # Group interactions by session
        sessions = defaultdict(list)
        for interaction in interactions:
            session_id = interaction.get('session_id', 'default')
            sessions[session_id].append(interaction)
        
        # Analyze co-access patterns
        for session_interactions in sessions.values():
            files_in_session = set()
            for interaction in session_interactions:
                file_path = interaction.get('file_path')
                if file_path:
                    files_in_session.add(file_path)
            
            # Record co-access patterns
            files_list = list(files_in_session)
            for i, file1 in enumerate(files_list):
                for file2 in files_list[i+1:]:
                    patterns['co_accessed_files'][(file1, file2)] += 1
        
        return patterns
    
    def get_navigation_style(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Determine user's navigation style"""
        if not interactions:
            return {'systematic': 0.5, 'exploratory': 0.5}
        
        # Analyze sequence patterns
        file_sequences = []
        current_sequence = []
        
        for interaction in interactions:
            if interaction.get('type') in ['file_opened', 'node_click']:
                file_path = interaction.get('file_path')
                if file_path:
                    current_sequence.append(file_path)
        
        # Simple heuristic: if user visits files in directory order, more systematic
        systematic_score = 0.5
        if len(current_sequence) > 3:
            # Check for directory-based navigation
            directory_jumps = 0
            for i in range(1, len(current_sequence)):
                prev_dir = '/'.join(current_sequence[i-1].split('/')[:-1])
                curr_dir = '/'.join(current_sequence[i].split('/')[:-1])
                if prev_dir != curr_dir:
                    directory_jumps += 1
            
            # Lower directory jumps = more systematic
            systematic_score = max(0.1, 1.0 - (directory_jumps / len(current_sequence)))
        
        return {
            'systematic': systematic_score,
            'exploratory': 1.0 - systematic_score
        }
