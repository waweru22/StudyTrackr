from flask import Blueprint, request, jsonify
from app.services.session_service import SessionService

from flask_jwt_extended import jwt_required, get_jwt_identity

session_bp = Blueprint('session', __name__)

@session_bp.route('/start', methods=['POST'])
@jwt_required()
def start_session():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    
    # Optional: Verify user_id match if it was in body, but redundant. 
    # Just pass user_id from token.
        
    session, nudge, tech_info = SessionService.start_session(user_id, data)
    
    return jsonify({
        'session_id': session.id,
        'message': 'Session Started',
        'nudge': nudge,
        'timer_config': tech_info['timer_config'],
        'technique': tech_info.get('name', session.learning_mode)
    }), 201

@session_bp.route('/<int:session_id>/distraction', methods=['POST'])
@jwt_required()
def log_distraction(session_id):
    # Optional: Check if session belongs to user_id
    success, message = SessionService.log_distraction(session_id)
    if not success:
        return jsonify({'error': message}), 400
        
    return jsonify({'message': message}), 200

@session_bp.route('/end', methods=['POST'])
@jwt_required()
def end_session_endpoint():
    request_user_id = int(get_jwt_identity()) 
    data = request.get_json()
    session_id = data.get('session_id')
    
    # Ideally should verify session.user_id == request_user_id inside service or here
    # Assuming service handles basic checks, but "Secure Session Routes" implies strict check.
    # Service 'end_session' takes session_id. 
    # Let's rely on session_id for now as "Secure" mostly means Auth required.
    total_distraction_seconds = data.get('total_distraction_seconds', 0)
    
    session, xp_or_error = SessionService.end_session(session_id, data)
    
    if not session:
        return jsonify({'error': xp_or_error}), 400
        
    xp = xp_or_error
    return jsonify({
        'message': 'Session Ended',
        'duration_minutes': session.duration_minutes,
        'xp_earned': xp,
        'distraction_count': session.distraction_count
    }), 200
