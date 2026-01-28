from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.session import StudySession, ScheduleBlock
from datetime import datetime
import random

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Real-time Trigger: Check for missed sessions
    from app.services.schedule_service import ScheduleService
    ScheduleService.check_missed_sessions(user_id)
    
    # Next session
    # Next session: Must be TODAY and >= current time
    today = datetime.utcnow().date()
    current_time = datetime.utcnow().time()
    
    next_session = ScheduleBlock.query.filter_by(user_id=user_id, date=today)\
        .filter(ScheduleBlock.start_time > current_time)\
        .order_by(ScheduleBlock.start_time.asc())\
        .first()
    
    # Unified Feed
    # 1. Fetch Broadcasts (Target level or 0)
    from app.models.broadcast import Broadcast
    broadcasts = Broadcast.query.filter(
        (Broadcast.target_level == user.level) | (Broadcast.target_level == 0)
    ).order_by(Broadcast.timestamp.desc()).limit(5).all()
    
    # 2. Fetch System Alerts
    from app.models.system_alert import SystemAlert
    alerts = SystemAlert.query.filter_by(user_id=user_id).order_by(SystemAlert.timestamp.desc()).limit(5).all()
    
    # 3. Merge and Sort
    feed_items = []
    for b in broadcasts:
        item = b.to_dict()
        item['type'] = 'broadcast' # Ensure distinction
        feed_items.append(item)
        
    for a in alerts:
        item = a.to_dict()
        feed_items.append(item) # Type handled in Model to_dict
        
    # Sort by timestamp desc (isoformat string works for comparison if YYYY-MM-DD...)
    # But safer to use actual datetime objects if we had them, OR rely on string sort since ISO8601 is sortable.
    # Broadcast/Alert models return ISO string in to_dict.
    feed_items.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Top 5
    feed = feed_items[:5]
    
    # Featured Tip
    from app.services.study_tips_service import StudyTipsService
    featured_tip = StudyTipsService.get_featured_tip()
    
    # Random Quote
    quotes = ["Code is poetry.", "Keep pushing.", "Bug is just a feature.", "Deep work wins."]
    
    return jsonify({
        "streak": user.streak_count,
        "badge": user.badge,
        "xp": user.xp_points,
        "next_session": {
            "course": next_session.course.code if next_session and next_session.course else "None",
            "time": str(next_session.start_time) if next_session else "N/A"
        },
        "quote": random.choice(quotes),
        "feed": feed,
        "featured_tip": featured_tip
    }), 200
