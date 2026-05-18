from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.session import ScheduleBlock
from app import limiter, db
from datetime import datetime, timedelta

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('', methods=['GET'])
@jwt_required()
def get_schedule():
    user_id = int(get_jwt_identity())
    
    # Verification gate: unverified students cannot access schedule
    from app.models.user import User
    user = User.query.get(user_id)
    if user and user.role == 'student' and not user.is_verified:
        return jsonify({
            "error": "Please verify your email to access your schedule.",
            "email_unverified": True
        }), 403
    # 1. Check for missed sessions (triggers penalties)
    from app.services.schedule_service import ScheduleService
    # ScheduleService.check_missed_sessions(user_id) # Simplify for now
    
    # 2. Get Today's Schedule (Lagos Time)
    from datetime import datetime, date, timezone, timedelta
    LAGOS_TZ = timezone(timedelta(hours=1))
    today = datetime.now(LAGOS_TZ).date()
    
    # 3. Inference-First: Regenerate if no future blocks or schedule is from a previous week
    # Auto-generate only for brand new users (zero blocks ever).
    # Returning users get their next schedule via the Adapt Schedule button,
    # which uses AdaptationEngine. This prevents silent regeneration from
    # bypassing adaptation logic.
    has_any_blocks = ScheduleBlock.query.filter_by(user_id=user_id).count() > 0

    if not has_any_blocks:
        from app.services.inference_service import InferenceService
        InferenceService.generate_week_schedule(user_id)
        
    # Support viewing a different week (e.g. after adaptation)
    week_offset = int(request.args.get('week_offset', 0))
    view_date = today + timedelta(weeks=week_offset)

    # Re-fetch blocks for the view date
    blocks = ScheduleBlock.query.filter_by(user_id=user_id, date=view_date).order_by(ScheduleBlock.start_time.asc()).all()
        
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
        # Trust the block's own status field.
        # It is managed by the /start and /complete endpoints.
        status = block.status or "upcoming"
             
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
    
    start_of_week = view_date - timedelta(days=view_date.weekday()) # Monday
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
        "weekly_summary": weekly_summary,
        "viewing_week_offset": week_offset,
        "week_start": start_of_week.isoformat(),
        "week_end": end_of_week.isoformat(),
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
    
    return jsonify({
        "message": "Session started",
        "status": "active",
        "course_id": block.course_id
    }), 200

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
@limiter.limit("20 per hour")
def regenerate_schedule():
    """
    End-of-week regeneration endpoint.
    Analyses past week's sessions and adapts next week's schedule.
    Falls back to standard generation when no session data exists.
    """
    user_id = int(get_jwt_identity())

    try:
        from app.services.inference_service_adaptation import AdaptationEngine
        result = AdaptationEngine.adapt_schedule_for_next_week(user_id)

        if 'error' in result:
            return jsonify({"error": result['error']}), 500

        return jsonify({
            "message": result.get('message', 'Schedule regenerated'),
            "adaptations_made": {
                "technique_swaps": result.get('technique_swaps', 0),
                "time_shifts": result.get('time_shifts', 0),
                "total_courses": result.get('total_courses_analyzed', 0),
            },
            "details": result.get('adaptations', {}),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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


# ─── Block serializer ────────────────────────────────────────────────

def _serialize_block(block):
    """Shared serializer for ScheduleBlock -> dict."""
    duration = int(
        (datetime.combine(block.date, block.end_time) -
         datetime.combine(block.date, block.start_time)).total_seconds() / 60
    ) if block.date else 0

    return {
        "id":                       block.id,
        "course_code":              block.course.code if block.course else "General",
        "course_name":              block.course.name if block.course else "Personal Development",
        "technique_name":           block.technique_name,
        "technique_details":        block.technique_details,
        "block_type":               block.block_type,
        "suggested_environment":    block.suggested_environment,
        "suggested_social_setting": block.suggested_social_setting,
        "suggested_medium":         block.suggested_medium,
        "start_time":               block.start_time.strftime("%H:%M") if block.start_time else None,
        "end_time":                 block.end_time.strftime("%H:%M") if block.end_time else None,
        "duration_minutes":         duration,
        "status":                   block.status,
    }


# ─── Adapt-Now endpoint (demo button) ───────────────────────────────

@schedule_bp.route('/adapt-now', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def adapt_schedule_now():
    """
    Used by the demo Adapt Schedule button.
    Returns before/after comparison + reasoning in one response.
    """
    import json as _json
    from app.services.inference_service_adaptation import AdaptationEngine
    from app.models.adaptation_log import AdaptationLog

    user_id = int(get_jwt_identity())

    # 1. Snapshot Week 1 blocks before adaptation
    week1_blocks = ScheduleBlock.query.filter_by(user_id=user_id, status='upcoming').all()
    week1_data   = [_serialize_block(b) for b in week1_blocks]

    # 2. Performance analysis (for frontend display)
    analysis = AdaptationEngine.analyze_weekly_performance(user_id)

    # 3. Run adaptation -- deletes upcoming blocks, generates new ones, saves AdaptationLog
    result = AdaptationEngine.adapt_schedule_for_next_week(user_id)

    # 4. Fetch newly generated blocks
    week2_blocks = ScheduleBlock.query.filter_by(user_id=user_id, status='upcoming').all()
    week2_data   = [_serialize_block(b) for b in week2_blocks]

    # 5. Fetch the AdaptationLog just created
    latest_log = AdaptationLog.query.filter_by(user_id=user_id)\
                     .order_by(AdaptationLog.created_at.desc()).first()
    reasoning = _json.loads(latest_log.reasoning) if latest_log else {}

    return jsonify({
        "week1":                week1_data,
        "week1_analysis":       analysis,
        "week2":                week2_data,
        "adaptation_reasoning": reasoning,
        "summary":              result,
    }), 200


# ─── Adaptation-Log endpoint (profile page) ─────────────────────────

@schedule_bp.route('/adaptation-log', methods=['GET'])
@jwt_required()
def get_adaptation_log():
    """Returns the last 5 adaptation logs for the current user."""
    import json as _json
    from app.models.adaptation_log import AdaptationLog

    user_id = int(get_jwt_identity())

    logs = AdaptationLog.query\
        .filter_by(user_id=user_id)\
        .order_by(AdaptationLog.created_at.desc())\
        .limit(5)\
        .all()

    return jsonify({
        "logs": [
            {
                "id":         log.id,
                "created_at": log.created_at.isoformat(),
                "week_label": log.week_label,
                "summary":    log.summary,
                "reasoning":  _json.loads(log.reasoning) if log.reasoning else {},
            }
            for log in logs
        ]
    }), 200
