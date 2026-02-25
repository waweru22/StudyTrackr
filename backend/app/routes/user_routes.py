from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.session import StudySession

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
        
    # ── Adaptation Insights ──
    from app.services.rule_engine import RuleEngine
    user_context = RuleEngine.get_user_context(user_id)

    dominant_env = user_context.get('dominant_environment', 'None')
    env_consistency = round(user_context.get('session_location_consistency', 0) * 100)
    avg_efficacy = round(user_context.get('avg_session_efficacy', 0), 1)

    total_sessions = StudySession.query.filter(
        StudySession.user_id == user_id,
        StudySession.end_time != None
    ).count()

    insights = []
    if total_sessions == 0:
        insights.append({
            'type': 'info',
            'text': 'No sessions logged yet. Complete your first session to start personalising your schedule.'
        })
    else:
        if dominant_env != 'None' and env_consistency >= 50:
            insights.append({
                'type': 'positive',
                'text': f"{env_consistency}% of your sessions have been in {dominant_env}. Your schedule prioritises conditions that match this environment."
            })

        if avg_efficacy >= 4.0:
            insights.append({
                'type': 'positive',
                'text': f"Your average session score is {avg_efficacy}/5. Feynman Technique blocks have been added for your highest-weight courses to match your strong performance."
            })
        elif avg_efficacy >= 2.5:
            insights.append({
                'type': 'neutral',
                'text': f"Your average session score is {avg_efficacy}/5. Your schedule is balanced between active recall and review sessions."
            })
        elif avg_efficacy > 0:
            insights.append({
                'type': 'warning',
                'text': f"Your average session score is {avg_efficacy}/5. Your schedule has shifted toward review techniques to consolidate before advancing."
            })

        if user_context.get('burnout_risk') == 'High':
            insights.append({
                'type': 'warning',
                'text': 'Two of your last three sessions were Low Energy. Your daily block count has been reduced to prevent burnout.'
            })
        else:
            insights.append({
                'type': 'positive',
                'text': 'No burnout risk detected. Your current block count and intensity are sustainable.'
            })

        peak_map = {
            'morning': '8am \u2013 11am',
            'afternoon': '1pm \u2013 4pm',
            'evening': '6pm \u2013 9pm',
            'night': '10pm \u2013 1am',
            'early_morning': '4am \u2013 7am'
        }
        peak_label = peak_map.get(str(user.peak_time or '').lower(), 'your stated peak time')
        insights.append({
            'type': 'info',
            'text': f"Your peak focus window is set to {peak_label}. Your highest-priority course is always scheduled in this slot."
        })

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
        'adaptation_insights': insights,
        'total_sessions': total_sessions,
        'avg_efficacy': avg_efficacy,
        'dominant_environment': dominant_env,
        'created_at': user.created_at.isoformat() if user.created_at else None,
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

@user_bp.route('/session-history', methods=['GET'])
@jwt_required()
def get_session_history():
    user_id = int(get_jwt_identity())

    sessions = StudySession.query.filter(
        StudySession.user_id == user_id,
        StudySession.end_time != None
    ).order_by(StudySession.start_time.desc()).limit(10).all()

    return jsonify([{
        'date': s.start_time.strftime('%d %b'),
        'day': s.start_time.strftime('%A'),
        'course_code': s.course.code if s.course else 'N/A',
        'environment': s.environment or 'Unknown',
        'vibe': s.vibe or 'Normal',
        'success_score': s.success_score or 0,
        'distraction_count': s.distraction_count or 0,
        'duration_minutes': s.duration_minutes or 0,
        'session_insight': s.session_insight or '',
        'mood_after': s.mood_after,
        'would_repeat': s.would_repeat,
    } for s in sessions]), 200
