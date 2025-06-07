# backend/src/api/routes/repository_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound
import uuid
import os
from datetime import datetime

from services.git.RepositoryManager import RepositoryManager
from services.graph.GraphBuilder import GraphBuilder
from services.personalization.PersonalizationFactory import PersonalizationFactory
from database.GraphDataManager import GraphDataManager
from utils.ValidationUtils import ValidationUtils

repository_bp = Blueprint('repository', __name__)
repo_manager = RepositoryManager()
graph_builder = GraphBuilder()
graph_data_manager = GraphDataManager()

@repository_bp.route('/analyze', methods=['POST'])
def analyze_repository():
    """Analyze a Git repository and build dependency graph"""
    try:
        data = request.get_json()
        git_url = data.get('gitUrl')
        version = data.get('version', 'personalized')
        
        # Validate input
        if not git_url:
            raise BadRequest('Git URL is required')
        
        if not ValidationUtils.is_valid_git_url(git_url):
            raise BadRequest('Invalid Git URL format')
        
        if version not in ['personalized', 'random']:
            raise BadRequest('Version must be "personalized" or "random"')
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Clone repository
        repo_path = repo_manager.clone_repository(git_url, project_id)
        
        # Build dependency graph
        graph_data = graph_builder.build_graph(repo_path)
        
        # Apply version-specific processing
        personalization_factory = PersonalizationFactory()
        processor = personalization_factory.create_graph_processor(version)
        processed_graph = processor.process_graph(graph_data)
        
        # Save graph data
        graph_data_manager.save_graph(project_id, processed_graph, {
            'git_url': git_url,
            'version': version,
            'created_at': datetime.utcnow().isoformat(),
            'node_count': len(processed_graph.get('nodes', [])),
            'edge_count': len(processed_graph.get('edges', []))
        })
        
        return jsonify({
            'projectId': project_id,
            'status': 'success',
            'nodeCount': len(processed_graph.get('nodes', [])),
            'edgeCount': len(processed_graph.get('edges', [])),
            'version': version
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@repository_bp.route('/<project_id>/status', methods=['GET'])
def get_repository_status(project_id):
    """Get the status of a repository analysis"""
    try:
        # Validate project ID
        if not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Invalid project ID format')
        
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
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@repository_bp.route('/<project_id>', methods=['DELETE'])
def delete_repository(project_id):
    """Delete a repository and its associated data"""
    try:
        # Validate project ID
        if not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Invalid project ID format')
        
        # Delete repository files
        repo_manager.delete_repository(project_id)
        
        # Delete graph data
        graph_data_manager.delete_project(project_id)
        
        return jsonify({
            'projectId': project_id,
            'status': 'deleted'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
