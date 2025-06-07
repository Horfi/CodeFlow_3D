# backend/src/services/analytics/InteractionTracker.py
from typing import Dict, Any
import logging

class InteractionTracker:
    """Tracks user interactions for analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def track_interaction(self, interaction_data: Dict[str, Any]):
        """Track a user interaction"""
        try:
            # Validate interaction data
            from utils.ValidationUtils import ValidationUtils
            if not ValidationUtils.validate_interaction_data(interaction_data):
                self.logger.warning(f"Invalid interaction data: {interaction_data}")
                return
            
            # Store interaction in database
            from database.UserDataManager import UserDataManager
            user_data_manager = UserDataManager()
            user_data_manager.track_interaction(interaction_data)
            
            self.logger.info(f"Tracked interaction: {interaction_data.get('type')} "
                           f"for user {interaction_data.get('user_id')}")
            
        except Exception as e:
            self.logger.error(f"Failed to track interaction: {e}")