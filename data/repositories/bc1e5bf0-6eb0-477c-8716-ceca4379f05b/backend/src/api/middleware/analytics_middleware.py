
# backend/src/api/middleware/analytics_middleware.py
from flask import request, g
import time
import logging

class AnalyticsMiddleware:
    """Middleware for tracking request analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def before_request(self):
        """Execute before each request"""
        g.start_time = time.time()
        g.user_id = request.headers.get('X-User-ID')
        g.session_id = request.headers.get('X-Session-ID')
    
    def after_request(self, response):
        """Execute after each request"""
        try:
            duration = time.time() - g.start_time
            
            # Log request details
            self.logger.info(f"Request: {request.method} {request.path} "
                           f"Duration: {duration:.3f}s "
                           f"Status: {response.status_code} "
                           f"User: {g.get('user_id', 'anonymous')}")
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{duration:.3f}"
            
        except Exception as e:
            self.logger.error(f"Analytics middleware error: {e}")
        
        return response