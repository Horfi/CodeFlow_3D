# backend/src/database/UserDataManager.py
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from .SQLiteManager import SQLiteManager

class UserDataManager:
    """Manages user data and models"""
    
    def __init__(self, db_manager: SQLiteManager = None):
        self.db = db_manager or SQLiteManager('codeflow.db')
    
    def save_user_model(self, user_id: str, model_data: Dict[str, Any]):
        """Save user model data"""
        try:
            self.db.execute_update(
                """INSERT OR REPLACE INTO user_models (user_id, model_data)
                   VALUES (?, ?)""",
                (user_id, json.dumps(model_data))
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to save user model: {e}")
    
    def get_user_model(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user model data"""
        try:
            rows = self.db.execute_query(
                "SELECT model_data FROM user_models WHERE user_id = ?",
                (user_id,)
            )
            
            if not rows:
                return None
            
            return json.loads(rows[0]['model_data'])
            
        except Exception as e:
            raise RuntimeError(f"Failed to get user model: {e}")
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Save user preferences (part of user model)"""
        try:
            # Get existing model or create new one
            model_data = self.get_user_model(user_id) or {}
            model_data['preferences'] = preferences
            
            self.save_user_model(user_id, model_data)
            
        except Exception as e:
            raise RuntimeError(f"Failed to save user preferences: {e}")
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        try:
            model_data = self.get_user_model(user_id)
            return model_data.get('preferences') if model_data else None
            
        except Exception as e:
            raise RuntimeError(f"Failed to get user preferences: {e}")
    
    def track_interaction(self, interaction_data: Dict[str, Any]):
        """Track a user interaction"""
        try:
            self.db.execute_update(
                """INSERT INTO user_interactions 
                   (user_id, session_id, project_id, interaction_type, file_path, data, ip_address, user_agent)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    interaction_data.get('user_id'),
                    interaction_data.get('session_id'),
                    interaction_data.get('project_id'),
                    interaction_data.get('type'),
                    interaction_data.get('file_path'),
                    json.dumps(interaction_data.get('data', {})),
                    interaction_data.get('ip_address'),
                    interaction_data.get('user_agent')
                )
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to track interaction: {e}")
    
    def get_user_interactions(self, user_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get user interactions"""
        try:
            rows = self.db.execute_query(
                """SELECT * FROM user_interactions 
                   WHERE user_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (user_id, limit)
            )
            
            interactions = []
            for row in rows:
                interaction = dict(row)
                interaction['data'] = json.loads(row['data']) if row['data'] else {}
                interactions.append(interaction)
            
            return interactions
            
        except Exception as e:
            raise RuntimeError(f"Failed to get user interactions: {e}")
    
    def add_bookmark(self, user_id: str, project_id: str, file_path: str):
        """Add a bookmark"""
        try:
            self.db.execute_update(
                """INSERT OR IGNORE INTO bookmarks (user_id, project_id, file_path)
                   VALUES (?, ?, ?)""",
                (user_id, project_id, file_path)
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to add bookmark: {e}")
    
    def remove_bookmark(self, user_id: str, project_id: str, file_path: str):
        """Remove a bookmark"""
        try:
            self.db.execute_update(
                """DELETE FROM bookmarks 
                   WHERE user_id = ? AND project_id = ? AND file_path = ?""",
                (user_id, project_id, file_path)
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to remove bookmark: {e}")
    
    def get_bookmarks(self, user_id: str, project_id: str = None) -> List[Dict[str, Any]]:
        """Get user bookmarks"""
        try:
            if project_id:
                rows = self.db.execute_query(
                    """SELECT * FROM bookmarks 
                       WHERE user_id = ? AND project_id = ?
                       ORDER BY created_at DESC""",
                    (user_id, project_id)
                )
            else:
                rows = self.db.execute_query(
                    """SELECT * FROM bookmarks 
                       WHERE user_id = ?
                       ORDER BY created_at DESC""",
                    (user_id,)
                )
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            raise RuntimeError(f"Failed to get bookmarks: {e}")
    
    def clear_bookmarks(self, user_id: str, project_id: str = None):
        """Clear user bookmarks"""
        try:
            if project_id:
                self.db.execute_update(
                    "DELETE FROM bookmarks WHERE user_id = ? AND project_id = ?",
                    (user_id, project_id)
                )
            else:
                self.db.execute_update(
                    "DELETE FROM bookmarks WHERE user_id = ?",
                    (user_id,)
                )
                
        except Exception as e:
            raise RuntimeError(f"Failed to clear bookmarks: {e}")
