# backend/src/api/routes/file_routes.py
from flask import Blueprint, request, jsonify, send_file
from werkzeug.exceptions import BadRequest, NotFound
import os

from services.git.RepositoryManager import RepositoryManager
from services.parsing.DependencyResolver import DependencyResolver
from utils.FileUtils import FileUtils
from utils.ValidationUtils import ValidationUtils

file_bp = Blueprint('files', __name__)
repo_manager = RepositoryManager()
dependency_resolver = DependencyResolver()

@file_bp.route('/<path:file_path>', methods=['GET'])
def get_file_content(file_path):
    """Get content of a specific file"""
    try:
        # Validate file path
        if not ValidationUtils.is_safe_path(file_path):
            raise BadRequest('Invalid file path')
        
        # Get project ID from query parameters
        project_id = request.args.get('project_id')
        if not project_id or not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Valid project ID is required')
        
        # Get repository path
        repo_path = repo_manager.get_repository_path(project_id)
        if not repo_path:
            raise NotFound('Project not found')
        
        # Construct full file path
        full_path = os.path.join(repo_path, file_path)
        
        # Validate file exists and is within repository
        if not FileUtils.is_safe_file(full_path, repo_path):
            raise BadRequest('Invalid file access')
        
        # Read and return file content
        content = FileUtils.read_file_content(full_path)
        
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@file_bp.route('/<path:file_path>', methods=['PUT'])
def save_file_content(file_path):
    """Save content to a specific file"""
    try:
        # Validate file path
        if not ValidationUtils.is_safe_path(file_path):
            raise BadRequest('Invalid file path')
        
        data = request.get_json()
        if not data or 'content' not in data:
            raise BadRequest('File content is required')
        
        content = data['content']
        project_id = data.get('project_id')
        
        if not project_id or not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Valid project ID is required')
        
        # Get repository path
        repo_path = repo_manager.get_repository_path(project_id)
        if not repo_path:
            raise NotFound('Project not found')
        
        # Construct full file path
        full_path = os.path.join(repo_path, file_path)
        
        # Validate file access
        if not FileUtils.is_safe_file(full_path, repo_path):
            raise BadRequest('Invalid file access')
        
        # Save file content
        FileUtils.write_file_content(full_path, content)
        
        return jsonify({
            'status': 'saved',
            'filePath': file_path
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@file_bp.route('/<path:file_path>/dependencies', methods=['GET'])
def get_file_dependencies(file_path):
    """Get dependencies for a specific file"""
    try:
        # Validate file path
        if not ValidationUtils.is_safe_path(file_path):
            raise BadRequest('Invalid file path')
        
        project_id = request.args.get('project_id')
        if not project_id or not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Valid project ID is required')
        
        # Get repository path
        repo_path = repo_manager.get_repository_path(project_id)
        if not repo_path:
            raise NotFound('Project not found')
        
        # Resolve dependencies
        dependencies = dependency_resolver.resolve_file_dependencies(
            os.path.join(repo_path, file_path)
        )
        
        return jsonify(dependencies)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@file_bp.route('/<path:file_path>/dependents', methods=['GET'])
def get_file_dependents(file_path):
    """Get files that depend on this file"""
    try:
        # Validate file path
        if not ValidationUtils.is_safe_path(file_path):
            raise BadRequest('Invalid file path')
        
        project_id = request.args.get('project_id')
        if not project_id or not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Valid project ID is required')
        
        # Get repository path
        repo_path = repo_manager.get_repository_path(project_id)
        if not repo_path:
            raise NotFound('Project not found')
        
        # Find reverse dependencies
        dependents = dependency_resolver.find_reverse_dependencies(
            os.path.join(repo_path, file_path), repo_path
        )
        
        return jsonify(dependents)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
