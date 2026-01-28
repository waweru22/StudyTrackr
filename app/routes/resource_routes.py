from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.resource_service import ResourceService

resource_bp = Blueprint('resource', __name__)

@resource_bp.route('/search', methods=['GET'])
@jwt_required()
def search_resources():
    course_id = request.args.get('course_id')
    topic = request.args.get('topic')
    
    if not course_id:
        return jsonify({"error": "course_id is required"}), 400
        
    resources = ResourceService.search_resources(course_id, topic)
    
    return jsonify(resources), 200
