from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.course import StudyKnowledge
from app.models.user import User

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/', methods=['GET'])
@jwt_required()
def get_knowledge():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Filter by user learning style if possible, or just return all
    # For now, just return all 
    tips = StudyKnowledge.query.all()
    
    data = [{
        "principle": t.principle,
        "content": t.content,
        "source": t.academic_source
    } for t in tips]
    
    return jsonify(data), 200
