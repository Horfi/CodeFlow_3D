# backend/src/api/routes/graph_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from database.GraphDataManager import GraphDataManager
from services.graph.CentralityCalculator import CentralityCalculator
from utils.ValidationUtils import ValidationUtils

graph_bp = Blueprint('graph', __name__)
graph_data_manager = GraphDataManager()
centrality_calculator = CentralityCalculator()

@graph_bp.route('/<project_id>', methods=['GET'])
def get_graph_data(project_id):
    """Get graph data for a project"""
    try:
        # Validate project ID
        if not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Invalid project ID format')
        
        # Get graph data
        graph_data = graph_data_manager.get_graph(project_id)
        
        if not graph_data:
            raise NotFound('Project not found')
        
        return jsonify(graph_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@graph_bp.route('/<project_id>/centrality', methods=['GET'])
def get_centrality_data(project_id):
    """Get centrality scores for graph nodes"""
    try:
        # Validate project ID
        if not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Invalid project ID format')
        
        # Get graph data
        graph_data = graph_data_manager.get_graph(project_id)
        
        if not graph_data:
            raise NotFound('Project not found')
        
        # Calculate centrality scores
        centrality_scores = centrality_calculator.calculate_all_centralities(graph_data)
        
        return jsonify(centrality_scores)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@graph_bp.route('/<project_id>', methods=['PUT'])
def update_graph_data(project_id):
    """Update graph data"""
    try:
        # Validate project ID
        if not ValidationUtils.is_valid_uuid(project_id):
            raise BadRequest('Invalid project ID format')
        
        data = request.get_json()
        if not data:
            raise BadRequest('Graph data is required')
        
        # Update graph data
        graph_data_manager.update_graph(project_id, data)
        
        return jsonify({
            'projectId': project_id,
            'status': 'updated'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
