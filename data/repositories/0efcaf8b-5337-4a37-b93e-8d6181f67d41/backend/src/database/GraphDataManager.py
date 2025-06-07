# backend/src/database/GraphDataManager.py
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from .SQLiteManager import SQLiteManager

class GraphDataManager:
    """Manages graph data storage and retrieval"""
    
    def __init__(self, db_manager: SQLiteManager = None):
        self.db = db_manager or SQLiteManager('codeflow.db')
    
    def save_graph(self, project_id: str, graph_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Save graph data for a project"""
        try:
            # Save project metadata
            self.db.execute_update(
                """INSERT OR REPLACE INTO projects (id, git_url, version, metadata)
                   VALUES (?, ?, ?, ?)""",
                (
                    project_id,
                    metadata.get('git_url', '') if metadata else '',
                    metadata.get('version', 'personalized') if metadata else 'personalized',
                    json.dumps(metadata) if metadata else '{}'
                )
            )
            
            # Save graph data
            self.db.execute_update(
                """INSERT OR REPLACE INTO graph_data 
                   (project_id, nodes, edges, metrics)
                   VALUES (?, ?, ?, ?)""",
                (
                    project_id,
                    json.dumps(graph_data.get('nodes', [])),
                    json.dumps(graph_data.get('edges', [])),
                    json.dumps(graph_data.get('metrics', {}))
                )
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to save graph data: {e}")
    
    def get_graph(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get graph data for a project"""
        try:
            rows = self.db.execute_query(
                """SELECT nodes, edges, metrics, centrality_scores 
                   FROM graph_data WHERE project_id = ?""",
                (project_id,)
            )
            
            if not rows:
                return None
            
            row = rows[0]
            return {
                'nodes': json.loads(row['nodes']),
                'edges': json.loads(row['edges']),
                'metrics': json.loads(row['metrics']) if row['metrics'] else {},
                'centrality_scores': json.loads(row['centrality_scores']) if row['centrality_scores'] else {}
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get graph data: {e}")
    
    def update_graph(self, project_id: str, graph_data: Dict[str, Any]):
        """Update existing graph data"""
        try:
            self.db.execute_update(
                """UPDATE graph_data 
                   SET nodes = ?, edges = ?, metrics = ?
                   WHERE project_id = ?""",
                (
                    json.dumps(graph_data.get('nodes', [])),
                    json.dumps(graph_data.get('edges', [])),
                    json.dumps(graph_data.get('metrics', {})),
                    project_id
                )
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to update graph data: {e}")
    
    def save_centrality_scores(self, project_id: str, centrality_scores: Dict[str, Any]):
        """Save centrality scores for a project"""
        try:
            self.db.execute_update(
                """UPDATE graph_data 
                   SET centrality_scores = ?
                   WHERE project_id = ?""",
                (json.dumps(centrality_scores), project_id)
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to save centrality scores: {e}")
    
    def get_project_metadata(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project metadata"""
        try:
            rows = self.db.execute_query(
                """SELECT * FROM projects WHERE id = ?""",
                (project_id,)
            )
            
            if not rows:
                return None
            
            row = rows[0]
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            
            return {
                'id': row['id'],
                'git_url': row['git_url'],
                'version': row['version'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'status': row['status'],
                **metadata
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get project metadata: {e}")
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all associated data"""
        try:
            affected = self.db.execute_update(
                "DELETE FROM projects WHERE id = ?",
                (project_id,)
            )
            return affected > 0
            
        except Exception as e:
            raise RuntimeError(f"Failed to delete project: {e}")
    
    def list_projects(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent projects"""
        try:
            rows = self.db.execute_query(
                """SELECT id, git_url, version, created_at, updated_at, status
                   FROM projects 
                   ORDER BY updated_at DESC 
                   LIMIT ?""",
                (limit,)
            )
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            raise RuntimeError(f"Failed to list projects: {e}")