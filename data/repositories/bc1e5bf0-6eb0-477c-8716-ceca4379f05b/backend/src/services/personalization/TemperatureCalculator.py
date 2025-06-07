# backend/src/services/personalization/TemperatureCalculator.py
from typing import Dict, Any
import time

class TemperatureCalculator:
    """Calculates file temperature based on user interactions"""
    
    def calculate_temperature(self, file_interactions: Dict[str, Any], current_time: float = None) -> float:
        """Calculate temperature for a file based on interaction data"""
        if current_time is None:
            current_time = time.time() * 1000  # milliseconds
        
        click_count = file_interactions.get('click_count', 0)
        edit_count = file_interactions.get('edit_count', 0)
        total_time = file_interactions.get('total_time', 0)
        last_access = file_interactions.get('last_access', 0)
        
        if click_count == 0:
            return 0.5  # Neutral temperature
        
        # Recency factor (0-1)
        hours_since_access = (current_time - last_access) / (1000 * 60 * 60)
        recency_score = max(0, 1 - (hours_since_access / 24))  # Decay over 24 hours
        
        # Interaction frequency factor (0-1)
        frequency_score = min(1, click_count / 10)  # Normalize to max 10 clicks
        
        # Edit activity factor (0-1)
        edit_score = min(1, edit_count / 5)  # Normalize to max 5 edits
        
        # Time investment factor (0-1)
        time_score = min(1, total_time / 300)  # Normalize to 5 minutes
        
        # Weighted combination
        temperature = (
            recency_score * 0.4 +
            frequency_score * 0.3 +
            edit_score * 0.2 +
            time_score * 0.1
        )
        
        return min(1.0, max(0.0, temperature))
