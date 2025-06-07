# backend/src/services/git/GitWatcher.py
import os
import time
from typing import Callable, Dict, Any

class GitWatcher:
    """Watches for changes in Git repositories"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.last_check = time.time()
        self.file_timestamps = {}
        self.callbacks = []
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback for file changes"""
        self.callbacks.append(callback)
    
    def check_for_changes(self) -> List[Dict[str, Any]]:
        """Check for file changes since last check"""
        changes = []
        
        if not os.path.exists(self.repo_path):
            return changes
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(file_path)
                    
                    # Check if file is new or modified
                    if file_path not in self.file_timestamps:
                        changes.append({
                            'type': 'added',
                            'path': file_path,
                            'timestamp': mtime
                        })
                    elif mtime > self.file_timestamps[file_path]:
                        changes.append({
                            'type': 'modified',
                            'path': file_path,
                            'timestamp': mtime
                        })
                    
                    self.file_timestamps[file_path] = mtime
                    
                except OSError:
                    continue
        
        # Check for deleted files
        current_files = set(self.file_timestamps.keys())
        actual_files = set()
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                actual_files.add(os.path.join(root, file))
        
        deleted_files = current_files - actual_files
        for deleted_file in deleted_files:
            changes.append({
                'type': 'deleted',
                'path': deleted_file,
                'timestamp': time.time()
            })
            del self.file_timestamps[deleted_file]
        
        # Notify callbacks
        for change in changes:
            for callback in self.callbacks:
                try:
                    callback(change)
                except Exception as e:
                    print(f"Callback error: {e}")
        
        self.last_check = time.time()
        return changes
    
    def start_watching(self, interval: int = 5):
        """Start watching for changes"""
        import threading
        import time
        
        def watch_loop():
            while True:
                try:
                    self.check_for_changes()
                    time.sleep(interval)
                except Exception as e:
                    print(f"Watcher error: {e}")
                    time.sleep(interval)
        
        thread = threading.Thread(target=watch_loop, daemon=True)
        thread.start()
        return thread