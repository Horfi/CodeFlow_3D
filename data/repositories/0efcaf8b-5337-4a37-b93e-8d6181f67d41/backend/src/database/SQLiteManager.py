# backend/src/database/SQLiteManager.py
import sqlite3
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

class SQLiteManager:
    """SQLite database manager for CodeFlow 3D"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    def init_db(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript("""
                    -- Projects table
                    CREATE TABLE IF NOT EXISTS projects (
                        id TEXT PRIMARY KEY,
                        git_url TEXT NOT NULL,
                        version TEXT NOT NULL CHECK (version IN ('personalized', 'random')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        status TEXT DEFAULT 'active'
                    );
                    
                    -- Graph data table
                    CREATE TABLE IF NOT EXISTS graph_data (
                        project_id TEXT PRIMARY KEY,
                        nodes TEXT NOT NULL,
                        edges TEXT NOT NULL,
                        metrics TEXT,
                        centrality_scores TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                    );
                    
                    -- User models table
                    CREATE TABLE IF NOT EXISTS user_models (
                        user_id TEXT PRIMARY KEY,
                        model_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    -- User interactions table
                    CREATE TABLE IF NOT EXISTS user_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        session_id TEXT,
                        project_id TEXT,
                        interaction_type TEXT NOT NULL,
                        file_path TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data TEXT,
                        ip_address TEXT,
                        user_agent TEXT
                    );
                    
                    -- Bookmarks table
                    CREATE TABLE IF NOT EXISTS bookmarks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        project_id TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, project_id, file_path)
                    );
                    
                    -- Analytics sessions table
                    CREATE TABLE IF NOT EXISTS analytics_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ended_at TIMESTAMP,
                        project_id TEXT,
                        version TEXT,
                        interaction_count INTEGER DEFAULT 0,
                        duration_seconds INTEGER,
                        metadata TEXT
                    );
                    
                    -- Create indexes for better performance
                    CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions (user_id);
                    CREATE INDEX IF NOT EXISTS idx_user_interactions_session_id ON user_interactions (session_id);
                    CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp ON user_interactions (timestamp);
                    CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id ON bookmarks (user_id);
                    CREATE INDEX IF NOT EXISTS idx_bookmarks_project_id ON bookmarks (project_id);
                """)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            self.logger.error(f"Update execution failed: {e}")
            raise
