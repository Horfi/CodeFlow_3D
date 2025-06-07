# backend/src/api/routes/repository_routes.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, NotFound
import uuid
import os
import traceback
from datetime import datetime

repository_bp = Blueprint('repository', __name__)

@repository_bp.route('/analyze', methods=['POST'])
def analyze_repository():
    """Analyze a Git repository and build dependency graph"""
    try:
        data = request.get_json()
        git_url = data.get('gitUrl')
        version = data.get('version', 'personalized')
        
        # Log the request
        current_app.logger.info(f"Repository analysis request: {git_url}, version: {version}")
        
        # Validate input
        if not git_url:
            raise BadRequest('Git URL is required')
        
        from utils.ValidationUtils import ValidationUtils
        if not ValidationUtils.is_valid_git_url(git_url):
            raise BadRequest('Invalid Git URL format')
        
        if version not in ['personalized', 'random']:
            raise BadRequest('Version must be "personalized" or "random"')
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        current_app.logger.info(f"Generated project ID: {project_id}")
        
        # Try to import and initialize services
        try:
            from services.git.RepositoryManager import RepositoryManager
            repo_manager = RepositoryManager()
            current_app.logger.info("RepositoryManager initialized")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize RepositoryManager: {e}")
            return jsonify({
                'error': f'Repository manager initialization failed: {str(e)}',
                'status': 'error'
            }), 500
        
        # Clone repository
        try:
            current_app.logger.info(f"Attempting to clone repository: {git_url}")
            repo_path = repo_manager.clone_repository(git_url, project_id)
            current_app.logger.info(f"Repository cloned to: {repo_path}")
        except Exception as e:
            current_app.logger.error(f"Repository cloning failed: {e}")
            return jsonify({
                'error': f'Repository cloning failed: {str(e)}',
                'status': 'error',
                'details': 'Make sure Git is installed and the repository is accessible'
            }), 500
        
        # Try to build dependency graph
        try:
            from services.graph.GraphBuilder import GraphBuilder
            graph_builder = GraphBuilder()
            current_app.logger.info("GraphBuilder initialized")
            
            graph_data = graph_builder.build_graph(repo_path)
            current_app.logger.info(f"Graph built with {len(graph_data.get('nodes', []))} nodes and {len(graph_data.get('edges', []))} edges")
        except Exception as e:
            current_app.logger.error(f"Graph building failed: {e}")
            # Clean up cloned repo on failure
            if os.path.exists(repo_path):
                import shutil
                shutil.rmtree(repo_path)
            return jsonify({
                'error': f'Graph building failed: {str(e)}',
                'status': 'error',
                'details': 'Failed to analyze repository structure'
            }), 500
        
        # Apply version-specific processing
        try:
            from services.personalization.PersonalizationFactory import PersonalizationFactory
            personalization_factory = PersonalizationFactory()
            processor = personalization_factory.create_graph_processor(version)
            processed_graph = processor.process_graph(graph_data)
            current_app.logger.info("Graph processing completed")
        except Exception as e:
            current_app.logger.error(f"Graph processing failed: {e}")
            processed_graph = graph_data  # Use unprocessed graph as fallback
        
        # Try to save graph data
        try:
            from database.GraphDataManager import GraphDataManager
            graph_data_manager = GraphDataManager(current_app.config.get('DB_MANAGER'))
            
            metadata = {
                'git_url': git_url,
                'version': version,
                'created_at': datetime.utcnow().isoformat(),
                'node_count': len(processed_graph.get('nodes', [])),
                'edge_count': len(processed_graph.get('edges', []))
            }
            
            graph_data_manager.save_graph(project_id, processed_graph, metadata)
            current_app.logger.info("Graph data saved to database")
        except Exception as e:
            current_app.logger.error(f"Database save failed: {e}")
            # Continue without failing - return the data even if DB save fails
            current_app.logger.warning("Continuing without database save")
        
        return jsonify({
            'projectId': project_id,
            'status': 'success',
            'nodeCount': len(processed_graph.get('nodes', [])),
            'edgeCount': len(processed_graph.get('edges', [])),
            'version': version,
            'message': 'Repository analyzed successfully'
        })
        
    except BadRequest as e:
        current_app.logger.warning(f"Bad request: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in repository analysis: {e}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'status': 'error',
            'details': 'Check server logs for more information'
        }), 500

@repository_bp.route('/<project_id>/status', methods=['GET'])
def get_repository_status(project_id):
    """Get the status of a repository analysis"""
    try:
        from utils.ValidationUtils import ValidationUtils
        # Validate project ID
        if not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Invalid project ID format')
        
        try:
            from database.GraphDataManager import GraphDataManager
            graph_data_manager = GraphDataManager(current_app.config.get('DB_MANAGER'))
            
            # Get project metadata
            project_data = graph_data_manager.get_project_metadata(project_id)
            
            if not project_data:
                raise NotFound('Project not found')
            
            return jsonify({
                'projectId': project_id,
                'status': 'completed',
                'metadata': project_data
            })
        except Exception as e:
            current_app.logger.error(f"Error getting project status: {e}")
            return jsonify({
                'projectId': project_id,
                'status': 'unknown',
                'error': str(e)
            })
        
    except BadRequest as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error in get_repository_status: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@repository_bp.route('/<project_id>', methods=['DELETE'])
def delete_repository(project_id):
    """Delete a repository and its associated data"""
    try:
        from utils.ValidationUtils import ValidationUtils
        # Validate project ID
        if not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Invalid project ID format')
        
        # Delete repository files
        try:
            from services.git.RepositoryManager import RepositoryManager
            repo_manager = RepositoryManager()
            repo_manager.delete_repository(project_id)
        except Exception as e:
            current_app.logger.warning(f"Failed to delete repository files: {e}")
        
        # Delete graph data
        try:
            from database.GraphDataManager import GraphDataManager
            graph_data_manager = GraphDataManager(current_app.config.get('DB_MANAGER'))
            graph_data_manager.delete_project(project_id)
        except Exception as e:
            current_app.logger.warning(f"Failed to delete graph data: {e}")
        
        return jsonify({
            'projectId': project_id,
            'status': 'deleted'
        })
        
    except BadRequest as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error in delete_repository: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500