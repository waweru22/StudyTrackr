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
    
    # 2. Get Today's Schedule
    from datetime import datetime, date
    today = datetime.utcnow().date()
    
    # 3. Inference-First: If no schedule, generate it
    # Check if we have any blocks from today onwards
    future_check = ScheduleBlock.query.filter(ScheduleBlock.user_id == user_id, ScheduleBlock.date >= today).first()
    if not future_check:
        from app.services.inference_service import InferenceService
        InferenceService.generate_week_schedule(user_id)
        
    # Re-fetch Today's Blocks
    blocks = ScheduleBlock.query.filter_by(user_id=user_id, date=today).order_by(ScheduleBlock.start_time.asc()).all()
        
    # 4. Build Response with Status & Themes
    from app.models.session import StudySession
    
    # Get all sessions for today to map to blocks (Status Sync)
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
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
            "color_theme": get_theme(block.course.code if block.course else "General")
        })
        
    # 5. Get Weekly Summary (Next 6 days)
    tomorrow = today + timedelta(days=1)
    end_of_week = today + timedelta(days=6)
    
    future_blocks = ScheduleBlock.query.filter(
        ScheduleBlock.user_id == user_id,
        ScheduleBlock.date >= tomorrow,
        ScheduleBlock.date <= end_of_week
    ).order_by(ScheduleBlock.date.asc(), ScheduleBlock.start_time.asc()).all()
    
    weekly_summary = {}
    for block in future_blocks:
        day_name = block.date.strftime("%A")
        if day_name not in weekly_summary:
            weekly_summary[day_name] = []
            
        weekly_summary[day_name].append({
            "id": block.id,
            "course_code": block.course.code if block.course else "General",
            "start_time": block.start_time.strftime("%H:%M"),
            "technique_name": block.technique_name,
            "color_theme": get_theme(block.course.code if block.course else "General") # Visual Consistency
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
