from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.course import Course

course_bp = Blueprint('course', __name__)

@course_bp.route('/filter', methods=['GET'])
def get_courses():
    level_filter = request.args.get('level')
    semester_filter = request.args.get('semester')
    
    query = Course.query
    
    if level_filter:
        try:
            level = int(level_filter)
            query = query.filter_by(level=level)
        except ValueError:
            return jsonify({'error': 'Invalid level parameter'}), 400

    if semester_filter:
        try:
            semester = int(semester_filter)
            query = query.filter_by(semester=semester)
        except ValueError:
            return jsonify({'error': 'Invalid semester parameter'}), 400
            
    # Allow fetching all if filters are missing, or strict? 
    # Current behavior is to filter if param exists.
            
    courses = query.order_by(Course.code.asc()).all()
    
    return jsonify([{
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'level': c.level,
        'semester': c.semester,
        'weight': c.weight,
        'credits': c.credits
    } for c in courses]), 200

@course_bp.route('/my_courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    from flask_jwt_extended import get_jwt_identity
    from app.models.user import User
    
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Return user's enrolled courses
    courses = user.courses
    
    return jsonify([{
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'level': c.level,
        'weight': c.weight,
        'credits': c.credits
    } for c in courses]), 200


@course_bp.route('/all', methods=['GET'])
def get_all_courses():
    # Global list ordered by level then code
    courses = Course.query.order_by(Course.level.asc(), Course.code.asc()).all()
    
    return jsonify([{
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'level': c.level,
        'weight': c.weight
    } for c in courses]), 200

from app.utils.decorators import admin_required
from app import db

@course_bp.route('/', methods=['POST'])
@admin_required()
def create_course():
    data = request.get_json()
    new_course = Course(
        code=data.get('code'),
        name=data.get('name'),
        level=data.get('level'),
        semester=data.get('semester', 1),
        credits=data.get('credits', 3),
        weight=data.get('weight', 1)
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "Course created", "id": new_course.id}), 201

@course_bp.route('/<int:course_id>', methods=['PUT'])
@admin_required()
def update_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
        
    data = request.get_json()
    course.code = data.get('code', course.code)
    course.name = data.get('name', course.name)
    course.level = data.get('level', course.level)
    course.semester = data.get('semester', course.semester)
    course.credits = data.get('credits', course.credits)
    course.weight = data.get('weight', course.weight)
    
    db.session.commit()
    return jsonify({"message": "Course updated"}), 200

@course_bp.route('/<int:course_id>', methods=['DELETE'])
@admin_required()
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
        
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Course deleted"}), 200
