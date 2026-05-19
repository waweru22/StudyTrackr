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
        
    # ── Session-Derived Learning Insights ──
    from sqlalchemy import func

    completed_sessions = StudySession.query.filter(
        StudySession.user_id == user_id,
        StudySession.end_time != None
    )

    total_sessions = completed_sessions.count()

    # Compute aggregate stats used below
    avg_efficacy = 0.0
    dominant_env = 'None'
    insights = []

    if total_sessions == 0:
        insights.append({
            'type': 'info',
            'text': 'Complete your first session to see your learning insights.'
        })
    else:
        all_sessions = completed_sessions.all()

        # ── Average session score ──
        scores = [s.success_score for s in all_sessions if s.success_score is not None]
        avg_efficacy = round(sum(scores) / len(scores), 1) if scores else 0.0
        if avg_efficacy > 0:
            insights.append({
                'type': 'positive' if avg_efficacy >= 3.5 else 'neutral',
                'text': f"Your average session effectiveness score is {avg_efficacy}/5."
            })

        # ── Most common study environment ──
        envs = [s.environment for s in all_sessions if s.environment]
        if envs:
            from collections import Counter
            env_counts = Counter(envs)
            top_env, top_count = env_counts.most_common(1)[0]
            pct = round(top_count / len(envs) * 100)
            dominant_env = top_env
            insights.append({
                'type': 'positive',
                'text': f"{pct}% of your sessions were completed in {top_env}."
            })

        # ── Peak study day ──
        days = [s.start_time.strftime('%A') for s in all_sessions if s.start_time]
        if days:
            from collections import Counter as DayCounter
            day_counts = DayCounter(days)
            top_day, _ = day_counts.most_common(1)[0]
            insights.append({
                'type': 'info',
                'text': f"You complete more sessions on {top_day}s than any other day."
            })

        # ── Average session length ──
        durations = [s.duration_minutes for s in all_sessions if s.duration_minutes and s.duration_minutes > 0]
        if durations:
            avg_dur = round(sum(durations) / len(durations))
            insights.append({
                'type': 'info',
                'text': f"Your average focus session lasts {avg_dur} minutes."
            })

        # ── Most productive time of day ──
        hours = [s.start_time.hour for s in all_sessions if s.start_time]
        if hours:
            avg_hour = round(sum(hours) / len(hours))
            if avg_hour < 12:
                window = 'in the morning'
            elif avg_hour < 17:
                window = 'in the afternoon'
            else:
                window = 'in the evening'
            insights.append({
                'type': 'positive',
                'text': f"Your most productive sessions tend to happen {window}."
            })

        # ── Best performing social setting ──
        social_scores: dict[str, list[float]] = {}
        for s in all_sessions:
            if s.social_setting and s.success_score is not None:
                social_scores.setdefault(s.social_setting, []).append(s.success_score)
        if social_scores:
            best_setting = max(social_scores, key=lambda k: sum(social_scores[k]) / len(social_scores[k]))
            insights.append({
                'type': 'positive',
                'text': f"You perform best when studying {best_setting.lower()}."
            })

        # ── Completion rate ──
        on_time = [s for s in all_sessions if s.completed_on_time is True]
        if total_sessions > 0:
            comp_pct = round(len(on_time) / total_sessions * 100)
            insights.append({
                'type': 'positive' if comp_pct >= 70 else 'warning',
                'text': f"{comp_pct}% of your sessions were completed on time."
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
        'completed_on_time': s.completed_on_time,
    } for s in sessions]), 200
