# backend/src/utils/CacheUtils.py
import json
import os
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta

class CacheUtils:
    """Caching utilities"""
    
    def __init__(self, cache_dir: str = 'cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, data: str) -> str:
        """Generate cache key from data"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def set_cache(self, key: str, data: Any, ttl_hours: int = 24):
        """Set cache entry"""
        try:
            cache_data = {
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'expires': (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
            }
            
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
                
        except Exception as e:
            print(f"Failed to set cache: {e}")
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cache entry"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check expiration
            expires = datetime.fromisoformat(cache_data['expires'])
            if datetime.now() > expires:
                os.remove(cache_file)
                return None
            
            return cache_data['data']
            
        except Exception as e:
            print(f"Failed to get cache: {e}")
            return None