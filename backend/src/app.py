# Update the main app.py to fix database initialization
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
    
    # Create data directories
    os.makedirs(app.config['REPOSITORY_STORAGE'], exist_ok=True)
    os.makedirs(app.config['CACHE_STORAGE'], exist_ok=True)
    os.makedirs(app.config['ANALYTICS_STORAGE'], exist_ok=True)
    
    # Initialize database
    db_manager = SQLiteManager(app.config['DATABASE_URL'].replace('sqlite:///', ''))
    db_manager.init_db()
    
    # Store db_manager in app config for access by other components
    app.config['DB_MANAGER'] = db_manager
    
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
    
    # Basic bookmarks endpoints
    @app.route('/api/bookmarks', methods=['GET'])
    def get_bookmarks():
        """Get user bookmarks"""
        try:
            from database.UserDataManager import UserDataManager
            user_id = request.headers.get('X-User-ID', 'anonymous')
            project_id = request.args.get('project_id')
            
            user_data_manager = UserDataManager(app.config['DB_MANAGER'])
            bookmarks = user_data_manager.get_bookmarks(user_id, project_id)
            
            return jsonify(bookmarks)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bookmarks', methods=['POST'])
    def add_bookmark():
        """Add a bookmark"""
        try:
            from database.UserDataManager import UserDataManager
            user_id = request.headers.get('X-User-ID', 'anonymous')
            data = request.get_json()
            
            if not data or 'filePath' not in data:
                return jsonify({'error': 'filePath is required'}), 400
            
            project_id = data.get('project_id', 'default')
            file_path = data['filePath']
            
            user_data_manager = UserDataManager(app.config['DB_MANAGER'])
            user_data_manager.add_bookmark(user_id, project_id, file_path)
            
            return jsonify({'status': 'added'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bookmarks/<path:file_path>', methods=['DELETE'])
    def remove_bookmark(file_path):
        """Remove a bookmark"""
        try:
            from database.UserDataManager import UserDataManager
            user_id = request.headers.get('X-User-ID', 'anonymous')
            project_id = request.args.get('project_id', 'default')
            
            user_data_manager = UserDataManager(app.config['DB_MANAGER'])
            user_data_manager.remove_bookmark(user_id, project_id, file_path)
            
            return jsonify({'status': 'removed'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bookmarks', methods=['DELETE'])
    def clear_bookmarks():
        """Clear all bookmarks"""
        try:
            from database.UserDataManager import UserDataManager
            user_id = request.headers.get('X-User-ID', 'anonymous')
            project_id = request.args.get('project_id')
            
            user_data_manager = UserDataManager(app.config['DB_MANAGER'])
            user_data_manager.clear_bookmarks(user_id, project_id)
            
            return jsonify({'status': 'cleared'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Basic project endpoint
    @app.route('/api/project/<project_id>')
    def get_project(project_id):
        """Get project data"""
        try:
            from database.GraphDataManager import GraphDataManager
            graph_data_manager = GraphDataManager(app.config['DB_MANAGER'])
            
            # Get graph data
            graph_data = graph_data_manager.get_graph(project_id)
            if not graph_data:
                return jsonify({'error': 'Project not found'}), 404
            
            # Get project metadata
            metadata = graph_data_manager.get_project_metadata(project_id)
            
            return jsonify({
                'graph': graph_data,
                'metadata': metadata
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Search endpoint
    @app.route('/api/search', methods=['POST'])
    def search_files():
        """Search files in project"""
        try:
            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({'error': 'Query is required'}), 400
            
            query = data['query']
            project_id = data.get('projectId')
            
            # Simple search implementation
            from database.GraphDataManager import GraphDataManager
            graph_data_manager = GraphDataManager(app.config['DB_MANAGER'])
            graph_data = graph_data_manager.get_graph(project_id) if project_id else None
            
            if not graph_data:
                return jsonify([])
            
            # Filter nodes by query
            results = []
            for node in graph_data.get('nodes', []):
                if query.lower() in node.get('name', '').lower() or query.lower() in node.get('path', '').lower():
                    results.append({
                        **node,
                        'relevanceScore': 0.8 if query.lower() in node.get('name', '').lower() else 0.5
                    })
            
            # Sort by relevance
            results.sort(key=lambda x: x.get('relevanceScore', 0), reverse=True)
            
            return jsonify(results[:20])  # Return top 20 results
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
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


