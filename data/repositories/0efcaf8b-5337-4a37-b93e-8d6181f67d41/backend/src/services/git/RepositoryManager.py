# backend/src/services/git/RepositoryManager.py
import os
import shutil
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any

from config import Config
from utils.FileUtils import FileUtils
from utils.ValidationUtils import ValidationUtils

class RepositoryManager:
    """Manages Git repository operations"""
    
    def __init__(self):
        self.storage_path = Config.REPOSITORY_STORAGE
        os.makedirs(self.storage_path, exist_ok=True)
    
    def clone_repository(self, git_url: str, project_id: str) -> str:
        """Clone a Git repository"""
        try:
            # Validate Git URL
            if not ValidationUtils.is_valid_git_url(git_url):
                raise ValueError("Invalid Git URL format")
            
            # Create project directory
            repo_path = os.path.join(self.storage_path, project_id)
            
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            
            # Clone repository with limited depth for performance
            cmd = [
                'git', 'clone',
                '--depth', '1',
                '--single-branch',
                git_url,
                repo_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Git clone failed: {result.stderr}")
            
            # Check repository size
            repo_size = FileUtils.get_directory_size(repo_path)
            if repo_size > Config.MAX_REPOSITORY_SIZE:
                shutil.rmtree(repo_path)
                raise ValueError("Repository size exceeds maximum allowed size")
            
            # Remove .git directory to save space
            git_dir = os.path.join(repo_path, '.git')
            if os.path.exists(git_dir):
                shutil.rmtree(git_dir)
            
            return repo_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Repository clone timed out")
        except Exception as e:
            # Clean up on failure
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            raise e
    
    def get_repository_path(self, project_id: str) -> Optional[str]:
        """Get the file system path for a project"""
        if not ValidationUtils.is_valid_uuid(project_id):
            return None
        
        repo_path = os.path.join(self.storage_path, project_id)
        return repo_path if os.path.exists(repo_path) else None
    
    def delete_repository(self, project_id: str) -> bool:
        """Delete a cloned repository"""
        repo_path = self.get_repository_path(project_id)
        if repo_path and os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            return True
        return False
    
    def get_repository_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a repository"""
        repo_path = self.get_repository_path(project_id)
        if not repo_path:
            return None
        
        try:
            file_count = 0
            total_size = 0
            languages = set()
            
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if FileUtils.is_allowed_file(file):
                        file_count += 1
                        total_size += os.path.getsize(file_path)
                        
                        # Detect language
                        language = FileUtils.detect_language(file)
                        if language:
                            languages.add(language)
            
            return {
                'projectId': project_id,
                'fileCount': file_count,
                'totalSize': total_size,
                'languages': list(languages),
                'lastModified': datetime.fromtimestamp(
                    os.path.getmtime(repo_path)
                ).isoformat()
            }
            
        except Exception:
            return None
