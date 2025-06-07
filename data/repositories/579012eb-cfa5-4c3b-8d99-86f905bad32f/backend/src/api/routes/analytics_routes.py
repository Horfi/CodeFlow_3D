# backend/src/api/routes/analytics_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta

from services.analytics.InteractionTracker import InteractionTracker
from services.analytics.MetricsCollector import MetricsCollector
from utils.ValidationUtils import ValidationUtils

analytics_bp = Blueprint('analytics', __name__)
interaction_tracker = InteractionTracker()
metrics_collector = MetricsCollector()

@analytics_bp.route('/interaction', methods=['POST'])
def track_interaction():
    """Track a user interaction"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Interaction data is required')
        
        # Validate required fields
        required_fields = ['type', 'timestamp']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f'{field} is required')
        
        # Add session and request metadata
        interaction_data = {
            **data,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'session_id': request.headers.get('X-Session-ID'),
            'user_id': request.headers.get('X-User-ID')
        }
        
        # Track interaction
        interaction_tracker.track_interaction(interaction_data)
        
        return jsonify({
            'status': 'tracked',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@analytics_bp.route('/batch', methods=['POST'])
def track_batch_interactions():
    """Track multiple interactions in batch"""
    try:
        data = request.get_json()
        if not data or 'events' not in data:
            raise BadRequest('Events array is required')
        
        events = data['events']
        if not isinstance(events, list):
            raise BadRequest('Events must be an array')
        
        # Process each event
        for event in events:
            # Add session metadata
            event_data = {
                **event,
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent')
            }
            interaction_tracker.track_interaction(event_data)
        
        return jsonify({
            'status': 'tracked',
            'count': len(events),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@analytics_bp.route('', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        # Parse query parameters
        time_range = request.args.get('range', '7d')
        user_id = request.args.get('user_id')
        session_id = request.args.get('session_id')
        
        # Calculate time range
        end_time = datetime.utcnow()
        if time_range == '1h':
            start_time = end_time - timedelta(hours=1)
        elif time_range == '24h':
            start_time = end_time - timedelta(days=1)
        elif time_range == '7d':
            start_time = end_time - timedelta(days=7)
        elif time_range == '30d':
            start_time = end_time - timedelta(days=30)
        else:
            raise BadRequest('Invalid time range')
        
        # Get analytics data
        analytics_data = metrics_collector.get_analytics(
            start_time=start_time,
            end_time=end_time,
            user_id=user_id,
            session_id=session_id
        )
        
        return jsonify(analytics_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500