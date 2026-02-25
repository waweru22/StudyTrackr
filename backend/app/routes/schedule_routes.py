from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.session import ScheduleBlock
from datetime import datetime, timedelta

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('', methods=['GET'])
@jwt_required()
def get_schedule():
    user_id = int(get_jwt_identity())
    
    # 1. Check for missed sessions (triggers penalties)
    from app.services.schedule_service import ScheduleService
    # ScheduleService.check_missed_sessions(user_id) # Simplify for now
    
    # 2. Get Today's Schedule (Lagos Time)
    from datetime import datetime, date, timezone, timedelta
    LAGOS_TZ = timezone(timedelta(hours=1))
    today = datetime.now(LAGOS_TZ).date()
    
    # 3. Inference-First: Regenerate if no future blocks or schedule is from a previous week
    last_block = ScheduleBlock.query.filter(
        ScheduleBlock.user_id == user_id,
        ScheduleBlock.date >= today
    ).order_by(ScheduleBlock.date.desc()).first()

    start_of_week = today - timedelta(days=today.weekday())
    needs_regen = not last_block or last_block.date < start_of_week

    if needs_regen:
        from app.services.inference_service import InferenceService
        InferenceService.generate_week_schedule(user_id)
        
    # Re-fetch Today's Blocks
    blocks = ScheduleBlock.query.filter_by(user_id=user_id, date=today).order_by(ScheduleBlock.start_time.asc()).all()
        
    # 4. Build Response with Status & Themes
    from app.models.session import StudySession
    
    # Get all sessions for today to map to blocks (Status Sync)
    # Get all sessions for today to map to blocks (Status Sync)
    start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=LAGOS_TZ)
    end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=LAGOS_TZ)
    todays_sessions = StudySession.query.filter(
        StudySession.user_id == user_id,
        StudySession.start_time >= start_of_day,
        StudySession.start_time <= end_of_day
    ).all()
    
    # Theme Helper
    def get_theme(course_code):
        if not course_code: return 'blue'
        colors = ['pink', 'blue', 'green', 'purple', 'orange']
        idx = sum(ord(c) for c in course_code) % len(colors)
        return colors[idx]
    
    today_blocks_data = []
    for block in blocks:
        # Status from DB
        status = block.status or "upcoming" 
        
        # Check if completed via Session as well
        matching_session = next((s for s in todays_sessions if s.course_id == block.course_id), None)
        if matching_session:
             status = "completed"
             
        today_blocks_data.append({
            "id": block.id,
            "course_code": block.course.code if block.course else "General",
            "course_title": block.course.name if block.course else "Personal Development",
            "start_time": block.start_time.strftime("%I:%M%p").lower(),
            "end_time": block.end_time.strftime("%I:%M%p").lower(),
            "block_type": block.block_type,
            "status": status,
            "technique_name": block.technique_name,
            "technique_details": block.technique_details,
            "refinement_reason": block.refinement_reason,
            "color_theme": get_theme(block.course.code if block.course else "General"),
            "duration_minutes": int((datetime.combine(block.date, block.end_time) - datetime.combine(block.date, block.start_time)).total_seconds() / 60),
            "suggested_environment": block.suggested_environment,
            "suggested_social_setting": block.suggested_social_setting,
            "suggested_medium": block.suggested_medium
        })
        
    # 5. Get Weekly Summary (Current Week - including Today)
    # We want to show the full week (or at least from today onwards correctly)
    # Actually, for a "Weekly View" effectively acting as a calendar, users often want to see Mon-Sun.
    # But usually "Upcoming" implies future. However, based on the issue "today... does not match", 
    # it implies the user sees the Weekly Grid and expects Today's column to be filled.
    
    # Let's fetch from start of current week (Monday) to end of week (Sunday)
    # OR just fetch from Today onwards and ensure Today is included.
    # Since the frontend renders a fixed Mon-Sun grid, we should probably return the whole week's data if possible,
    # or at least ensuring 'today' is in there.
    
    # Let's align with the user request: "today... does not match...". 
    # If we only send tomorrow+, today is empty in the grid.
    
    start_of_week = today - timedelta(days=today.weekday()) # Monday
    end_of_week = start_of_week + timedelta(days=6) # Sunday
    
    week_blocks = ScheduleBlock.query.filter(
        ScheduleBlock.user_id == user_id,
        ScheduleBlock.date >= start_of_week,
        ScheduleBlock.date <= end_of_week
    ).order_by(ScheduleBlock.date.asc(), ScheduleBlock.start_time.asc()).all()
    
    weekly_summary = {}
    for block in week_blocks:
        day_name = block.date.strftime("%A")
        if day_name not in weekly_summary:
            weekly_summary[day_name] = []
            
        weekly_summary[day_name].append({
            "id": block.id,
            "course_code": block.course.code if block.course else "General",
            "start_time": block.start_time.strftime("%H:%M"),
            "end_time": block.end_time.strftime("%H:%M"), # Added end_time
            "technique_name": block.technique_name,
            "block_type": block.block_type,
            "color_theme": get_theme(block.course.code if block.course else "General"),
            "duration_minutes": int((datetime.combine(block.date, block.end_time) - datetime.combine(block.date, block.start_time)).total_seconds() / 60)
        })
        
    return jsonify({
        "today_blocks": today_blocks_data,
        "weekly_summary": weekly_summary
    }), 200

@schedule_bp.route('/<int:block_id>/start', methods=['POST'])
@jwt_required()
def start_session(block_id):
    user_id = int(get_jwt_identity())
    block = ScheduleBlock.query.filter_by(id=block_id, user_id=user_id).first()
    
    if not block:
        return jsonify({"error": "Block not found"}), 404
        
    block.status = "active"
    db.session.commit()
    
    return jsonify({"message": "Session started", "status": "active"}), 200

@schedule_bp.route('/<int:block_id>/complete', methods=['POST'])
@jwt_required()
def complete_session(block_id):
    user_id = get_jwt_identity()
    block = ScheduleBlock.query.filter_by(id=block_id, user_id=user_id).first()
    
    if not block:
        return jsonify({"error": "Block not found"}), 404
        
    block.status = "completed"
    db.session.commit()
    
    return jsonify({"message": "Session completed", "status": "completed"}), 200

@schedule_bp.route('/complete/<int:block_id>', methods=['POST'])
@jwt_required()
def complete_block(block_id):
    user_id = int(get_jwt_identity())
    block = ScheduleBlock.query.get(block_id)
    
    if not block:
        return jsonify({"message": "Block not found"}), 404
        
    if block.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403
        
    block.status = 'completed'
    from app import db
    db.session.commit()
    
    return jsonify({"message": "Block marked as completed", "status": "completed"}), 200

@schedule_bp.route('/regenerate', methods=['POST'])
@jwt_required()
def regenerate_schedule():
    user_id = int(get_jwt_identity())
    from app.services.inference_service import InferenceService
    result = InferenceService.generate_week_schedule(user_id)
    return jsonify({"message": result}), 200

@schedule_bp.route('/debug/all', methods=['GET'])
def debug_all_schedules():
    """
    Debug Endpoint: Retrieve all schedule blocks to verify persistence.
    Public access (Dev use only).
    """
    blocks = ScheduleBlock.query.order_by(ScheduleBlock.date.asc(), ScheduleBlock.start_time.asc()).all()
    
    results = []
    for b in blocks:
        results.append({
            "id": b.id,
            "user_id": b.user_id,
            "course_id": b.course_id,
            "date": b.date.isoformat() if b.date else None,
            "start_time": b.start_time.strftime("%H:%M:%S"),
            "end_time": b.end_time.strftime("%H:%M:%S"),
            "block_type": b.block_type,
            "technique_name": b.technique_name,
            "status": b.status
        })
        
    return jsonify(results), 200

@schedule_bp.route('/weekly-summary', methods=['GET'])
@jwt_required()
def get_weekly_summary():
    user_id = int(get_jwt_identity())
    from datetime import date
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    total_blocks = ScheduleBlock.query.filter(
        ScheduleBlock.user_id == user_id,
        ScheduleBlock.date >= start_of_week,
        ScheduleBlock.date <= end_of_week
    ).count()

    completed_blocks = ScheduleBlock.query.filter(
        ScheduleBlock.user_id == user_id,
        ScheduleBlock.date >= start_of_week,
        ScheduleBlock.date <= end_of_week,
        ScheduleBlock.status == 'completed'
    ).count()

    missed_blocks = ScheduleBlock.query.filter(
        ScheduleBlock.user_id == user_id,
        ScheduleBlock.date >= start_of_week,
        ScheduleBlock.date < today,
        ScheduleBlock.status == 'upcoming'
    ).count()

    return jsonify({
        'total': total_blocks,
        'completed': completed_blocks,
        'missed': missed_blocks,
        'remaining': total_blocks - completed_blocks - missed_blocks
    }), 200
