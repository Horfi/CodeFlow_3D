# backend/src/services/git/GitCloner.py
import subprocess
import os
import shutil
from typing import Optional

class GitCloner:
    """Git repository cloning utilities"""
    
    @staticmethod
    def clone(git_url: str, target_path: str, depth: int = 1) -> bool:
        """Clone a Git repository"""
        try:
            # Remove target directory if it exists
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            
            # Ensure parent directory exists
            parent_dir = os.path.dirname(target_path)
            os.makedirs(parent_dir, exist_ok=True)
            
            # Build git clone command
            cmd = ['git', 'clone']
            
            if depth > 0:
                cmd.extend(['--depth', str(depth)])
            
            cmd.extend(['--single-branch', git_url, target_path])
            
            # Execute git clone
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"Git clone failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("Git clone timed out")
            return False
        except FileNotFoundError:
            print("Git command not found. Please install Git.")
            return False
        except Exception as e:
            print(f"Git clone error: {e}")
            return False
    
    @staticmethod
    def is_git_available() -> bool:
        """Check if git command is available"""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False