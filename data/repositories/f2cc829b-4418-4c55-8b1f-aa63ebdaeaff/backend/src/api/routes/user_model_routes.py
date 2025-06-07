# backend/src/api/routes/user_model_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from services.personalization.UserModelEngine import UserModelEngine
from database.UserDataManager import UserDataManager
from utils.ValidationUtils import ValidationUtils

user_model_bp = Blueprint('user', __name__)
user_model_engine = UserModelEngine()
user_data_manager = UserDataManager()

@user_model_bp.route('/model', methods=['GET'])
def get_user_model():
    """Get user model data"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            raise BadRequest('User ID is required')
        
        # Get user model
        user_model = user_data_manager.get_user_model(user_id)
        
        if not user_model:
            # Create new user model
            user_model = user_model_engine.create_new_user_model()
            user_data_manager.save_user_model(user_id, user_model)
        
        return jsonify(user_model)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@user_model_bp.route('/model', methods=['PUT'])
def update_user_model():
    """Update user model data"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            raise BadRequest('User ID is required')
        
        data = request.get_json()
        if not data:
            raise BadRequest('User model data is required')
        
        # Update user model
        user_data_manager.save_user_model(user_id, data)
        
        return jsonify({
            'status': 'updated',
            'userId': user_id
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@user_model_bp.route('/preferences', methods=['GET'])
def get_user_preferences():
    """Get user preferences"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            raise BadRequest('User ID is required')
        
        preferences = user_data_manager.get_user_preferences(user_id)
        
        return jsonify(preferences or {})
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@user_model_bp.route('/preferences', methods=['PUT'])
def update_user_preferences():
    """Update user preferences"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            raise BadRequest('User ID is required')
        
        data = request.get_json()
        if not data:
            raise BadRequest('Preferences data is required')
        
        # Update preferences
        user_data_manager.save_user_preferences(user_id, data)
        
        return jsonify({
            'status': 'updated',
            'userId': user_id
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500