from flask import Blueprint, request, jsonify
from app.utils.decorators import admin_required
from app.services.admin_service import AdminService
from flask_jwt_extended import get_jwt_identity
from app.models.user import User

admin_bp = Blueprint('admin', __name__)


# ─── Dashboard ───────────────────────────────────────────────────────

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required()
def get_dashboard():
    weeks = request.args.get('weeks', 1, type=int)
    data = AdminService.get_dashboard_metrics(weeks)
    return jsonify(data), 200


# ─── Course CRUD ─────────────────────────────────────────────────────

@admin_bp.route('/courses', methods=['GET'])
@admin_required()
def list_courses():
    data = AdminService.list_courses()
    return jsonify(data), 200


@admin_bp.route('/courses', methods=['POST'])
@admin_required()
def create_course():
    data = request.get_json()
    if not data.get('code') or not data.get('name'):
        return jsonify({"error": "Code and name are required"}), 400

    course, message = AdminService.create_course(data)
    if not course:
        return jsonify({"error": message}), 400

    return jsonify({
        "message": message,
        "course": {
            "id": course.id, "code": course.code,
            "name": course.name, "credits": course.credits,
            "weight": course.weight, "level": course.level
        }
    }), 201


@admin_bp.route('/courses/<int:course_id>', methods=['PATCH'])
@admin_required()
def update_course(course_id):
    data = request.get_json()
    course, message = AdminService.update_course(course_id, data)
    if not course:
        return jsonify({"error": message}), 404 if "not found" in message.lower() else 400

    return jsonify({"message": message}), 200


@admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@admin_required()
def delete_course(course_id):
    course, message = AdminService.delete_course(course_id)
    if not course:
        return jsonify({"error": message}), 404

    return jsonify({"message": message}), 200


# ─── Student Verification ────────────────────────────────────────────

@admin_bp.route('/verification', methods=['GET'])
@admin_required()
def list_unverified():
    data = AdminService.get_unverified_students()
    return jsonify(data), 200


@admin_bp.route('/verification/<int:student_id>/approve', methods=['POST'])
@admin_required()
def approve_student(student_id):
    student, message = AdminService.approve_student(student_id)
    if not student:
        return jsonify({"error": message}), 404

    return jsonify({"message": message}), 200


@admin_bp.route('/verification/<int:student_id>/reject', methods=['POST'])
@admin_required()
def reject_student(student_id):
    result, message = AdminService.reject_student(student_id)
    if not result:
        return jsonify({"error": message}), 404

    return jsonify({"message": message}), 200


# ─── Analytics ───────────────────────────────────────────────────────

@admin_bp.route('/analytics/courses', methods=['GET'])
@admin_required()
def get_course_analytics():
    level = request.args.get('level', type=int)
    weeks = request.args.get('weeks', type=int)
    data = AdminService.get_course_analytics(level=level, weeks=weeks)
    return jsonify(data), 200


@admin_bp.route('/analytics/techniques', methods=['GET'])
@admin_required()
def get_technique_analytics():
    data = AdminService.get_technique_effectiveness()
    return jsonify(data), 200


# Legacy focus analytics endpoint (backward compat)
@admin_bp.route('/analytics/focus', methods=['GET'])
@admin_required()
def get_focus_analytics():
    data = AdminService.get_low_focus_areas()
    return jsonify(data), 200


# ─── Broadcast ───────────────────────────────────────────────────────

@admin_bp.route('/broadcast', methods=['POST'])
@admin_required()
def create_broadcast():
    data = request.get_json()
    admin_id = int(get_jwt_identity())
    admin = User.query.get(admin_id)

    title = data.get('title')
    message = data.get('message')
    target_level = data.get('target_level')  # null = all students

    if not title or not message:
        return jsonify({"error": "Title and message are required"}), 400

    broadcast, count = AdminService.send_broadcast(
        admin_id=admin_id,
        admin_email=admin.email,
        title=title,
        message=message,
        target_level=target_level
    )

    return jsonify({
        "message": f"Broadcast sent to {count} students",
        "broadcast_id": broadcast.id,
        "notifications_created": count
    }), 201


@admin_bp.route('/broadcasts', methods=['GET'])
@admin_required()
def list_broadcasts():
    data = AdminService.get_broadcast_history()
    return jsonify(data), 200
