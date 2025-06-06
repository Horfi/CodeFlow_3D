# backend/src/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from api.routes.repository_routes import repository_bp
from api.routes.graph_routes import graph_bp
from api.routes.file_routes import file_bp
from api.routes.analytics_routes import analytics_bp
from api.routes.user_model_routes import user_model_bp
from api.middleware.cors_handler import setup_cors
from api.middleware.error_handler import setup_error_handlers
from api.middleware.analytics_middleware import AnalyticsMiddleware
from database.SQLiteManager import SQLiteManager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    db_manager = SQLiteManager(app.config['DATABASE_URL'])
    db_manager.init_db()
    
    # Setup CORS
    setup_cors(app)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Setup analytics middleware
    analytics_middleware = AnalyticsMiddleware()
    app.before_request(analytics_middleware.before_request)
    app.after_request(analytics_middleware.after_request)
    
    # Register blueprints
    app.register_blueprint(repository_bp, url_prefix='/api/repository')
    app.register_blueprint(graph_bp, url_prefix='/api/graph')
    app.register_blueprint(file_bp, url_prefix='/api/files')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(user_model_bp, url_prefix='/api/user')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    
    # Global exception handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({
                'error': e.description,
                'status_code': e.code
            }), e.code
        
        # Log the error
        app.logger.error(f"Unhandled exception: {str(e)}")
        
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
