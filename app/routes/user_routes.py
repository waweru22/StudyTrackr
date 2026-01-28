from flask import Blueprint, jsonify
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
            'streak_count': user.streak_count
        })
        
    return jsonify(response), 200
