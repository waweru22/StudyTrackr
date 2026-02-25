from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
def get_users():
    # Order by ID Descending (Newest first)
    users = User.query.order_by(User.id.desc()).all()
    
    response = []
    for user in users:
        response.append({
            # Identity
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'level': user.level,
            
            # Cognitive Profile
            'base_template': user.base_template,
            'peak_time': user.peak_time,
            'focus_threshold': user.focus_threshold,
            'daily_cognitive_budget': user.daily_cognitive_budget,
            
            # Progress
            'xp_points': user.xp_points,
            'badge': user.badge,
            'streak_count': user.streak_count,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            
        })
        
    return jsonify(response), 200

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    # Helper to get current user ID
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'level': user.level,
        'phone_number': user.phone_number if hasattr(user, 'phone_number') else "", 
        'role': user.role,
        'xp_points': user.xp_points,
        'badge': user.badge,
        'streak_count': user.streak_count,
        'base_template': user.base_template,
        'peak_time': user.peak_time,
        'focus_threshold': user.focus_threshold,
        'learning_style': user.learning_style,
        'daily_cognitive_budget': user.daily_cognitive_budget,
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    from flask import request
    data = request.get_json()
    
    # Update Allowed Fields
    if 'username' in data: user.username = data['username']
    if 'phone_number' in data: user.phone_number = data['phone_number']
    if 'level' in data: user.level = data['level']
    
    # Commit
    from app import db
    db.session.commit()
    
    return jsonify({"message": "Profile updated successfully", "user": {
        'id': user.id,
        'username': user.username,
        'phone_number': user.phone_number,
        'level': user.level
    }}), 200

@user_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_user_courses():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify([{
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'credits': c.credits,
        'weight': c.weight
    } for c in user.courses]), 200
