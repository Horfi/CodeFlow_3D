# backend/src/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import os
import sys
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'
    
    # Database configuration
    app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///codeflow.db')
    
    # File storage paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['REPOSITORY_STORAGE'] = os.path.join(BASE_DIR, '../../data/repositories')
    app.config['CACHE_STORAGE'] = os.path.join(BASE_DIR, '../../data/cache')
    app.config['ANALYTICS_STORAGE'] = os.path.join(BASE_DIR, '../../data/analytics')
    
    # CORS settings
    app.config['CORS_ORIGINS'] = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # Create data directories
    for directory in [app.config['REPOSITORY_STORAGE'], app.config['CACHE_STORAGE'], app.config['ANALYTICS_STORAGE']]:
        os.makedirs(directory, exist_ok=True)
        app.logger.info(f"Created directory: {directory}")
    
    # Initialize database
    try:
        from database.SQLiteManager import SQLiteManager
        db_path = app.config['DATABASE_URL'].replace('sqlite:///', '')
        db_manager = SQLiteManager(db_path)
        db_manager.init_db()
        app.config['DB_MANAGER'] = db_manager
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")
        # Continue without database for now
        app.config['DB_MANAGER'] = None
    
    # Setup CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-User-ID', 'X-Session-ID'],
         supports_credentials=True)
    
    # Setup error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred'
        }), 500
    
    # Setup analytics middleware
    try:
        from api.middleware.analytics_middleware import AnalyticsMiddleware
        analytics_middleware = AnalyticsMiddleware()
        app.before_request(analytics_middleware.before_request)
        app.after_request(analytics_middleware.after_request)
        app.logger.info("Analytics middleware initialized")
    except Exception as e:
        app.logger.warning(f"Analytics middleware initialization failed: {e}")
    
    # Register blueprints with error handling
    blueprints = [
        ('api.routes.repository_routes', 'repository_bp', '/api/repository'),
        ('api.routes.graph_routes', 'graph_bp', '/api/graph'),
        ('api.routes.file_routes', 'file_bp', '/api/files'),
        ('api.routes.analytics_routes', 'analytics_bp', '/api/analytics'),
        ('api.routes.user_model_routes', 'user_model_bp', '/api/user'),
    ]
    
    for module_name, blueprint_name, url_prefix in blueprints:
        try:
            module = __import__(module_name, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            app.logger.info(f"Registered blueprint: {blueprint_name}")
        except Exception as e:
            app.logger.error(f"Failed to register blueprint {blueprint_name}: {e}")
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        # Check system status
        status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': 'connected' if app.config.get('DB_MANAGER') else 'disconnected'
        }
        
        # Check Git availability
        try:
            import subprocess
            result = subprocess.run(['git', '--version'], capture_output=True, timeout=5)
            status['git'] = 'available' if result.returncode == 0 else 'unavailable'
        except Exception:
            status['git'] = 'unavailable'
        
        return jsonify(status)
    
    # Basic bookmarks endpoints
    @app.route('/api/bookmarks', methods=['GET'])
    def get_bookmarks():
        """Get user bookmarks"""
        try:
            if not app.config.get('DB_MANAGER'):
                return jsonify([])  # Return empty if no database
            
            from database.UserDataManager import UserDataManager
            user_id = request.headers.get('X-User-ID', 'anonymous')
            project_id = request.args.get('project_id')
            
            user_data_manager = UserDataManager(app.config['DB_MANAGER'])
            bookmarks = user_data_manager.get_bookmarks(user_id, project_id)
            
            return jsonify(bookmarks)
        except Exception as e:
            app.logger.error(f"Error getting bookmarks: {e}")
            return jsonify([])  # Return empty array on error
    
    @app.route('/api/bookmarks', methods=['POST'])
    def add_bookmark():
        """Add a bookmark"""
        try:
            if not app.config.get('DB_MANAGER'):
                return jsonify({'error': 'Database not available'}), 503
            
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
            app.logger.error(f"Error adding bookmark: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bookmarks/<path:file_path>', methods=['DELETE'])
    def remove_bookmark(file_path):
        """Remove a bookmark"""
        try:
            if not app.config.get('DB_MANAGER'):
                return jsonify({'error': 'Database not available'}), 503
            
            from database.UserDataManager import UserDataManager
            user_id = request.headers.get('X-User-ID', 'anonymous')
            project_id = request.args.get('project_id', 'default')
            
            user_data_manager = UserDataManager(app.config['DB_MANAGER'])
            user_data_manager.remove_bookmark(user_id, project_id, file_path)
            
            return jsonify({'status': 'removed'})
        except Exception as e:
            app.logger.error(f"Error removing bookmark: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Basic project endpoint
    @app.route('/api/project/<project_id>')
    def get_project(project_id):
        """Get project data"""
        try:
            if not app.config.get('DB_MANAGER'):
                return jsonify({'error': 'Database not available'}), 503
            
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
            app.logger.error(f"Error getting project: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Search endpoint
    @app.route('/api/search', methods=['POST'])
    def search_files():
        """Search files in project"""
        try:
            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({'error': 'Query is required'}), 400
            
            query = data['query'].lower()
            project_id = data.get('projectId')
            
            if not app.config.get('DB_MANAGER') or not project_id:
                return jsonify([])
            
            # Simple search implementation
            from database.GraphDataManager import GraphDataManager
            graph_data_manager = GraphDataManager(app.config['DB_MANAGER'])
            graph_data = graph_data_manager.get_graph(project_id)
            
            if not graph_data:
                return jsonify([])
            
            # Filter nodes by query
            results = []
            for node in graph_data.get('nodes', []):
                node_name = node.get('name', '').lower()
                node_path = node.get('path', '').lower()
                
                if query in node_name or query in node_path:
                    results.append({
                        **node,
                        'relevanceScore': 0.8 if query in node_name else 0.5
                    })
            
            # Sort by relevance
            results.sort(key=lambda x: x.get('relevanceScore', 0), reverse=True)
            
            return jsonify(results[:20])  # Return top 20 results
        except Exception as e:
            app.logger.error(f"Error in search: {e}")
            return jsonify([])
    
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
        import traceback
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500,
            'message': str(e)
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.logger.info(f"Starting CodeFlow 3D Backend on port {port}")
    app.logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )