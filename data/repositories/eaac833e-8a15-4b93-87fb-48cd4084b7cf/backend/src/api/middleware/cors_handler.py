# backend/src/api/middleware/cors_handler.py
from flask_cors import CORS

def setup_cors(app):
    """Setup CORS configuration"""
    CORS(app, 
         origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-User-ID', 'X-Session-ID'],
         supports_credentials=True)