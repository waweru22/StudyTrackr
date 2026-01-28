from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.session import ScheduleBlock

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/', methods=['GET'])
@schedule_bp.route('/', methods=['GET'])
@jwt_required()
def get_schedule():
    user_id = int(get_jwt_identity())
    
    # Return all blocks for simplicity (in prod, filter by date)
    blocks = ScheduleBlock.query.filter_by(user_id=user_id).all()
    
    schedule_data = []
    for block in blocks:
        schedule_data.append({
            "day": block.day_of_week,
            "date": block.date.strftime("%Y-%m-%d") if block.date else "N/A",
            "start": str(block.start_time),
            "end": str(block.end_time),
            "course": block.course.code if block.course else "Generic",
            "type": block.block_type,
            "refinement_reason": block.refinement_reason,
            "academic_citation": block.academic_citation
        })
        
    return jsonify(schedule_data), 200
