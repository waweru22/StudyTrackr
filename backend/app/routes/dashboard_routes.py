from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.session import StudySession, ScheduleBlock
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Real-time Trigger: Check for missed sessions
    from app.services.schedule_service import ScheduleService
    from app.services.gamification_service import GamificationService
    ScheduleService.check_missed_sessions(user_id)
    GamificationService.calculate_streak(user_id)
    
    # Next session: Must be (Today AND > Current Time AND upcoming) OR (Future Date AND upcoming)
    from datetime import timezone, timedelta
    LAGOS_TZ = timezone(timedelta(hours=1))
    now_lagos = datetime.now(LAGOS_TZ)
    today = now_lagos.date()
    current_time = now_lagos.time()
    
    # 1. Check for upcoming sessions LATER TODAY
    next_session = ScheduleBlock.query.filter_by(user_id=user_id, date=today)\
        .filter(
            ScheduleBlock.start_time > current_time,
            ScheduleBlock.status == 'upcoming'
        )\
        .order_by(ScheduleBlock.start_time.asc())\
        .first()
        
    # 2. If none today, check FUTURE DATES
    if not next_session:
        next_session = ScheduleBlock.query.filter(
            ScheduleBlock.user_id == user_id, 
            ScheduleBlock.date > today,
            ScheduleBlock.status == 'upcoming'
        ).order_by(ScheduleBlock.date.asc(), ScheduleBlock.start_time.asc()).first()
    
    # Unified Feed
    from app.models.broadcast import Broadcast
    broadcasts = Broadcast.query.filter(
        (Broadcast.target_level == user.level) | (Broadcast.target_level == 0)
    ).order_by(Broadcast.timestamp.desc()).limit(5).all()
    
    from app.models.system_alert import SystemAlert
    alerts = SystemAlert.query.filter_by(user_id=user_id).order_by(SystemAlert.created_at.desc()).limit(5).all()
    
    feed_items = []
    for b in broadcasts:
        item = b.to_dict()
        item['type'] = 'broadcast'
        feed_items.append(item)
        
    for a in alerts:
        item = a.to_dict()
        feed_items.append(item)
        
    feed_items.sort(key=lambda x: x['timestamp'], reverse=True)
    feed = feed_items[:5]
    
    # Featured Tip
    from app.services.study_tips_service import StudyTipsService
    featured_tip = StudyTipsService.get_featured_tip()
    
    # Daily Quote — rotates by day of year
    quotes = [
        {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
        {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
        {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
        {"text": "The expert in anything was once a beginner.", "author": "Helen Hayes"},
        {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
        {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
        {"text": "You don't have to be great to start, but you have to start to be great.", "author": "Zig Ziglar"},
        {"text": "The beautiful thing about learning is nobody can take it away from you.", "author": "B.B. King"},
        {"text": "An investment in knowledge pays the best interest.", "author": "Benjamin Franklin"},
        {"text": "Education is the most powerful weapon you can use to change the world.", "author": "Nelson Mandela"},
        {"text": "The more that you read, the more things you will know.", "author": "Dr. Seuss"},
        {"text": "Live as if you were to die tomorrow. Learn as if you were to live forever.", "author": "Mahatma Gandhi"},
        {"text": "The mind is not a vessel to be filled but a fire to be kindled.", "author": "Plutarch"},
        {"text": "Perseverance is not a long race; it is many short races one after the other.", "author": "Walter Elliot"},
        {"text": "Deep work is the ability to focus without distraction on a cognitively demanding task.", "author": "Cal Newport"},
    ]
    from datetime import date
    day_index = date.today().timetuple().tm_yday % len(quotes)
    daily_quote = quotes[day_index]
    
    return jsonify({
        "streak": user.streak_count,
        "badge": user.badge,
        "xp": user.xp_points,
        "next_session": {
            "id": next_session.id if next_session else None,
            "course": next_session.course.code if next_session and next_session.course else "None",
            "course_title": next_session.course.name if next_session and next_session.course else "No Upcoming Session",
            "time": next_session.start_time.strftime("%I:%M %p").lower() if next_session else "N/A",
            "technique": next_session.technique_name if next_session else "General Study",
            "technique_details": next_session.technique_details if next_session else "",
            "duration_minutes": int((datetime.combine(next_session.date, next_session.end_time) - datetime.combine(next_session.date, next_session.start_time)).total_seconds() / 60) if next_session else 0,
            "status": next_session.status if next_session else "none"
        },
        "quote": daily_quote,
        "feed": feed,
        "featured_tip": featured_tip
    }), 200


@dashboard_bp.route('/focus-pulse', methods=['GET'])
@jwt_required()
def get_focus_pulse():
    from datetime import timedelta
    
    user_id = int(get_jwt_identity())
    days = int(request.args.get('days', 7))
    since = datetime.utcnow() - timedelta(days=days)

    sessions = StudySession.query.filter(
        StudySession.user_id == user_id,
        StudySession.start_time >= since,
        StudySession.end_time != None
    ).order_by(StudySession.start_time.asc()).all()

    if not sessions:
        return jsonify([]), 200

    return jsonify([{
        'name': s.start_time.strftime('%a'),
        'focus': max(0, round(
            ((s.success_score or 0) / 5.0 * 100) - ((s.distraction_count or 0) * 10),
            1
        ))
    } for s in sessions]), 200
